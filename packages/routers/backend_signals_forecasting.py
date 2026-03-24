from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.signals_forecasting import (
    CreateSignalsForecastingWorkspaceRequest,
    UpdateSignalsForecastingStatusRequest,
    UpsertSignalsForecastingSnapshotRequest,
)
from packages.domain.signals_forecasting import (
    SignalsForecastingSnapshot,
    SignalsForecastingStatus,
    SignalsForecastingWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.signals_forecasting import (
    SignalsForecastingSnapshotRepository,
    SignalsForecastingWorkspaceRepository,
)
from packages.services.signals_forecasting import (
    build_signals_forecasting_summary,
    review_signals_forecasting_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/signals-forecasting', tags=['signals_forecasting'])
telemetry = TelemetryLogger(filepath='var/signals_forecasting_telemetry.jsonl')


@router.post('/workspaces')
def create_signals_forecasting_workspace(payload: CreateSignalsForecastingWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = SignalsForecastingWorkspaceRepository(db)
    workspace = SignalsForecastingWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        tracked_domains=payload.tracked_domains,
        forecast_targets=payload.forecast_targets,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='signals_forecasting',
        source_id=saved.id,
        summary=f'Created signals workspace {saved.name}',
        metadata={'owner': saved.owner, 'tracked_domains': saved.tracked_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_signals_forecasting_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_signals_forecasting_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in SignalsForecastingWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_signals_forecasting_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_signals_forecasting_status(workspace_id: str, payload: UpdateSignalsForecastingStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = SignalsForecastingStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = SignalsForecastingWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='signals_forecasting',
        source_id=workspace_id,
        summary=f'Updated signals workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_signals_forecasting_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_signals_forecasting_snapshot(workspace_id: str, payload: UpsertSignalsForecastingSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = SignalsForecastingWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = SignalsForecastingSnapshotRepository(db)
    snapshot = SignalsForecastingSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='signals_forecasting',
        source_id=workspace_id,
        summary=f'Updated signals snapshot for {workspace.name}',
        metadata={
            'signal_quality_score': saved.signal_quality_score,
            'forecast_confidence_score': saved.forecast_confidence_score,
            'anomaly_alerts': saved.anomaly_alerts,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_signals_forecasting_snapshot', workspace_id=workspace_id, signal_quality_score=saved.signal_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_signals_forecasting_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = SignalsForecastingWorkspaceRepository(db)
    snapshot_repo = SignalsForecastingSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_signals_forecasting_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_signals_forecasting_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_signals_forecasting_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = SignalsForecastingWorkspaceRepository(db).list()
    snapshot_repo = SignalsForecastingSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_signals_forecasting_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_signals_forecasting_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
