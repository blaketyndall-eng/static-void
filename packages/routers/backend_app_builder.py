from fastapi import APIRouter, HTTPException

from packages.contracts.app_builder import CreateAppBlueprintRequest, GenerateScaffoldPlanRequest
from packages.domain.app_builder import AppTemplateType
from packages.services.app_blueprint_generator import build_blueprint, generate_scaffold_plan
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/app-builder", tags=["app_builder"])
telemetry = TelemetryLogger(filepath="var/app_builder_telemetry.jsonl")


@router.post("/blueprints")
def create_app_blueprint(payload: CreateAppBlueprintRequest) -> dict:
    try:
        app_type = AppTemplateType(payload.app_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid app_type") from exc

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
    emit_action_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="create_app_blueprint",
        blueprint_id=blueprint.id,
        app_type=blueprint.app_type.value,
    )
    return blueprint.model_dump(mode="json")


@router.post("/blueprints/{blueprint_id}/scaffold-plan")
def generate_blueprint_scaffold_plan(blueprint_id: str, payload: GenerateScaffoldPlanRequest, blueprint: CreateAppBlueprintRequest | None = None) -> dict:
    # Stateless plan generation endpoint: caller should supply blueprint shape again in future persistent version.
    # For now, synthesize a generic workflow blueprint using the blueprint_id as a handle.
    generated_blueprint = build_blueprint(
        name=f"generated_{blueprint_id}",
        app_type=AppTemplateType.decision_workflow,
        description="Generated scaffold plan",
        target_users=["internal"],
        workflows=["intake", "evaluation", "summary"],
        primary_views=["dashboard", "detail", "summary"],
    )
    generated_blueprint.id = blueprint_id
    plan = generate_scaffold_plan(
        generated_blueprint,
        include_observability=payload.include_observability,
        include_tests=payload.include_tests,
        include_runtime_apps=payload.include_runtime_apps,
        tech_debt_items=payload.tech_debt_items,
    )
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="generate_blueprint_scaffold_plan",
        blueprint_id=blueprint_id,
        generated_count=len(plan.generated_files),
    )
    return plan.model_dump(mode="json")
