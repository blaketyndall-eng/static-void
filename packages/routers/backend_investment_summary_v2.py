from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository
from packages.repositories.system_events import SystemEventRepository
from packages.services.investment_learning import build_learning_summary
from packages.services.investment_portfolio_risk import build_portfolio_risk_snapshot
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v2/investment", tags=["investment_summary_v2"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/console-summary")
def get_investment_console_summary_v2(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = repo.list()

    thesis_payloads = [item.model_dump(mode="json") for item in theses]
    watchlist = [item for item in thesis_payloads if item.get("status") == "watch" or item.get("recommendation_state") == "watch"]
    active = [item for item in thesis_payloads if item.get("status") in {"active", "scaling"}]

    catalysts: list[dict] = []
    for thesis in thesis_payloads:
        for catalyst in thesis.get("catalysts", []):
            catalysts.append(
                {
                    "thesis_id": thesis.get("id"),
                    "ticker": thesis.get("ticker"),
                    "asset_name": thesis.get("asset_name"),
                    "catalyst": catalyst,
                }
            )

    portfolio_snapshot = build_portfolio_risk_snapshot(theses)
    learning_summary = build_learning_summary(theses)
    recent_activity = [item.model_dump(mode="json") for item in SystemEventRepository(db).list() if item.source_arm == "investment"]

    payload = {
        "total_theses": len(thesis_payloads),
        "watchlist_count": len(watchlist),
        "active_count": len(active),
        "catalyst_count": len(catalysts),
        "portfolio_snapshot": portfolio_snapshot.model_dump(mode="json"),
        "learning_summary": learning_summary.model_dump(mode="json"),
        "watchlist": watchlist[:10],
        "active": active[:10],
        "catalysts": catalysts[:10],
        "recent_activity": recent_activity[:10],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_investment_console_summary_v2",
        returned_count=len(thesis_payloads),
        active_count=len(active),
        watchlist_count=len(watchlist),
    )
    return payload
