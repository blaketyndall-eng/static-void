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
from app_investment_router import app


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


def test_investment_router_thesis_and_profiles() -> None:
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
        },
    )
    assert thesis.status_code == 200
    thesis_id = thesis.json()["id"]

    fetched = client.get(f"/api/v1/investment/theses/{thesis_id}")
    assert fetched.status_code == 200
    assert fetched.json()["ticker"] == "NVDA"

    status = client.post(
        f"/api/v1/investment/theses/{thesis_id}/status",
        json={"status": "active"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "active"

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
    assert swing.json()["setup_type"] == "breakout_continuation"

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
    assert options.json()["structure_type"] == "call_vertical"

    crypto = client.post(
        f"/api/v1/investment/theses/{thesis_id}/crypto-profile",
        json={
            "token": "BTC",
            "chain_or_ecosystem": "Bitcoin",
            "narrative": "institutional adoption",
            "exchange_liquidity_score": 0.95,
            "regime_bucket": "risk_on",
        },
    )
    assert crypto.status_code == 200
    assert crypto.json()["token"] == "BTC"

    prediction = client.post(
        f"/api/v1/investment/theses/{thesis_id}/prediction-profile",
        json={
            "market_venue": "Kalshi",
            "contract_text": "Will the Fed cut rates by July?",
            "settlement_rule_summary": "Resolves yes if official target rate lower by July meeting",
            "implied_probability": 0.41,
            "estimated_probability": 0.49,
            "edge": 0.08,
            "max_stake": 500,
            "ambiguity_score": 0.12,
        },
    )
    assert prediction.status_code == 200
    assert prediction.json()["market_venue"] == "Kalshi"
