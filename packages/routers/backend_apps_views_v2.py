from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppFeedbackRepository, AppRepository, AppRunRepository
from packages.repositories.system_events import SystemEventRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/apps", tags=["apps_views_v2"])
telemetry = TelemetryLogger(filepath="var/apps_telemetry.jsonl")


@router.get("/summary")
def get_apps_summary_v2(db: Session = Depends(get_db)) -> dict:
    repo = AppRepository(db)
    apps = [item.model_dump(mode="json") for item in repo.list()]
    events = [item.model_dump(mode="json") for item in SystemEventRepository(db).list() if item.source_arm == "apps"]

    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_deployment_state: dict[str, int] = {}
    for app in apps:
        app_type = app.get("app_type", "unknown")
        status = app.get("status", "unknown")
        deployment_state = app.get("deployment_state", "unknown")
        by_type[app_type] = by_type.get(app_type, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        by_deployment_state[deployment_state] = by_deployment_state.get(deployment_state, 0) + 1

    payload = {
        "count": len(apps),
        "by_type": by_type,
        "by_status": by_status,
        "by_deployment_state": by_deployment_state,
        "recent_apps": apps[:10],
        "recent_activity": events[:10],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_apps_summary_v2", returned_count=len(apps))
    return payload


@router.get("/{app_id}/operator-summary")
def get_app_operator_summary_v2(app_id: str, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    run_repo = AppRunRepository(db)
    feedback_repo = AppFeedbackRepository(db)
    event_repo = SystemEventRepository(db)

    app = app_repo.get(app_id)
    if app is None:
        return {"count": 0, "app": None, "runs": [], "feedback": [], "recent_activity": [], "open_feedback_count": 0}

    runs = [item.model_dump(mode="json") for item in run_repo.list_for_app(app_id)]
    feedback = [item.model_dump(mode="json") for item in feedback_repo.list_for_app(app_id)]
    recent_activity = [item.model_dump(mode="json") for item in event_repo.list_for_source("apps", app_id)]
    payload = {
        "app": app.model_dump(mode="json"),
        "run_count": len(runs),
        "feedback_count": len(feedback),
        "runs": runs[:10],
        "feedback": feedback[:10],
        "recent_activity": recent_activity[:10],
        "open_feedback_count": len([item for item in feedback if item.get("severity") in {"warning", "error"}]),
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_app_operator_summary_v2", app_id=app_id, run_count=len(runs), feedback_count=len(feedback))
    return payload
