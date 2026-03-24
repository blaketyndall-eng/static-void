from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.investment import InvestmentThesisRepository, OptionsProfileRepository
from packages.services.investment_options_engine import evaluate_options_strategy
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_options"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/theses/{thesis_id}/options-evaluation")
def get_options_strategy_evaluation(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    profile_repo = OptionsProfileRepository(db)

    thesis = thesis_repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")

    profile = profile_repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="options profile not found")

    evaluation = evaluate_options_strategy(thesis, profile)
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_options_strategy_evaluation",
        thesis_id=thesis_id,
        confidence_score=evaluation.confidence_score,
        recommendation_state=evaluation.recommendation_state.value,
    )
    return evaluation.model_dump(mode="json")
