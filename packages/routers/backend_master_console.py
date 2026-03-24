from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.repositories.investment import InvestmentThesisRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/master-console", tags=["master_console"])
telemetry = TelemetryLogger(filepath="var/master_console_telemetry.jsonl")


@router.get("/summary")
def get_master_console_summary(db: Session = Depends(get_db)) -> dict:
    apps = AppRepository(db).list()
    blueprints = AppBlueprintRepository(db).list()
    marketing_projects = MarketingProjectRepository(db).list()
    scans = OpportunityScanRepository(db).list()
    scan_ids = [scan.id for scan in scans]
    opportunity_candidates = []
    opp_repo = OpportunityCandidateRepository(db)
    for scan_id in scan_ids:
        opportunity_candidates.extend(opp_repo.list_for_scan(scan_id))
    investments = InvestmentThesisRepository(db).list()

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
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_master_console_summary", returned_count=sum(section.get("count", section.get("candidate_count", 0)) for section in payload.values()))
    return payload
