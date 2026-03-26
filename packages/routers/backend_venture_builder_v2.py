from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.venture_builder import CreateVentureBuilderWorkspaceRequest, UpdateVentureBuilderStatusRequest, UpsertVentureBuilderSnapshotRequest
from packages.domain.system_events import SystemEventType
from packages.domain.venture_builder import VentureBuilderSnapshot, VentureBuilderStatus, VentureBuilderWorkspace
from packages.repositories.venture_builder import VentureBuilderSnapshotRepository, VentureBuilderWorkspaceRepository
from packages.services.system_event_helpers import record_system_event
from packages.services.venture_builder import build_venture_builder_summary, review_venture_builder_workspace
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/venture-builder', tags=['venture_builder'])
telemetry = TelemetryLogger(filepath='var/venture_builder_telemetry.jsonl')


@router.post('/workspaces')
def create_workspace(payload: CreateVentureBuilderWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = VentureBuilderWorkspaceRepository(db)
    workspace = VentureBuilderWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        venture_ideas=payload.venture_ideas,
        thesis_points=payload.thesis_points,
        linked_apps=payload.linked_apps,
        linked_modules=payload.linked_modules,
    )
    saved = repo.create(workspace)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='venture_builder', source_id=saved.id, summary=f'Created venture builder workspace {saved.name}', metadata={'owner': saved.owner})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_venture_builder_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in VentureBuilderWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_venture_builder_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_status(workspace_id: str, payload: UpdateVentureBuilderStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = VentureBuilderStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = VentureBuilderWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_venture_builder_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_snapshot(workspace_id: str, payload: UpsertVentureBuilderSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = VentureBuilderWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = VentureBuilderSnapshotRepository(db)
    snapshot = VentureBuilderSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_venture_builder_snapshot', workspace_id=workspace_id, launch_readiness_score=saved.launch_readiness_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = VentureBuilderWorkspaceRepository(db)
    snapshot_repo = VentureBuilderSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_venture_builder_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_venture_builder_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = VentureBuilderWorkspaceRepository(db).list()
    snapshot_repo = VentureBuilderSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_venture_builder_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_venture_builder_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
