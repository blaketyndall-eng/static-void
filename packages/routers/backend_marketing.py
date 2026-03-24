from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.marketing import (
    CreateContentAssetRequest,
    CreateMarketingProjectRequest,
    UpdateMarketingProjectStatusRequest,
    UpsertMarketingAnalyticsRequest,
    UpsertMarketingResearchRequest,
)
from packages.domain.marketing import (
    ContentAsset,
    ContentAssetType,
    MarketingAnalyticsSnapshot,
    MarketingProject,
    MarketingProjectStatus,
    MarketingProjectType,
    MarketingResearchRecord,
)
from packages.repositories.marketing import (
    ContentAssetRepository,
    MarketingAnalyticsRepository,
    MarketingProjectRepository,
    MarketingResearchRepository,
)
from packages.services.marketing_engines import BEST_AVAILABLE_TOOLS, evaluate_content_asset, evaluate_marketing_research
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/marketing", tags=["marketing"])
telemetry = TelemetryLogger(filepath="var/marketing_telemetry.jsonl")


@router.post("/projects")
def create_marketing_project(payload: CreateMarketingProjectRequest, db: Session = Depends(get_db)) -> dict:
    try:
        project_type = MarketingProjectType(payload.project_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid project_type") from exc
    repo = MarketingProjectRepository(db)
    project = MarketingProject(
        name=payload.name,
        project_type=project_type,
        owner=payload.owner,
        description=payload.description,
        audience=payload.audience,
        channels=payload.channels,
        goals=payload.goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(project)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_marketing_project", project_id=saved.id, project_type=saved.project_type.value)
    return saved.model_dump(mode="json")


@router.get("/projects")
def list_marketing_projects(db: Session = Depends(get_db)) -> list[dict]:
    repo = MarketingProjectRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_marketing_projects", returned_count=len(payload))
    return payload


@router.get("/projects/{project_id}")
def get_marketing_project(project_id: str, db: Session = Depends(get_db)) -> dict:
    repo = MarketingProjectRepository(db)
    project = repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_project", project_id=project_id)
    return project.model_dump(mode="json")


@router.post("/projects/{project_id}/status")
def update_marketing_project_status(project_id: str, payload: UpdateMarketingProjectStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = MarketingProjectStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid status") from exc
    repo = MarketingProjectRepository(db)
    project = repo.update_status(project_id, status)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_marketing_project_status", project_id=project_id, status=project.status.value)
    return project.model_dump(mode="json")


@router.post("/projects/{project_id}/research")
def upsert_marketing_research(project_id: str, payload: UpsertMarketingResearchRequest, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    if project_repo.get(project_id) is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    repo = MarketingResearchRepository(db)
    record = MarketingResearchRecord(project_id=project_id, **payload.model_dump())
    saved = repo.upsert(record)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_marketing_research", project_id=project_id, opportunity_score=saved.opportunity_score)
    return saved.model_dump(mode="json")


@router.get("/projects/{project_id}/research")
def get_marketing_research(project_id: str, db: Session = Depends(get_db)) -> dict:
    repo = MarketingResearchRepository(db)
    record = repo.get(project_id)
    if record is None:
        raise HTTPException(status_code=404, detail="marketing research not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_research", project_id=project_id)
    return record.model_dump(mode="json")


@router.get("/projects/{project_id}/research-evaluation")
def get_marketing_research_evaluation(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    research_repo = MarketingResearchRepository(db)
    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    record = research_repo.get(project_id)
    if record is None:
        raise HTTPException(status_code=404, detail="marketing research not found")
    evaluation = evaluate_marketing_research(project, record)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_research_evaluation", project_id=project_id, confidence_score=evaluation.confidence_score)
    return evaluation.model_dump(mode="json")


@router.post("/projects/{project_id}/content-assets")
def create_content_asset(project_id: str, payload: CreateContentAssetRequest, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    if project_repo.get(project_id) is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    try:
        asset_type = ContentAssetType(payload.asset_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid asset_type") from exc
    repo = ContentAssetRepository(db)
    asset = ContentAsset(project_id=project_id, asset_type=asset_type, title=payload.title, status=payload.status, target_channel=payload.target_channel, source_brief=payload.source_brief, generated_outline=payload.generated_outline, body=payload.body, call_to_action=payload.call_to_action)
    saved = repo.create(asset)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_content_asset", project_id=project_id, asset_type=saved.asset_type.value)
    return saved.model_dump(mode="json")


@router.get("/projects/{project_id}/content-assets")
def list_content_assets(project_id: str, db: Session = Depends(get_db)) -> dict:
    repo = ContentAssetRepository(db)
    items = [item.model_dump(mode="json") for item in repo.list_for_project(project_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_content_assets", project_id=project_id, returned_count=len(items))
    return {"count": len(items), "items": items}


@router.get("/projects/{project_id}/content-evaluation")
def get_content_evaluation(project_id: str, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    content_repo = ContentAssetRepository(db)
    project = project_repo.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    assets = content_repo.list_for_project(project_id)
    if not assets:
        raise HTTPException(status_code=404, detail="content assets not found")
    evaluation = evaluate_content_asset(project, assets[-1])
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_content_evaluation", project_id=project_id, confidence_score=evaluation.confidence_score)
    return evaluation.model_dump(mode="json")


@router.post("/projects/{project_id}/analytics")
def upsert_marketing_analytics(project_id: str, payload: UpsertMarketingAnalyticsRequest, db: Session = Depends(get_db)) -> dict:
    project_repo = MarketingProjectRepository(db)
    if project_repo.get(project_id) is None:
        raise HTTPException(status_code=404, detail="marketing project not found")
    repo = MarketingAnalyticsRepository(db)
    snapshot = MarketingAnalyticsSnapshot(project_id=project_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="upsert_marketing_analytics", project_id=project_id, quality_score=saved.quality_score)
    return saved.model_dump(mode="json")


@router.get("/projects/{project_id}/analytics")
def get_marketing_analytics(project_id: str, db: Session = Depends(get_db)) -> dict:
    repo = MarketingAnalyticsRepository(db)
    snapshot = repo.get(project_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="marketing analytics not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_analytics", project_id=project_id)
    return snapshot.model_dump(mode="json")


@router.get("/tools")
def get_marketing_tools() -> dict:
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_marketing_tools", returned_count=len(BEST_AVAILABLE_TOOLS))
    return BEST_AVAILABLE_TOOLS
