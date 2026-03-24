from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.brain_links import BrainLinkRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.repositories.system_events import SystemEventRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/global", tags=["global_summary_v2"])
telemetry = TelemetryLogger(filepath="var/system_events_telemetry.jsonl")


@router.get("/summary-v2")
def get_global_system_summary_v2(db: Session = Depends(get_db)) -> dict:
    brain_links = BrainLinkRepository(db).list()
    module_summary = [item.model_dump(mode="json") for item in BrainLinkRepository(db).summarize_modules()]
    events = [item.model_dump(mode="json") for item in SystemEventRepository(db).list()]
    scans = OpportunityScanRepository(db).list()
    opp_repo = OpportunityCandidateRepository(db)
    candidates = []
    for scan in scans:
        candidates.extend(opp_repo.list_for_scan(scan.id))

    payload = {
        "brain_links": {
            "count": len(brain_links),
            "modules": module_summary[:10],
        },
        "system_events": {
            "count": len(events),
            "recent": events[:15],
        },
        "opportunity_hunter": {
            "scan_count": len(scans),
            "candidate_count": len(candidates),
        },
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_global_system_summary_v2",
        returned_count=(len(brain_links) + len(events) + len(candidates)),
    )
    return payload
