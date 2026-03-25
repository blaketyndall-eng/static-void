from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.decision_memory import CreateDecisionMemoryWorkspaceRequest, UpdateDecisionMemoryStatusRequest, UpsertDecisionMemorySnapshotRequest
from packages.domain.decision_memory import DecisionMemorySnapshot, DecisionMemoryStatus, DecisionMemoryWorkspace
from packages.domain.system_events import SystemEventType
from packages.repositories.decision_memory_store import DecisionMemorySnapshotRepository, DecisionMemoryWorkspaceRepository
from packages.services.decision_memory_ops import build_decision_memory_summary, review_decision_memory_workspace
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/decision-memory', tags=['memory_reviews'])
telemetry = TelemetryLogger(filepath='var/decision_memory_telemetry.jsonl')

@router.post('/workspaces')
def create_memory_workspace(payload: CreateDecisionMemoryWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = DecisionMemoryWorkspaceRepository(db)
    workspace = DecisionMemoryWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        memory_domains=payload.memory_domains,
        review_goals=payload.review_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='decision_memory', source_id=saved.id, summary=f'Created decision memory workspace {saved.name}', metadata={'owner': saved.owner, 'memory_domains': saved.memory_domains})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_memory_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')

@router.get('/workspaces')
def list_memory_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in DecisionMemoryWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_memory_workspaces', returned_count=len(payload))
    return payload

@router.post('/workspaces/{workspace_id}/status')
def update_memory_status(workspace_id: str, payload: UpdateDecisionMemoryStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = DecisionMemoryStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = DecisionMemoryWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='decision_memory', source_id=workspace_id, summary=f'Updated decision memory workspace {saved.name} to {saved.status.value}', metadata={'status': saved.status.value})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_memory_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')

@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_memory_snapshot(workspace_id: str, payload: UpsertDecisionMemorySnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = DecisionMemoryWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = DecisionMemorySnapshotRepository(db)
    snapshot = DecisionMemorySnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='decision_memory', source_id=workspace_id, summary=f'Updated decision memory snapshot for {workspace.name}', metadata={'memory_quality_score': saved.memory_quality_score, 'calibration_score': saved.calibration_score, 'captured_decisions': saved.captured_decisions})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_memory_snapshot', workspace_id=workspace_id, memory_quality_score=saved.memory_quality_score)
    return saved.model_dump(mode='json')

@router.get('/workspaces/{workspace_id}/review')
def get_memory_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace = DecisionMemoryWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_decision_memory_workspace(workspace, DecisionMemorySnapshotRepository(db).get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_memory_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')

@router.get('/summary')
def get_memory_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = DecisionMemoryWorkspaceRepository(db).list()
    snapshot_repo = DecisionMemorySnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_decision_memory_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_memory_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
