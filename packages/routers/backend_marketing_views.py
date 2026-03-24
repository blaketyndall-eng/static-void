from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.marketing import ContentAssetRepository, MarketingAnalyticsRepository, MarketingProjectRepository, MarketingResearchRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/marketing", tags=["marketing_views"])
telemetry = TelemetryLogger(filepath="var/marketing_telemetry.jsonl")


@router.get("/summary")
def get_marketing_summary(db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    projects = [item.model_dump(mode="json") for item in project_repo.list()]

    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for project in projects:
        by_type[project["project_type"]] = by_type.get(project["project_type"], 0) + 1
        by_status[project["status"]] = by_status.get(project["status"], 0) + 1

    payload = {
        "count": len(projects),
        "by_type": by_type,
        "by_status": by_status,
        "recent_projects": projects[:10],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_summary", returned_count=len(projects))
    return payload


@router.get("/projects/{project_id}/operator-summary")
def get_marketing_project_operator_summary(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    content_repo = ContentAssetRepository(db)
    analytics_repo = MarketingAnalyticsRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        return {"project": None, "research": None, "content_count": 0, "analytics": None}

    research = research_repo.get(project_id)
    content_assets = [item.model_dump(mode="json") for item in content_repo.list_for_project(project_id)]
    analytics = analytics_repo.get(project_id)
    payload = {
        "project": project.model_dump(mode="json"),
        "research": None if research is None else research.model_dump(mode="json"),
        "content_count": len(content_assets),
        "content_assets": content_assets[:10],
        "analytics": None if analytics is None else analytics.model_dump(mode="json"),
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_project_operator_summary", project_id=project_id, content_count=len(content_assets))
    return payload
