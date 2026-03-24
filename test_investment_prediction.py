from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_investment import (
    CryptoProfileORM,
    InvestmentThesisORM,
    OptionsProfileORM,
    PredictionMarketProfileORM,
    SwingTradeProfileORM,
)
from app_investment_three_engine import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/investment_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    InvestmentThesisORM.metadata.create_all(bind=db_session.engine)
    SwingTradeProfileORM.metadata.create_all(bind=db_session.engine)
    OptionsProfileORM.metadata.create_all(bind=db_session.engine)
    CryptoProfileORM.metadata.create_all(bind=db_session.engine)
    PredictionMarketProfileORM.metadata.create_all(bind=db_session.engine)


def test_prediction_market_evaluation_returns_confidence_and_recommendation() -> None:
    reset_state()
    client = TestClient(app)

    thesis = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": "prediction_market",
            "instrument_type": "event_contract",
            "ticker": "FEDCUT_JULY",
            "asset_name": "Fed cut by July",
            "thesis_type": "event_probability",
            "timeframe": "3 months",
            "conviction": 0.61,
            "entry_zone": "0.38-0.42",
            "target_zone": "0.50-0.56",
            "invalidation": "Macro data turns sharply inflationary",
            "recommendation_state": "watch",
            "portfolio_role": "tactical",
            "notes": "Pricing seems modestly low versus internal macro read.",
            "catalysts": [{"type": "CPI", "date": "2026-04-10"}],
            "risk_flags": ["settlement_rule_review"],
        },
    )
    assert thesis.status_code == 200
    thesis_id = thesis.json()["id"]

    prediction = client.post(
        f"/api/v1/investment/theses/{thesis_id}/prediction-profile",
        json={
            "market_venue": "Kalshi",
            "contract_text": "Will the Fed cut rates by July?",
            "settlement_rule_summary": "Resolves yes if official target rate is lower by July meeting.",
            "event_date": "2026-07-31",
            "implied_probability": 0.41,
            "estimated_probability": 0.49,
            "edge": 0.08,
            "max_stake": 500,
            "ambiguity_score": 0.12,
        },
    )
    assert prediction.status_code == 200

    evaluation = client.get(f"/api/v1/investment/theses/{thesis_id}/prediction-evaluation")
    assert evaluation.status_code == 200
    payload = evaluation.json()
    assert payload["thesis_id"] == thesis_id
    assert payload["confidence_score"] >= 0
    assert payload["recommendation_state"] in {"watch", "starter", "build", "no_trade"}
    assert payload["market_venue"] == "Kalshi"
    assert "summary" in payload
    assert "rationale" in payload
