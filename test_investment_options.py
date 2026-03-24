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
from app_investment_multi_engine import app


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


def test_options_strategy_evaluation_returns_confidence_and_recommendation() -> None:
    reset_state()
    client = TestClient(app)

    thesis = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": "option",
            "instrument_type": "call_vertical",
            "ticker": "NVDA",
            "asset_name": "NVIDIA",
            "thesis_type": "options_long",
            "timeframe": "2-4 weeks",
            "conviction": 0.68,
            "entry_zone": "120-123",
            "target_zone": "132-136",
            "invalidation": "Underlying close below 116",
            "recommendation_state": "starter",
            "portfolio_role": "tactical",
            "notes": "Prefer defined-risk upside expression.",
            "catalysts": [{"type": "earnings", "date": "2026-05-20"}],
            "risk_flags": ["iv_elevated"],
        },
    )
    assert thesis.status_code == 200
    thesis_id = thesis.json()["id"]

    options = client.post(
        f"/api/v1/investment/theses/{thesis_id}/options-profile",
        json={
            "underlying_ticker": "NVDA",
            "structure_type": "call_vertical",
            "expiry": "2026-05-15",
            "strikes": [120, 130],
            "debit_credit": "debit",
            "max_loss": 320,
            "max_gain": 680,
            "iv_context": "elevated but acceptable",
            "greeks": {"delta": 0.41},
            "liquidity_score": 0.9,
        },
    )
    assert options.status_code == 200

    evaluation = client.get(f"/api/v1/investment/theses/{thesis_id}/options-evaluation")
    assert evaluation.status_code == 200
    payload = evaluation.json()
    assert payload["thesis_id"] == thesis_id
    assert payload["confidence_score"] >= 0
    assert payload["recommendation_state"] in {"watch", "starter", "build", "no_trade"}
    assert "summary" in payload
    assert "rationale" in payload
