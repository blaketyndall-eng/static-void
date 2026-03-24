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
from app_investment_four_engine import app


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


def test_crypto_strategy_evaluation_returns_confidence_and_recommendation() -> None:
    reset_state()
    client = TestClient(app)

    thesis = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": "crypto",
            "instrument_type": "spot",
            "ticker": "BTC",
            "asset_name": "Bitcoin",
            "thesis_type": "crypto_trend",
            "timeframe": "2-8 weeks",
            "conviction": 0.66,
            "entry_zone": "72000-74000",
            "target_zone": "82000-86000",
            "invalidation": "Daily close below 69000",
            "recommendation_state": "starter",
            "portfolio_role": "tactical",
            "notes": "Regime remains risk-on with institutional support.",
            "catalysts": [{"type": "ETF_flow", "date": "2026-04-15"}],
            "risk_flags": ["macro_volatility"],
        },
    )
    assert thesis.status_code == 200
    thesis_id = thesis.json()["id"]

    crypto = client.post(
        f"/api/v1/investment/theses/{thesis_id}/crypto-profile",
        json={
            "token": "BTC",
            "chain_or_ecosystem": "Bitcoin",
            "narrative": "institutional adoption and ETF demand",
            "exchange_liquidity_score": 0.95,
            "regime_bucket": "risk_on",
        },
    )
    assert crypto.status_code == 200

    evaluation = client.get(f"/api/v1/investment/theses/{thesis_id}/crypto-evaluation")
    assert evaluation.status_code == 200
    payload = evaluation.json()
    assert payload["thesis_id"] == thesis_id
    assert payload["token"] == "BTC"
    assert payload["confidence_score"] >= 0
    assert payload["recommendation_state"] in {"watch", "starter", "build", "no_trade"}
    assert "summary" in payload
    assert "rationale" in payload
