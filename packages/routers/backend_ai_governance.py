from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.ai_governance import (
    CreateAIGovernanceWorkspaceRequest,
    UpdateAIGovernanceStatusRequest,
    UpsertAIGovernanceSnapshotRequest,
)
from packages.domain.ai_governance import (
    AIGovernanceSnapshot,
    AIGovernanceStatus,
    AIGovernanceWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.ai_governance import (
    AIGovernanceSnapshotRepository,
    AIGovernanceWorkspaceRepository,
)
from packages.services.ai_governance import (
    build_ai_governance_summary,
    review_ai_governance_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/ai-governance', tags=['ai_governance'])
telemetry = TelemetryLogger(filepath='var/ai_governance_telemetry.jsonl')


@router.post('/workspaces')
def create_ai_governance_workspace(payload: CreateAIGovernanceWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = AIGovernanceWorkspaceRepository(db)
    workspace = AIGovernanceWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        model_scope=payload.model_scope,
        evaluation_goals=payload.evaluation_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ai_governance',
        source_id=saved.id,
        summary=f'Created AI governance workspace {saved.name}',
        metadata={'owner': saved.owner, 'model_scope': saved.model_scope},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_ai_governance_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_ai_governance_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in AIGovernanceWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_ai_governance_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_ai_governance_status(workspace_id: str, payload: UpdateAIGovernanceStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = AIGovernanceStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = AIGovernanceWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ai_governance',
        source_id=workspace_id,
        summary=f'Updated AI governance workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_ai_governance_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_ai_governance_snapshot(workspace_id: str, payload: UpsertAIGovernanceSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = AIGovernanceWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = AIGovernanceSnapshotRepository(db)
    snapshot = AIGovernanceSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ai_governance',
        source_id=workspace_id,
        summary=f'Updated AI governance snapshot for {workspace.name}',
        metadata={'governance_score': saved.governance_score, 'policy_checks': saved.policy_checks},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_ai_governance_snapshot', workspace_id=workspace_id, governance_score=saved.governance_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_ai_governance_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = AIGovernanceWorkspaceRepository(db)
    snapshot_repo = AIGovernanceSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_ai_governance_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_ai_governance_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_ai_governance_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = AIGovernanceWorkspaceRepository(db).list()
    snapshot_repo = AIGovernanceSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_ai_governance_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_ai_governance_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
