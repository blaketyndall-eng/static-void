from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_views"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/watchlist")
def get_investment_watchlist(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    watchlist = [
        item for item in theses if item.get("status") == "watch" or item.get("recommendation_state") == "watch"
    ]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_watchlist", returned_count=len(watchlist))
    return {"count": len(watchlist), "items": watchlist}


@router.get("/active")
def get_active_investment_theses(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    active = [item for item in theses if item.get("status") in {"active", "scaling"}]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_active_investment_theses", returned_count=len(active))
    return {"count": len(active), "items": active}


@router.get("/catalysts")
def get_upcoming_investment_catalysts(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    catalysts: list[dict] = []
    for thesis in theses:
        for catalyst in thesis.get("catalysts", []):
            catalysts.append(
                {
                    "thesis_id": thesis.get("id"),
                    "ticker": thesis.get("ticker"),
                    "asset_name": thesis.get("asset_name"),
                    "thesis_type": thesis.get("thesis_type"),
                    "catalyst": catalyst,
                }
            )
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_upcoming_investment_catalysts", returned_count=len(catalysts))
    return {"count": len(catalysts), "items": catalysts}


@router.get("/summary")
def get_investment_summary(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]

    by_asset_class: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_recommendation: dict[str, int] = {}
    for thesis in theses:
        asset_class = thesis.get("asset_class", "unknown")
        status = thesis.get("status", "unknown")
        recommendation = thesis.get("recommendation_state", "unknown")
        by_asset_class[asset_class] = by_asset_class.get(asset_class, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        by_recommendation[recommendation] = by_recommendation.get(recommendation, 0) + 1

    payload = {
        "count": len(theses),
        "by_asset_class": by_asset_class,
        "by_status": by_status,
        "by_recommendation": by_recommendation,
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_summary", returned_count=len(theses))
    return payload
