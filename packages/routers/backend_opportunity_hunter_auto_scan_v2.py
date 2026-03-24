from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.brain_links import BrainLinkRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.services.opportunity_hunter_auto_scan import build_auto_scan, generate_auto_scan_candidates
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunity_hunter_auto_scan_v2"])
telemetry = TelemetryLogger(filepath="var/opportunity_hunter_telemetry.jsonl")


@router.post("/auto-scan-v2")
def run_auto_opportunity_scan_v2(db: Session = Depends(get_db)) -> dict:
    apps = AppRepository(db).list()
    projects = MarketingProjectRepository(db).list()
    brain_links = BrainLinkRepository(db).list()

    scan_repo = OpportunityScanRepository(db)
    candidate_repo = OpportunityCandidateRepository(db)

    scan = build_auto_scan(name="Auto Opportunity Sweep V2")
    scan.notes = f"Generated from active apps, projects, and {len(brain_links)} brain links."
    saved_scan = scan_repo.create(scan)

    candidates = []
    for candidate in generate_auto_scan_candidates(saved_scan, apps, projects):
        if brain_links:
            candidate.evidence_notes.append({"source": "brain_links", "note": f"{len(brain_links)} active shared links available"})
            candidate.priority_score = min(candidate.priority_score + 3.0, 100.0)
        candidates.append(candidate_repo.create(candidate).model_dump(mode="json"))

    emit_action_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="run_auto_opportunity_scan_v2",
        scan_id=saved_scan.id,
        created_count=len(candidates),
        brain_link_count=len(brain_links),
    )
    return {"scan": saved_scan.model_dump(mode="json"), "count": len(candidates), "brain_link_count": len(brain_links), "items": candidates[:20]}
