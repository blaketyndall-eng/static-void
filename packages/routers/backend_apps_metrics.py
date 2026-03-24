from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.apps_metrics import UpsertAppAnalyticsRequest, UpsertAppHealthRequest
from packages.domain.apps import AppAnalyticsSnapshot, AppHealthCheck
from packages.repositories.apps import AppAnalyticsRepository, AppHealthRepository, AppRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/apps", tags=["apps_metrics"])
telemetry = TelemetryLogger(filepath="var/apps_telemetry.jsonl")


@router.post("/{app_id}/analytics")
def upsert_app_analytics(app_id: str, payload: UpsertAppAnalyticsRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    if app_repo.get(app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")
    repo = AppAnalyticsRepository(db)
    snapshot = AppAnalyticsSnapshot(app_id=app_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_app_analytics", app_id=app_id, sessions=saved.sessions)
    return saved.model_dump(mode="json")


@router.get("/{app_id}/analytics")
def get_app_analytics(app_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppAnalyticsRepository(db)
    snapshot = repo.get(app_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="analytics not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_app_analytics", app_id=app_id)
    return snapshot.model_dump(mode="json")


@router.post("/{app_id}/health")
def upsert_app_health(app_id: str, payload: UpsertAppHealthRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    if app_repo.get(app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")
    repo = AppHealthRepository(db)
    check = AppHealthCheck(app_id=app_id, **payload.model_dump())
    saved = repo.upsert(check)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_app_health", app_id=app_id, healthy=saved.healthy)
    return saved.model_dump(mode="json")


@router.get("/{app_id}/health")
def get_app_health(app_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppHealthRepository(db)
    check = repo.get(app_id)
    if check is None:
        raise HTTPException(status_code=404, detail="health not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_app_health", app_id=app_id)
    return check.model_dump(mode="json")
