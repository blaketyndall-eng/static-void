from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.console_expansion import (
    CreateConsoleArmWorkspaceRequest,
    UpdateConsoleArmStatusRequest,
    UpsertConsoleArmSnapshotRequest,
)
from packages.domain.console_expansion import (
    ConsoleArmSnapshot,
    ConsoleArmStatus,
    ConsoleArmType,
    ConsoleArmWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.console_expansion import (
    ConsoleArmSnapshotRepository,
    ConsoleArmWorkspaceRepository,
)
from packages.services.console_expansion import (
    build_console_expansion_summary,
    review_console_arm,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/console-expansion', tags=['console_expansion'])
telemetry = TelemetryLogger(filepath='var/console_expansion_telemetry.jsonl')


@router.post('/workspaces')
def create_console_arm_workspace(payload: CreateConsoleArmWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    try:
        arm_type = ConsoleArmType(payload.arm_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid arm_type') from exc
    repo = ConsoleArmWorkspaceRepository(db)
    workspace = ConsoleArmWorkspace(
        arm_type=arm_type,
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        goals=payload.goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='console_expansion',
        source_id=saved.id,
        summary=f'Created console expansion workspace {saved.name}',
        metadata={'arm_type': saved.arm_type.value, 'owner': saved.owner},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_console_arm_workspace', workspace_id=saved.id, arm_type=saved.arm_type.value)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_console_arm_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in ConsoleArmWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_console_arm_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_console_arm_workspace_status(workspace_id: str, payload: UpdateConsoleArmStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ConsoleArmStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = ConsoleArmWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='console_expansion',
        source_id=workspace_id,
        summary=f'Updated console arm workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_console_arm_workspace_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_console_arm_snapshot(workspace_id: str, payload: UpsertConsoleArmSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ConsoleArmWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ConsoleArmSnapshotRepository(db)
    snapshot = ConsoleArmSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='console_expansion',
        source_id=workspace_id,
        summary=f'Updated console arm snapshot for {workspace.name}',
        metadata={'maturity_score': saved.maturity_score, 'active_tracks': saved.active_tracks},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_console_arm_snapshot', workspace_id=workspace_id, maturity_score=saved.maturity_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_console_arm_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = ConsoleArmWorkspaceRepository(db)
    snapshot_repo = ConsoleArmSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_console_arm(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_console_arm_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_console_expansion_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = ConsoleArmWorkspaceRepository(db).list()
    snapshot_repo = ConsoleArmSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_console_expansion_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_console_expansion_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
