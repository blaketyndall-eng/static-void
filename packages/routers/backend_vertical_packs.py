from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.vertical_packs_config import (
    CreateVerticalPacksWorkspaceRequest,
    UpdateVerticalPacksStatusRequest,
    UpsertVerticalPacksSnapshotRequest,
)
from packages.domain.system_events import SystemEventType
from packages.domain.vertical_packs import (
    VerticalPacksSnapshot,
    VerticalPacksStatus,
    VerticalPacksWorkspace,
)
from packages.repositories.verticalization_store import (
    VerticalPacksSnapshotRepository,
    VerticalPacksWorkspaceRepository,
)
from packages.services.system_event_helpers import record_system_event
from packages.services.vertical_pack_ops import (
    build_vertical_pack_summary,
    review_vertical_pack_workspace,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/vertical-packs', tags=['vertical_packs'])
telemetry = TelemetryLogger(filepath='var/vertical_packs_telemetry.jsonl')


@router.post('/workspaces')
def create_vertical_packs_workspace(payload: CreateVerticalPacksWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = VerticalPacksWorkspaceRepository(db)
    workspace = VerticalPacksWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        industries=payload.industries,
        pack_goals=payload.pack_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='vertical_packs',
        source_id=saved.id,
        summary=f'Created vertical pack workspace {saved.name}',
        metadata={'owner': saved.owner, 'industries': saved.industries},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_vertical_packs_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_vertical_packs_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in VerticalPacksWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_vertical_packs_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_vertical_packs_status(workspace_id: str, payload: UpdateVerticalPacksStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = VerticalPacksStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = VerticalPacksWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='vertical_packs',
        source_id=workspace_id,
        summary=f'Updated vertical pack workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_vertical_packs_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_vertical_packs_snapshot(workspace_id: str, payload: UpsertVerticalPacksSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = VerticalPacksWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = VerticalPacksSnapshotRepository(db)
    snapshot = VerticalPacksSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='vertical_packs',
        source_id=workspace_id,
        summary=f'Updated vertical pack snapshot for {workspace.name}',
        metadata={
            'pack_quality_score': saved.pack_quality_score,
            'adaptation_readiness_score': saved.adaptation_readiness_score,
            'pack_templates': saved.pack_templates,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_vertical_packs_snapshot', workspace_id=workspace_id, pack_quality_score=saved.pack_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_vertical_packs_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = VerticalPacksWorkspaceRepository(db)
    snapshot_repo = VerticalPacksSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_vertical_pack_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_vertical_packs_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_vertical_packs_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = VerticalPacksWorkspaceRepository(db).list()
    snapshot_repo = VerticalPacksSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_vertical_pack_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_vertical_packs_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
