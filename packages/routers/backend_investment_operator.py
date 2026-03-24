from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.repositories.investment import (
    CryptoProfileRepository,
    InvestmentThesisRepository,
    OptionsProfileRepository,
    PredictionMarketProfileRepository,
    SwingTradeProfileRepository,
)
from packages.services.investment_agent_orchestration import build_operator_run
from packages.services.investment_crypto_engine import evaluate_crypto_strategy
from packages.services.investment_options_engine import evaluate_options_strategy
from packages.services.investment_prediction_engine import evaluate_prediction_market
from packages.services.investment_risk_engine import build_risk_review
from packages.services.investment_swing_engine import evaluate_swing_trade
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment_operator"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.get("/theses/{thesis_id}/operator-run")
def get_investment_operator_run(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    thesis = thesis_repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")

    category = thesis.asset_class.value
    profile_dict = {}
    engine_output: dict
    liquidity_score = None
    ambiguity_score = None

    if category == "equity":
        profile = SwingTradeProfileRepository(db).get(thesis_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="swing profile not found")
        evaluation = evaluate_swing_trade(thesis, profile)
        engine_output = evaluation.model_dump(mode="json")
        profile_dict = profile.model_dump(mode="json")
    elif category == "option":
        profile = OptionsProfileRepository(db).get(thesis_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="options profile not found")
        evaluation = evaluate_options_strategy(thesis, profile)
        engine_output = evaluation.model_dump(mode="json")
        profile_dict = profile.model_dump(mode="json")
        liquidity_score = evaluation.liquidity_score
    elif category == "crypto":
        profile = CryptoProfileRepository(db).get(thesis_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="crypto profile not found")
        evaluation = evaluate_crypto_strategy(thesis, profile)
        engine_output = evaluation.model_dump(mode="json")
        profile_dict = profile.model_dump(mode="json")
        liquidity_score = evaluation.liquidity_score
    elif category == "prediction_market":
        profile = PredictionMarketProfileRepository(db).get(thesis_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="prediction profile not found")
        evaluation = evaluate_prediction_market(thesis, profile)
        engine_output = evaluation.model_dump(mode="json")
        profile_dict = profile.model_dump(mode="json")
        ambiguity_score = profile.ambiguity_score
    else:
        raise HTTPException(status_code=400, detail="unsupported investment category")

    risk_review = build_risk_review(
        thesis,
        engine_output.get("confidence_score", 0),
        liquidity_score=liquidity_score,
        ambiguity_score=ambiguity_score,
    )
    run = build_operator_run(category, thesis, engine_output, risk_review, profile_dict)
    payload = run.model_dump(mode="json")
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route="get_investment_operator_run",
        thesis_id=thesis_id,
        decision=payload.get("allocation_decision", {}).get("decision"),
    )
    return payload
