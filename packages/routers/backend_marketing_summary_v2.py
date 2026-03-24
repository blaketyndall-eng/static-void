from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.marketing import ContentAssetRepository, MarketingAnalyticsRepository, MarketingProjectRepository, MarketingResearchRepository
from packages.repositories.system_events import SystemEventRepository
from packages.services.marketing_learning import build_marketing_learning_summary, review_marketing_project
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/marketing", tags=["marketing_summary_v2"])
telemetry = TelemetryLogger(filepath="var/marketing_telemetry.jsonl")


@router.get("/console-summary")
def get_marketing_console_summary_v2(db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    content_repo = ContentAssetRepository(db)
    analytics_repo = MarketingAnalyticsRepository(db)
    event_repo = SystemEventRepository(db)

    projects = project_repo.list()
    project_payloads = [item.model_dump(mode="json") for item in projects]
    active = [item for item in project_payloads if item.get("status") == "active"]

    research_ready = 0
    content_ready = 0
    analytics_ready = 0
    reviews = []
    operator_notes = []

    for project in projects:
        research = research_repo.get(project.id)
        assets = content_repo.list_for_project(project.id)
        analytics = analytics_repo.get(project.id)
        if research is not None:
            research_ready += 1
        if assets:
            content_ready += 1
        if analytics is not None:
            analytics_ready += 1
        review = review_marketing_project(project, research, assets, analytics)
        reviews.append(review)
        operator_notes.append({
            "project_id": project.id,
            "project_name": project.name,
            "review_score": review.review_score,
            "top_lessons": review.lessons[:2],
        })

    learning_summary = build_marketing_learning_summary(reviews)
    recent_activity = [item.model_dump(mode="json") for item in event_repo.list() if item.source_arm == "marketing"]

    payload = {
        "total_projects": len(project_payloads),
        "active_projects": len(active),
        "research_ready": research_ready,
        "content_ready": content_ready,
        "analytics_ready": analytics_ready,
        "learning_summary": learning_summary.model_dump(mode="json"),
        "recent_projects": project_payloads[:10],
        "operator_notes": operator_notes[:10],
        "recent_activity": recent_activity[:10],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_marketing_console_summary_v2",
        returned_count=len(project_payloads),
        active_count=len(active),
    )
    return payload
