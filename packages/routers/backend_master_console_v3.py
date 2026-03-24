from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.brain_links import BrainLinkRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.repositories.investment import InvestmentThesisRepository
from packages.repositories.system_events import SystemEventRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/master-console", tags=["master_console_v3"])
telemetry = TelemetryLogger(filepath="var/master_console_telemetry.jsonl")


@router.get("/summary-v3")
def get_master_console_summary_v3(db: Session = Depends(get_db)) -> dict:
    apps = AppRepository(db).list()
    blueprints = AppBlueprintRepository(db).list()
    marketing_projects = MarketingProjectRepository(db).list()
    scans = OpportunityScanRepository(db).list()
    opp_repo = OpportunityCandidateRepository(db)
    opportunity_candidates = []
    for scan in scans:
        opportunity_candidates.extend(opp_repo.list_for_scan(scan.id))
    investments = InvestmentThesisRepository(db).list()
    brain_links = BrainLinkRepository(db).list()
    module_summary = [item.model_dump(mode="json") for item in BrainLinkRepository(db).summarize_modules()]
    system_events = [item.model_dump(mode="json") for item in SystemEventRepository(db).list()]

    payload = {
        "apps": {
            "count": len(apps),
            "active": len([item for item in apps if item.status.value == "active"]),
        },
        "app_builder": {
            "count": len(blueprints),
        },
        "marketing": {
            "count": len(marketing_projects),
            "active": len([item for item in marketing_projects if item.status.value == "active"]),
        },
        "opportunity_hunter": {
            "scan_count": len(scans),
            "candidate_count": len(opportunity_candidates),
        },
        "investment": {
            "count": len(investments),
            "active": len([item for item in investments if item.status.value in {"active", "scaling"}]),
        },
        "brain_links": {
            "count": len(brain_links),
            "module_count": len(module_summary),
            "modules": module_summary[:10],
        },
        "recent_activity": system_events[:15],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_master_console_summary_v3",
        returned_count=(len(apps) + len(blueprints) + len(marketing_projects) + len(scans) + len(investments) + len(brain_links) + len(system_events)),
    )
    return payload
