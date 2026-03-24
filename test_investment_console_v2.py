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
from app_investment_console_v2 import app
from test_investment_factories import create_investment_thesis, create_prediction_profile, create_swing_profile


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


def test_console_summary_and_operator_run_v2() -> None:
    reset_state()
    client = TestClient(app)

    swing_thesis = create_investment_thesis(client, ticker="NVDA", thesis_type="swing_long")
    create_swing_profile(client, swing_thesis["id"])

    prediction_thesis = create_investment_thesis(
        client,
        asset_class="prediction_market",
        instrument_type="event_contract",
        ticker="FEDCUT_JULY",
        asset_name="Fed cut by July",
        thesis_type="event_probability",
        timeframe="3 months",
    )
    create_prediction_profile(client, prediction_thesis["id"])

    operator_v2 = client.get(f"/api/v1/investment/theses/{prediction_thesis['id']}/operator-run-v2")
    assert operator_v2.status_code == 200
    operator_payload = operator_v2.json()
    assert operator_payload["thesis_id"] == prediction_thesis["id"]
    assert "portfolio_snapshot" in operator_payload
    assert "debate_packet" in operator_payload
    assert "risk_review" in operator_payload
    assert "allocation_decision" in operator_payload

    console = client.get("/api/v1/investment/console/summary")
    assert console.status_code == 200
    payload = console.json()
    assert payload["total_theses"] >= 2
    assert "portfolio_snapshot" in payload
    assert "learning_summary" in payload
    assert "watchlist" in payload
    assert "catalysts" in payload
