from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.services.opportunity_hunter_scanners_v2 import (
    build_underserved_industry_opportunities,
    build_workflow_gap_opportunities,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunity_hunter_scanners_v2"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/scans/{scan_id}/scan-underserved-industries")
def scan_underserved_industries(scan_id: str, industries: str = "", db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    selected = [item.strip() for item in industries.split(",") if item.strip()] or None
    repo = OpportunityCandidateRepository(db)
    created = []
    for candidate in build_underserved_industry_opportunities(scan, selected):
        created.append(repo.create(candidate).model_dump(mode="json"))
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="scan_underserved_industries", scan_id=scan_id, created_count=len(created))
    return {"count": len(created), "items": created}


@router.post("/scans/{scan_id}/scan-workflow-gaps")
def scan_workflow_gaps(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    apps = AppRepository(db).list()
    projects = MarketingProjectRepository(db).list()
    repo = OpportunityCandidateRepository(db)
    created = []
    for candidate in build_workflow_gap_opportunities(scan, apps, projects):
        created.append(repo.create(candidate).model_dump(mode="json"))
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="scan_workflow_gaps", scan_id=scan_id, created_count=len(created))
    return {"count": len(created), "items": created}


@router.get("/scans/{scan_id}/scanner-summary-v2")
def get_scanner_summary_v2(scan_id: str, db: Session = Depends(get_db)) -> dict:
    scan = OpportunityScanRepository(db).get(scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="scan not found")
    candidates = OpportunityCandidateRepository(db).list_for_scan(scan_id)
    by_type: dict[str, int] = {}
    for candidate in candidates:
        key = candidate.opportunity_type.value
        by_type[key] = by_type.get(key, 0) + 1
    payload = {
        "scan": scan.model_dump(mode="json"),
        "candidate_count": len(candidates),
        "by_type": by_type,
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_scanner_summary_v2", scan_id=scan_id, returned_count=len(candidates))
    return payload
