from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.storage.orm_marketing import MarketingProjectORM
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/marketing", tags=["marketing_app_links_v2"])
telemetry = TelemetryLogger(filepath="var/marketing_telemetry.jsonl")


@router.get("/projects/{project_id}/linked-apps-v2")
def get_marketing_linked_apps_v2(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    app_repo = AppRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")

    apps = []
    for app_id in project.linked_apps:
        app = app_repo.get(app_id)
        if app is not None:
            apps.append(app.model_dump(mode="json"))

    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_linked_apps_v2", project_id=project_id, returned_count=len(apps))
    return {"count": len(apps), "items": apps}


@router.post("/projects/{project_id}/link-app-v2/{app_id}")
def link_app_to_marketing_project_v2(project_id: str, app_id: str, db: Session = Depends(get_db)) -> dict:
    app_repo = AppRepository(db)
    app = app_repo.get(app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")

    row = db.get(MarketingProjectORM, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="marketing project not found")

    linked_apps = row.linked_apps or []
    if app_id not in linked_apps:
        row.linked_apps = [*linked_apps, app_id]
        db.add(row)
        db.commit()
        db.refresh(row)

    project = MarketingProjectRepository(db).get(project_id)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="link_app_to_marketing_project_v2", project_id=project_id, app_id=app_id)
    return project.model_dump(mode="json")
