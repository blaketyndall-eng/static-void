from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.app_builder import CreateAppBlueprintRequest, GenerateScaffoldPlanRequest
from packages.domain.app_builder import AppTemplateType
from packages.repositories.app_builder import AppBlueprintRepository, AppScaffoldPlanRepository
from packages.services.app_blueprint_generator import build_blueprint, generate_scaffold_plan
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/app-builder", tags=["app_builder_persistent"])
telemetry = TelemetryLogger(filepath="var/app_builder_telemetry.jsonl")


@router.post("/persistent-blueprints")
def create_persistent_blueprint(payload: CreateAppBlueprintRequest, db: Session = Depends(get_db)) -> dict:
    try:
        app_type = AppTemplateType(payload.app_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid app_type") from exc

    repo = AppBlueprintRepository(db)
    blueprint = build_blueprint(
        name=payload.name,
        app_type=app_type,
        description=payload.description,
        target_users=payload.target_users,
        workflows=payload.workflows,
        required_engines=payload.required_engines,
        primary_views=payload.primary_views,
        data_sources=payload.data_sources,
        notes=payload.notes,
    )
    saved = repo.create(blueprint)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_persistent_blueprint", blueprint_id=saved.id, app_type=saved.app_type.value)
    return saved.model_dump(mode="json")


@router.get("/persistent-blueprints")
def list_persistent_blueprints(db: Session = Depends(get_db)) -> list[dict]:
    repo = AppBlueprintRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_persistent_blueprints", returned_count=len(payload))
    return payload


@router.get("/persistent-blueprints/{blueprint_id}")
def get_persistent_blueprint(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppBlueprintRepository(db)
    blueprint = repo.get(blueprint_id)
    if blueprint is None:
        raise HTTPException(status_code=404, detail="blueprint not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_persistent_blueprint", blueprint_id=blueprint_id)
    return blueprint.model_dump(mode="json")


@router.post("/persistent-blueprints/{blueprint_id}/scaffold-plan")
def create_persistent_scaffold_plan(blueprint_id: str, payload: GenerateScaffoldPlanRequest, db: Session = Depends(get_db)) -> dict:
    blueprint_repo = AppBlueprintRepository(db)
    plan_repo = AppScaffoldPlanRepository(db)

    blueprint = blueprint_repo.get(blueprint_id)
    if blueprint is None:
        raise HTTPException(status_code=404, detail="blueprint not found")

    plan = generate_scaffold_plan(
        blueprint,
        include_observability=payload.include_observability,
        include_tests=payload.include_tests,
        include_runtime_apps=payload.include_runtime_apps,
        tech_debt_items=payload.tech_debt_items,
    )
    saved = plan_repo.upsert(plan)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_persistent_scaffold_plan", blueprint_id=blueprint_id, generated_count=len(saved.generated_files))
    return saved.model_dump(mode="json")


@router.get("/persistent-blueprints/{blueprint_id}/scaffold-plan")
def get_persistent_scaffold_plan(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppScaffoldPlanRepository(db)
    plan = repo.get(blueprint_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="scaffold plan not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_persistent_scaffold_plan", blueprint_id=blueprint_id)
    return plan.model_dump(mode="json")
