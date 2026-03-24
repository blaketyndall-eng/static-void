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
from app_investment_decision_console import app
from test_investment_factories import (
    create_crypto_profile,
    create_investment_thesis,
    create_options_profile,
    create_prediction_profile,
    create_swing_profile,
)


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


def test_investment_operator_run_for_swing_and_prediction() -> None:
    reset_state()
    client = TestClient(app)

    swing_thesis = create_investment_thesis(client, ticker="NVDA", thesis_type="swing_long")
    create_swing_profile(client, swing_thesis["id"])

    swing_run = client.get(f"/api/v1/investment/theses/{swing_thesis['id']}/operator-run")
    assert swing_run.status_code == 200
    swing_payload = swing_run.json()
    assert swing_payload["thesis_id"] == swing_thesis["id"]
    assert "debate_packet" in swing_payload
    assert "risk_review" in swing_payload
    assert "allocation_decision" in swing_payload

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

    prediction_run = client.get(f"/api/v1/investment/theses/{prediction_thesis['id']}/operator-run")
    assert prediction_run.status_code == 200
    prediction_payload = prediction_run.json()
    assert prediction_payload["thesis_id"] == prediction_thesis["id"]
    assert prediction_payload["risk_review"]["decision"] in {"approve", "watch_only", "reject"}
    assert prediction_payload["allocation_decision"]["target_action"] in {"enter_or_add", "watch_only", "reject"}
