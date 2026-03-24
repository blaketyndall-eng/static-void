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
from app_investment_full import app


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


def test_swing_trade_evaluation_returns_confidence_and_recommendation() -> None:
    reset_state()
    client = TestClient(app)

    thesis = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": "equity",
            "instrument_type": "stock",
            "ticker": "NVDA",
            "asset_name": "NVIDIA",
            "thesis_type": "swing_long",
            "timeframe": "2-6 weeks",
            "conviction": 0.72,
            "entry_zone": "118-121",
            "target_zone": "132-138",
            "invalidation": "Daily close below 114",
            "recommendation_state": "starter",
            "portfolio_role": "tactical",
            "notes": "Trend and AI momentum remain supportive.",
            "catalysts": [{"type": "earnings", "date": "2026-05-20"}],
            "risk_flags": ["event_gap"],
        },
    )
    assert thesis.status_code == 200
    thesis_id = thesis.json()["id"]

    swing = client.post(
        f"/api/v1/investment/theses/{thesis_id}/swing-profile",
        json={
            "setup_type": "breakout_continuation",
            "relative_strength": 0.84,
            "atr": 4.2,
            "sector_momentum": 0.78,
            "chart_structure": "tight flag under highs",
            "gap_risk": "earnings in 18 days",
        },
    )
    assert swing.status_code == 200

    evaluation = client.get(f"/api/v1/investment/theses/{thesis_id}/swing-evaluation")
    assert evaluation.status_code == 200
    payload = evaluation.json()
    assert payload["thesis_id"] == thesis_id
    assert payload["confidence_score"] >= 0
    assert payload["recommendation_state"] in {"watch", "starter", "build", "no_trade"}
    assert "summary" in payload
    assert "rationale" in payload
