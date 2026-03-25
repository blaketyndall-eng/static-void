from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.ingestion_data_acquisition import (
    CreateIngestionDataAcquisitionWorkspaceRequest,
    UpdateIngestionDataAcquisitionStatusRequest,
    UpsertIngestionDataAcquisitionSnapshotRequest,
)
from packages.domain.ingestion_data_acquisition import (
    IngestionDataAcquisitionSnapshot,
    IngestionDataAcquisitionStatus,
    IngestionDataAcquisitionWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.ingestion_data_acquisition import (
    IngestionDataAcquisitionSnapshotRepository,
    IngestionDataAcquisitionWorkspaceRepository,
)
from packages.services.ingestion_data_acquisition import (
    build_ingestion_data_acquisition_summary,
    review_ingestion_data_acquisition_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/ingestion-data-acquisition', tags=['ingestion_data_acquisition'])
telemetry = TelemetryLogger(filepath='var/ingestion_data_acquisition_telemetry.jsonl')


@router.post('/workspaces')
def create_ingestion_workspace(payload: CreateIngestionDataAcquisitionWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = IngestionDataAcquisitionWorkspaceRepository(db)
    workspace = IngestionDataAcquisitionWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        source_targets=payload.source_targets,
        ingestion_goals=payload.ingestion_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ingestion_data_acquisition',
        source_id=saved.id,
        summary=f'Created ingestion workspace {saved.name}',
        metadata={'owner': saved.owner, 'source_targets': saved.source_targets},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_ingestion_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_ingestion_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in IngestionDataAcquisitionWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_ingestion_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_ingestion_status(workspace_id: str, payload: UpdateIngestionDataAcquisitionStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = IngestionDataAcquisitionStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = IngestionDataAcquisitionWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ingestion_data_acquisition',
        source_id=workspace_id,
        summary=f'Updated ingestion workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_ingestion_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_ingestion_snapshot(workspace_id: str, payload: UpsertIngestionDataAcquisitionSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = IngestionDataAcquisitionWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = IngestionDataAcquisitionSnapshotRepository(db)
    snapshot = IngestionDataAcquisitionSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='ingestion_data_acquisition',
        source_id=workspace_id,
        summary=f'Updated ingestion snapshot for {workspace.name}',
        metadata={
            'ingestion_health_score': saved.ingestion_health_score,
            'normalization_readiness_score': saved.normalization_readiness_score,
            'connectors': saved.connectors,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_ingestion_snapshot', workspace_id=workspace_id, ingestion_health_score=saved.ingestion_health_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_ingestion_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = IngestionDataAcquisitionWorkspaceRepository(db)
    snapshot_repo = IngestionDataAcquisitionSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_ingestion_data_acquisition_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_ingestion_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_ingestion_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = IngestionDataAcquisitionWorkspaceRepository(db).list()
    snapshot_repo = IngestionDataAcquisitionSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_ingestion_data_acquisition_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_ingestion_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
