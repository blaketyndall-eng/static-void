from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.agent_studio import (
    CreateAgentStudioWorkspaceRequest,
    UpdateAgentStudioStatusRequest,
    UpsertAgentStudioSnapshotRequest,
)
from packages.domain.agent_studio import (
    AgentStudioSnapshot,
    AgentStudioStatus,
    AgentStudioWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.orchestration_studio import (
    AgentStudioSnapshotRepository,
    AgentStudioWorkspaceRepository,
)
from packages.services.studio_ops import (
    build_studio_summary,
    review_studio_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/agent-studio', tags=['agent_studio'])
telemetry = TelemetryLogger(filepath='var/agent_studio_telemetry.jsonl')


@router.post('/workspaces')
def create_agent_studio_workspace(payload: CreateAgentStudioWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = AgentStudioWorkspaceRepository(db)
    workspace = AgentStudioWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        agent_roles=payload.agent_roles,
        routing_goals=payload.routing_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='agent_studio',
        source_id=saved.id,
        summary=f'Created agent studio workspace {saved.name}',
        metadata={'owner': saved.owner, 'agent_roles': saved.agent_roles},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_agent_studio_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_agent_studio_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in AgentStudioWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_agent_studio_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_agent_studio_status(workspace_id: str, payload: UpdateAgentStudioStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = AgentStudioStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = AgentStudioWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='agent_studio',
        source_id=workspace_id,
        summary=f'Updated agent studio workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_agent_studio_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_agent_studio_snapshot(workspace_id: str, payload: UpsertAgentStudioSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = AgentStudioWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = AgentStudioSnapshotRepository(db)
    snapshot = AgentStudioSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='agent_studio',
        source_id=workspace_id,
        summary=f'Updated agent studio snapshot for {workspace.name}',
        metadata={
            'routing_quality_score': saved.routing_quality_score,
            'operator_confidence_score': saved.operator_confidence_score,
            'routing_policies': saved.routing_policies,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_agent_studio_snapshot', workspace_id=workspace_id, routing_quality_score=saved.routing_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_agent_studio_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = AgentStudioWorkspaceRepository(db)
    snapshot_repo = AgentStudioSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_studio_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_agent_studio_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_agent_studio_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = AgentStudioWorkspaceRepository(db).list()
    snapshot_repo = AgentStudioSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_studio_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_agent_studio_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
