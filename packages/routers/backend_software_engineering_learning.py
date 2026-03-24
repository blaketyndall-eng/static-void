from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.software_engineering import (
    EngineeringExecutionRepository,
    EngineeringExperimentRepository,
    EngineeringProjectRepository,
    EngineeringResearchRepository,
)
from packages.services.software_engineering_learning import (
    build_engineering_learning_summary,
    review_engineering_project,
)
from packages.services.software_engineering_operator import build_engineering_operator_run
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/software-engineering", tags=["software_engineering_learning"])
telemetry = TelemetryLogger(filepath="var/software_engineering_telemetry.jsonl")


@router.get("/projects/{project_id}/review")
def get_engineering_project_review(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="engineering project not found")

    review = review_engineering_project(
        project,
        research_repo.get(project_id),
        execution_repo.get(project_id),
        experiment_repo.get(project_id),
    )
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_engineering_project_review", project_id=project_id, review_score=review.review_score)
    return review.model_dump(mode="json")


@router.get("/learning/summary")
def get_engineering_learning_summary(db: Session = Depends(get_db)) -> dict:
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    reviews = []
    for project in project_repo.list():
        reviews.append(
            review_engineering_project(
                project,
                research_repo.get(project.id),
                execution_repo.get(project.id),
                experiment_repo.get(project.id),
            )
        )
    summary = build_engineering_learning_summary(reviews)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_engineering_learning_summary", returned_count=summary.total_projects)
    return summary.model_dump(mode="json")


@router.get("/projects/{project_id}/operator-run")
def get_engineering_operator_run(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="engineering project not found")

    run = build_engineering_operator_run(
        project,
        research_repo.get(project_id),
        execution_repo.get(project_id),
        experiment_repo.get(project_id),
    )
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_engineering_operator_run",
        project_id=project_id,
        decision=run.risk_review.decision.value if run.risk_review else None,
    )
    return run.model_dump(mode="json")
