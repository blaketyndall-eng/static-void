from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.services.opportunity_hunter_auto_scan import build_auto_scan, generate_auto_scan_candidates
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunity_hunter_auto_scan"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/auto-scan")
def run_auto_opportunity_scan(db: Session = Depends(get_db)) -> dict:
    apps = AppRepository(db).list()
    projects = MarketingProjectRepository(db).list()

    scan_repo = OpportunityScanRepository(db)
    candidate_repo = OpportunityCandidateRepository(db)

    scan = scan_repo.create(build_auto_scan())
    candidates = []
    for candidate in generate_auto_scan_candidates(scan, apps, projects):
        candidates.append(candidate_repo.create(candidate).model_dump(mode="json"))

    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="run_auto_opportunity_scan", scan_id=scan.id, created_count=len(candidates))
    return {"scan": scan.model_dump(mode="json"), "count": len(candidates), "items": candidates[:20]}
