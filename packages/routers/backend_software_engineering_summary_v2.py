from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.software_engineering import (
    EngineeringExecutionRepository,
    EngineeringExperimentRepository,
    EngineeringProjectRepository,
    EngineeringResearchRepository,
)
from packages.repositories.system_events import SystemEventRepository
from packages.services.software_engineering_learning import (
    build_engineering_learning_summary,
    review_engineering_project,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/software-engineering", tags=["software_engineering_summary_v2"])
telemetry = TelemetryLogger(filepath="var/software_engineering_telemetry.jsonl")


@router.get("/summary")
def get_software_engineering_summary_v2(db: Session = Depends(get_db)) -> dict:
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)
    event_repo = SystemEventRepository(db)

    projects = project_repo.list()
    project_payloads = [item.model_dump(mode="json") for item in projects]
    active = [item for item in project_payloads if item.get("status") == "active"]

    research_ready = 0
    execution_ready = 0
    experimentation_ready = 0
    reviews = []
    operator_notes = []

    for project in projects:
        research = research_repo.get(project.id)
        execution = execution_repo.get(project.id)
        experiments = experiment_repo.get(project.id)
        if research is not None:
            research_ready += 1
        if execution is not None:
            execution_ready += 1
        if experiments is not None:
            experimentation_ready += 1
        review = review_engineering_project(project, research, execution, experiments)
        reviews.append(review)
        operator_notes.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "review_score": review.review_score,
                "top_lessons": review.lessons[:2],
            }
        )

    learning_summary = build_engineering_learning_summary(reviews)
    recent_activity = [item.model_dump(mode="json") for item in event_repo.list() if item.source_arm == "software_engineering"]

    payload = {
        "total_projects": len(project_payloads),
        "active_projects": len(active),
        "research_ready": research_ready,
        "execution_ready": execution_ready,
        "experimentation_ready": experimentation_ready,
        "learning_summary": learning_summary.model_dump(mode="json"),
        "recent_projects": project_payloads[:10],
        "operator_notes": operator_notes[:10],
        "recent_activity": recent_activity[:10],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_software_engineering_summary_v2",
        returned_count=len(project_payloads),
        active_count=len(active),
    )
    return payload
