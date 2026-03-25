from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.reasoning_decision_engine import (
    CreateReasoningDecisionEngineWorkspaceRequest,
    UpdateReasoningDecisionEngineStatusRequest,
    UpsertReasoningDecisionEngineSnapshotRequest,
)
from packages.domain.reasoning_decision_engine import (
    ReasoningDecisionEngineSnapshot,
    ReasoningDecisionEngineStatus,
    ReasoningDecisionEngineWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.reasoning_decision_engine import (
    ReasoningDecisionEngineSnapshotRepository,
    ReasoningDecisionEngineWorkspaceRepository,
)
from packages.services.reasoning_decision_engine import (
    build_reasoning_decision_engine_summary,
    review_reasoning_decision_engine_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/reasoning-decision-engine', tags=['reasoning_decision_engine'])
telemetry = TelemetryLogger(filepath='var/reasoning_decision_engine_telemetry.jsonl')


@router.post('/workspaces')
def create_reasoning_workspace(payload: CreateReasoningDecisionEngineWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = ReasoningDecisionEngineWorkspaceRepository(db)
    workspace = ReasoningDecisionEngineWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        decision_domains=payload.decision_domains,
        reasoning_goals=payload.reasoning_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='reasoning_decision_engine',
        source_id=saved.id,
        summary=f'Created reasoning workspace {saved.name}',
        metadata={'owner': saved.owner, 'decision_domains': saved.decision_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_reasoning_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_reasoning_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in ReasoningDecisionEngineWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_reasoning_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_reasoning_status(workspace_id: str, payload: UpdateReasoningDecisionEngineStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ReasoningDecisionEngineStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = ReasoningDecisionEngineWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='reasoning_decision_engine',
        source_id=workspace_id,
        summary=f'Updated reasoning workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_reasoning_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_reasoning_snapshot(workspace_id: str, payload: UpsertReasoningDecisionEngineSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ReasoningDecisionEngineWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ReasoningDecisionEngineSnapshotRepository(db)
    snapshot = ReasoningDecisionEngineSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='reasoning_decision_engine',
        source_id=workspace_id,
        summary=f'Updated reasoning snapshot for {workspace.name}',
        metadata={
            'reasoning_quality_score': saved.reasoning_quality_score,
            'recommendation_confidence_score': saved.recommendation_confidence_score,
            'reasoning_policies': saved.reasoning_policies,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_reasoning_snapshot', workspace_id=workspace_id, reasoning_quality_score=saved.reasoning_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_reasoning_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = ReasoningDecisionEngineWorkspaceRepository(db)
    snapshot_repo = ReasoningDecisionEngineSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_reasoning_decision_engine_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_reasoning_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_reasoning_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = ReasoningDecisionEngineWorkspaceRepository(db).list()
    snapshot_repo = ReasoningDecisionEngineSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_reasoning_decision_engine_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_reasoning_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
