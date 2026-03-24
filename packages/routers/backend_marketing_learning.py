from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.marketing import ContentAssetRepository, MarketingAnalyticsRepository, MarketingProjectRepository, MarketingResearchRepository
from packages.services.marketing_learning import build_marketing_learning_summary, review_marketing_project
from packages.services.marketing_operator import build_marketing_operator_run
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/marketing", tags=["marketing_learning"])
telemetry = TelemetryLogger(filepath="var/marketing_telemetry.jsonl")


@router.get("/projects/{project_id}/review")
def get_marketing_project_review(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    content_repo = ContentAssetRepository(db)
    analytics_repo = MarketingAnalyticsRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")

    research = research_repo.get(project_id)
    assets = content_repo.list_for_project(project_id)
    analytics = analytics_repo.get(project_id)
    review = review_marketing_project(project, research, assets, analytics)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_project_review", project_id=project_id, review_score=review.review_score)
    return review.model_dump(mode="json")


@router.get("/learning/summary")
def get_marketing_learning_summary(db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    content_repo = ContentAssetRepository(db)
    analytics_repo = MarketingAnalyticsRepository(db)

    reviews = []
    for project in project_repo.list():
        reviews.append(
            review_marketing_project(
                project,
                research_repo.get(project.id),
                content_repo.list_for_project(project.id),
                analytics_repo.get(project.id),
            )
        )
    summary = build_marketing_learning_summary(reviews)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_learning_summary", returned_count=summary.total_projects)
    return summary.model_dump(mode="json")


@router.get("/projects/{project_id}/operator-run")
def get_marketing_operator_run(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    content_repo = ContentAssetRepository(db)
    analytics_repo = MarketingAnalyticsRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")

    run = build_marketing_operator_run(
        project,
        research_repo.get(project_id),
        content_repo.list_for_project(project_id),
        analytics_repo.get(project_id),
    )
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_marketing_operator_run",
        project_id=project_id,
        decision=run.risk_review.decision.value if run.risk_review else None,
    )
    return run.model_dump(mode="json")
