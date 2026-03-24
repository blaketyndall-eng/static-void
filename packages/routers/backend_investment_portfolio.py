from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_portfolio"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/portfolio/roles")
def get_investment_portfolio_roles(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    by_role: dict[str, int] = {}
    for thesis in theses:
        role = thesis.get("portfolio_role", "unknown")
        by_role[role] = by_role.get(role, 0) + 1
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_portfolio_roles", returned_count=len(theses))
    return {"count": len(theses), "by_role": by_role}


@router.get("/portfolio/risk-flags")
def get_investment_risk_flags(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    items: list[dict] = []
    counts: dict[str, int] = {}
    for thesis in theses:
        for flag in thesis.get("risk_flags", []):
            counts[flag] = counts.get(flag, 0) + 1
            items.append(
                {
                    "thesis_id": thesis.get("id"),
                    "ticker": thesis.get("ticker"),
                    "asset_name": thesis.get("asset_name"),
                    "flag": flag,
                }
            )
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_risk_flags", returned_count=len(items))
    return {"count": len(items), "by_flag": counts, "items": items}


@router.get("/portfolio/exposure")
def get_investment_exposure_summary(db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    theses = [item.model_dump(mode="json") for item in repo.list()]
    by_asset_class: dict[str, int] = {}
    by_recommendation: dict[str, int] = {}
    by_timeframe: dict[str, int] = {}
    for thesis in theses:
        asset_class = thesis.get("asset_class", "unknown")
        recommendation = thesis.get("recommendation_state", "unknown")
        timeframe = thesis.get("timeframe", "unknown")
        by_asset_class[asset_class] = by_asset_class.get(asset_class, 0) + 1
        by_recommendation[recommendation] = by_recommendation.get(recommendation, 0) + 1
        by_timeframe[timeframe] = by_timeframe.get(timeframe, 0) + 1
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_exposure_summary", returned_count=len(theses))
    return {
        "count": len(theses),
        "by_asset_class": by_asset_class,
        "by_recommendation": by_recommendation,
        "by_timeframe": by_timeframe,
    }
