from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.services.opportunity_hunter_scanners import (
    build_active_app_opportunities,
    build_marketing_adjacency_opportunities,
    build_niche_opportunities,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunity_hunter_scanners"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/scans/{scan_id}/scan-active-apps")
def scan_active_apps_for_opportunities(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    apps = AppRepository(db).list()
    repo = OpportunityCandidateRepository(db)
    created = []
    for candidate in build_active_app_opportunities(scan, apps):
        created.append(repo.create(candidate).model_dump(mode="json"))
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="scan_active_apps_for_opportunities", scan_id=scan_id, created_count=len(created))
    return {"count": len(created), "items": created}


@router.post("/scans/{scan_id}/scan-marketing-adjacencies")
def scan_marketing_adjacencies(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    projects = MarketingProjectRepository(db).list()
    repo = OpportunityCandidateRepository(db)
    created = []
    for candidate in build_marketing_adjacency_opportunities(scan, projects):
        created.append(repo.create(candidate).model_dump(mode="json"))
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="scan_marketing_adjacencies", scan_id=scan_id, created_count=len(created))
    return {"count": len(created), "items": created}


@router.post("/scans/{scan_id}/scan-niches")
def scan_niches(scan_id: str, terms: str = "", db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    niche_terms = [item.strip() for item in terms.split(",") if item.strip()] or scan.source_queries or ["workflow automation", "proposal ops", "industry-specific analytics"]
    repo = OpportunityCandidateRepository(db)
    created = []
    for candidate in build_niche_opportunities(scan, niche_terms):
        created.append(repo.create(candidate).model_dump(mode="json"))
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="scan_niches", scan_id=scan_id, created_count=len(created))
    return {"count": len(created), "items": created}


@router.get("/scans/{scan_id}/scanner-status")
def get_scanner_status(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    candidates = OpportunityCandidateRepository(db).list_for_scan(scan_id)
    payload = {
        "scan": scan.model_dump(mode="json"),
        "candidate_count": len(candidates),
        "source_arms": scan.source_arms,
        "source_queries": scan.source_queries,
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_scanner_status", scan_id=scan_id, returned_count=len(candidates))
    return payload
