from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository, SwingTradeProfileRepository
from packages.services.investment_swing_engine import evaluate_swing_trade
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_swing"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/theses/{thesis_id}/swing-evaluation")
def get_swing_trade_evaluation(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    profile_repo = SwingTradeProfileRepository(db)

    thesis = thesis_repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")

    profile = profile_repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="swing profile not found")

    evaluation = evaluate_swing_trade(thesis, profile)
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_swing_trade_evaluation",
        thesis_id=thesis_id,
        confidence_score=evaluation.confidence_score,
        recommendation_state=evaluation.recommendation_state.value,
    )
    return evaluation.model_dump(mode="json")
