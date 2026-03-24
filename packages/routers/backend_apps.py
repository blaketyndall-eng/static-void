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
from packages.repositories.apps import AppFeedbackRepository, AppRepository, AppRunRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/apps", tags=["apps"])
telemetry = TelemetryLogger(filepath="var/apps_telemetry.jsonl")


@router.post("")
def create_app(payload: CreateAppRequest, db: Session = Depends(get_db)) -> dict:
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
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app", app_id=saved.id, app_type=saved.app_type.value)
    return saved.model_dump(mode="json")


@router.get("")
def list_apps(db: Session = Depends(get_db)) -> list[dict]:
    repo = AppRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_apps", returned_count=len(payload))
    return payload


@router.get("/{app_id}")
def get_app(app_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppRepository(db)
    app = repo.get(app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_app", app_id=app_id)
    return app.model_dump(mode="json")


@router.post("/{app_id}/status")
def update_app_status(app_id: str, payload: UpdateAppStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = AppStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid app status") from exc
    repo = AppRepository(db)
    app = repo.update_status(app_id, status)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_app_status", app_id=app_id, status=app.status.value)
    return app.model_dump(mode="json")


@router.post("/{app_id}/deployment")
def update_app_deployment_state(app_id: str, payload: UpdateDeploymentStateRequest, db: Session = Depends(get_db)) -> dict:
    try:
        deployment_state = DeploymentState(payload.deployment_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid deployment_state") from exc
    repo = AppRepository(db)
    app = repo.update_deployment_state(app_id, deployment_state)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_app_deployment_state", app_id=app_id, deployment_state=app.deployment_state.value)
    return app.model_dump(mode="json")


@router.post("/{app_id}/runs")
def create_app_run(app_id: str, payload: CreateAppRunRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    if app_repo.get(app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")
    run_repo = AppRunRepository(db)
    run = AppRun(app_id=app_id, output_summary=payload.output_summary, error_summary=payload.error_summary)
    saved = run_repo.create(run)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app_run", app_id=app_id, run_id=saved.id)
    return saved.model_dump(mode="json")


@router.get("/{app_id}/runs")
def list_app_runs(app_id: str, db: Session = Depends(get_db)) -> dict:
    run_repo = AppRunRepository(db)
    runs = [item.model_dump(mode="json") for item in run_repo.list_for_app(app_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_app_runs", app_id=app_id, returned_count=len(runs))
    return {"count": len(runs), "items": runs}


@router.post("/{app_id}/feedback")
def create_app_feedback(app_id: str, payload: CreateAppFeedbackRequest, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    if app_repo.get(app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")
    repo = AppFeedbackRepository(db)
    feedback = AppFeedbackItem(app_id=app_id, category=payload.category, severity=payload.severity, message=payload.message)
    saved = repo.create(feedback)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_app_feedback", app_id=app_id, category=saved.category)
    return saved.model_dump(mode="json")


@router.get("/{app_id}/feedback")
def list_app_feedback(app_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppFeedbackRepository(db)
    items = [item.model_dump(mode="json") for item in repo.list_for_app(app_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_app_feedback", app_id=app_id, returned_count=len(items))
    return {"count": len(items), "items": items}
