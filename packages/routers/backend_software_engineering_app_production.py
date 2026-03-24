from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.software_engineering import (
    EngineeringExecutionRepository,
    EngineeringExperimentRepository,
    EngineeringProjectRepository,
    EngineeringResearchRepository,
)
from packages.services.software_engineering_app_production import (
    build_app_production_advisory,
    build_app_production_portfolio_summary,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/software-engineering", tags=["software_engineering_app_production"])
telemetry = TelemetryLogger(filepath="var/software_engineering_telemetry.jsonl")


@router.get("/app-production/summary")
def get_app_production_summary(db: Session = Depends(get_db)) -> dict:
    blueprint_repo = AppBlueprintRepository(db)
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    advisories = []
    projects = project_repo.list()
    projects_by_name = {project.name.lower(): project for project in projects}

    for blueprint in blueprint_repo.list():
        linked_project = projects_by_name.get(blueprint.name.lower())
        advisories.append(
            build_app_production_advisory(
                blueprint,
                linked_project,
                None if linked_project is None else research_repo.get(linked_project.id),
                None if linked_project is None else execution_repo.get(linked_project.id),
                None if linked_project is None else experiment_repo.get(linked_project.id),
            )
        )

    portfolio = build_app_production_portfolio_summary(advisories)
    payload = {
        "portfolio": portfolio.model_dump(mode="json"),
        "advisories": [item.model_dump(mode="json") for item in advisories[:15]],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_app_production_summary", returned_count=len(advisories))
    return payload


@router.get("/app-production/blueprint/{blueprint_id}")
def get_blueprint_app_production_advisory(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    blueprint_repo = AppBlueprintRepository(db)
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    blueprint = blueprint_repo.get(blueprint_id)
    if blueprint is None:
        return {"blueprint": None, "advisory": None}

    projects = project_repo.list()
    linked_project = next((project for project in projects if project.name.lower() == blueprint.name.lower()), None)
    advisory = build_app_production_advisory(
        blueprint,
        linked_project,
        None if linked_project is None else research_repo.get(linked_project.id),
        None if linked_project is None else execution_repo.get(linked_project.id),
        None if linked_project is None else experiment_repo.get(linked_project.id),
    )
    payload = {
        "blueprint": blueprint.model_dump(mode="json"),
        "linked_project": None if linked_project is None else linked_project.model_dump(mode="json"),
        "advisory": advisory.model_dump(mode="json"),
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_blueprint_app_production_advisory", blueprint_id=blueprint_id)
    return payload
