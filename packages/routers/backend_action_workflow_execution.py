from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.action_workflow_execution import (
    CreateActionWorkflowExecutionWorkspaceRequest,
    UpdateActionWorkflowExecutionStatusRequest,
    UpsertActionWorkflowExecutionSnapshotRequest,
)
from packages.domain.action_workflow_execution import (
    ActionWorkflowExecutionSnapshot,
    ActionWorkflowExecutionStatus,
    ActionWorkflowExecutionWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.action_workflow_execution import (
    ActionWorkflowExecutionSnapshotRepository,
    ActionWorkflowExecutionWorkspaceRepository,
)
from packages.services.action_workflow_execution import (
    build_action_workflow_execution_summary,
    review_action_workflow_execution_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/action-workflow-execution', tags=['action_workflow_execution'])
telemetry = TelemetryLogger(filepath='var/action_workflow_execution_telemetry.jsonl')


@router.post('/workspaces')
def create_action_workspace(payload: CreateActionWorkflowExecutionWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = ActionWorkflowExecutionWorkspaceRepository(db)
    workspace = ActionWorkflowExecutionWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        execution_domains=payload.execution_domains,
        workflow_goals=payload.workflow_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='action_workflow_execution',
        source_id=saved.id,
        summary=f'Created action workspace {saved.name}',
        metadata={'owner': saved.owner, 'execution_domains': saved.execution_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_action_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_action_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in ActionWorkflowExecutionWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_action_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_action_status(workspace_id: str, payload: UpdateActionWorkflowExecutionStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ActionWorkflowExecutionStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = ActionWorkflowExecutionWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='action_workflow_execution',
        source_id=workspace_id,
        summary=f'Updated action workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_action_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_action_snapshot(workspace_id: str, payload: UpsertActionWorkflowExecutionSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ActionWorkflowExecutionWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ActionWorkflowExecutionSnapshotRepository(db)
    snapshot = ActionWorkflowExecutionSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='action_workflow_execution',
        source_id=workspace_id,
        summary=f'Updated action snapshot for {workspace.name}',
        metadata={
            'execution_reliability_score': saved.execution_reliability_score,
            'approval_readiness_score': saved.approval_readiness_score,
            'workflow_templates': saved.workflow_templates,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_action_snapshot', workspace_id=workspace_id, execution_reliability_score=saved.execution_reliability_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_action_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = ActionWorkflowExecutionWorkspaceRepository(db)
    snapshot_repo = ActionWorkflowExecutionSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_action_workflow_execution_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_action_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_action_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = ActionWorkflowExecutionWorkspaceRepository(db).list()
    snapshot_repo = ActionWorkflowExecutionSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_action_workflow_execution_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_action_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
