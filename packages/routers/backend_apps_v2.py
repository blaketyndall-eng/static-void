from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.apps import (
    CreateAppFeedbackRequest,
    CreateAppRequest,
    CreateAppRunRequest,
    UpdateAppStatusRequest,
    UpdateDeploymentStateRequest,
)
from packages.domain.apps import (
    AppFeedbackItem,
    AppRecord,
    AppRun,
    AppStatus,
    AppType,
    DeploymentState,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.apps import AppFeedbackRepository, AppRepository, AppRunRepository
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/apps", tags=["apps_v2"])
telemetry = TelemetryLogger(filepath="var/apps_telemetry.jsonl")


@router.post("")
def create_app_v2(payload: CreateAppRequest, db: Session = Depends(get_db)) -> dict:
    try:
        app_type = AppType(payload.app_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid app_type") from exc
    repo = AppRepository(db)
    app = AppRecord(
        name=payload.name,
        app_type=app_type,
        owner=payload.owner,
        description=payload.description,
        version=payload.version,
        runtime_url=payload.runtime_url,
        tags=payload.tags,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(app)
    record_system_event(
        db,
        event_type=SystemEventType.app_created,
        source_arm="apps",
        source_id=saved.id,
        summary=f"Created app {saved.name}",
        metadata={"app_type": saved.app_type.value, "owner": saved.owner},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app_v2", app_id=saved.id, app_type=saved.app_type.value)
    return saved.model_dump(mode="json")


@router.post("/{app_id}/status")
def update_app_status_v2(app_id: str, payload: UpdateAppStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = AppStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid app status") from exc
    repo = AppRepository(db)
    app = repo.update_status(app_id, status)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    record_system_event(
        db,
        event_type=SystemEventType.app_updated,
        source_arm="apps",
        source_id=app_id,
        summary=f"Updated app {app.name} status to {app.status.value}",
        metadata={"status": app.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_app_status_v2", app_id=app_id, status=app.status.value)
    return app.model_dump(mode="json")


@router.post("/{app_id}/deployment")
def update_app_deployment_state_v2(app_id: str, payload: UpdateDeploymentStateRequest, db: Session = Depends(get_db)) -> dict:
    try:
        deployment_state = DeploymentState(payload.deployment_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid deployment_state") from exc
    repo = AppRepository(db)
    app = repo.update_deployment_state(app_id, deployment_state)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    record_system_event(
        db,
        event_type=SystemEventType.app_updated,
        source_arm="apps",
        source_id=app_id,
        summary=f"Updated app {app.name} deployment to {app.deployment_state.value}",
        metadata={"deployment_state": app.deployment_state.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_app_deployment_state_v2", app_id=app_id, deployment_state=app.deployment_state.value)
    return app.model_dump(mode="json")


@router.post("/{app_id}/runs")
def create_app_run_v2(app_id: str, payload: CreateAppRunRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    app = app_repo.get(app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    run_repo = AppRunRepository(db)
    run = AppRun(app_id=app_id, output_summary=payload.output_summary, error_summary=payload.error_summary)
    saved = run_repo.create(run)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm="apps",
        source_id=app_id,
        summary=f"Created app run for {app.name}",
        metadata={"run_id": saved.id},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app_run_v2", app_id=app_id, run_id=saved.id)
    return saved.model_dump(mode="json")


@router.post("/{app_id}/feedback")
def create_app_feedback_v2(app_id: str, payload: CreateAppFeedbackRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    app = app_repo.get(app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    repo = AppFeedbackRepository(db)
    feedback = AppFeedbackItem(app_id=app_id, category=payload.category, severity=payload.severity, message=payload.message)
    saved = repo.create(feedback)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm="apps",
        source_id=app_id,
        summary=f"Recorded feedback for {app.name}",
        metadata={"category": saved.category, "severity": saved.severity},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app_feedback_v2", app_id=app_id, category=saved.category)
    return saved.model_dump(mode="json")


@router.get("")
def list_apps_v2(db: Session = Depends(get_db)) -> list[dict]:
    repo = AppRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_apps_v2", returned_count=len(payload))
    return payload
