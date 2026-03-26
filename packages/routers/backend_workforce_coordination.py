from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.workforce_coordination import (
    CreateWorkforceCoordinationWorkspaceRequest,
    UpdateWorkforceCoordinationStatusRequest,
    UpsertWorkforceCoordinationSnapshotRequest,
)
from packages.domain.workforce_coordination import (
    WorkforceCoordinationSnapshot,
    WorkforceCoordinationStatus,
    WorkforceCoordinationWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.workforce_coordination import (
    WorkforceCoordinationSnapshotRepository,
    WorkforceCoordinationWorkspaceRepository,
)
from packages.services.workforce_coordination import (
    build_workforce_coordination_summary,
    review_workforce_coordination_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/workforce-coordination', tags=['workforce_coordination'])
telemetry = TelemetryLogger(filepath='var/workforce_coordination_telemetry.jsonl')


@router.post('/workspaces')
def create_workforce_coordination_workspace(payload: CreateWorkforceCoordinationWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = WorkforceCoordinationWorkspaceRepository(db)
    workspace = WorkforceCoordinationWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        role_groups=payload.role_groups,
        coordination_goals=payload.coordination_goals,
        linked_apps=payload.linked_apps,
        linked_modules=payload.linked_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='workforce_coordination',
        source_id=saved.id,
        summary=f'Created workforce coordination workspace {saved.name}',
        metadata={'owner': saved.owner, 'role_groups': saved.role_groups},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_workforce_coordination_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_workforce_coordination_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in WorkforceCoordinationWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_workforce_coordination_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_workforce_coordination_status(workspace_id: str, payload: UpdateWorkforceCoordinationStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = WorkforceCoordinationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = WorkforceCoordinationWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='workforce_coordination',
        source_id=workspace_id,
        summary=f'Updated workforce coordination workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_workforce_coordination_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_workforce_coordination_snapshot(workspace_id: str, payload: UpsertWorkforceCoordinationSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = WorkforceCoordinationWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = WorkforceCoordinationSnapshotRepository(db)
    snapshot = WorkforceCoordinationSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='workforce_coordination',
        source_id=workspace_id,
        summary=f'Updated workforce coordination snapshot for {workspace.name}',
        metadata={
            'reliability_score': saved.reliability_score,
            'readiness_score': saved.readiness_score,
            'work_queues': saved.work_queues,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_workforce_coordination_snapshot', workspace_id=workspace_id, reliability_score=saved.reliability_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_workforce_coordination_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = WorkforceCoordinationWorkspaceRepository(db)
    snapshot_repo = WorkforceCoordinationSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_workforce_coordination_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_workforce_coordination_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_workforce_coordination_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = WorkforceCoordinationWorkspaceRepository(db).list()
    snapshot_repo = WorkforceCoordinationSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_workforce_coordination_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_workforce_coordination_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
