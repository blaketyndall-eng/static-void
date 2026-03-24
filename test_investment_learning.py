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
from app_investment_learning_operator import app
from test_investment_factories import create_investment_thesis


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


def test_investment_learning_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    thesis_a = create_investment_thesis(client, ticker="NVDA", thesis_type="swing_long")
    thesis_b = create_investment_thesis(
        client,
        asset_class="prediction_market",
        instrument_type="event_contract",
        ticker="FEDCUT_JULY",
        asset_name="Fed cut by July",
        thesis_type="event_probability",
        timeframe="3 months",
    )

    status = client.post(f"/api/v1/investment/theses/{thesis_b['id']}/status", json={"status": "reviewed"})
    assert status.status_code == 200

    review = client.get(f"/api/v1/investment/theses/{thesis_a['id']}/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["thesis_id"] == thesis_a["id"]
    assert review_payload["review_score"] >= 0
    assert "lessons" in review_payload

    summary = client.get("/api/v1/investment/learning/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["total_theses"] >= 2
    assert payload["reviewed_count"] >= 1
    assert "by_outcome" in payload
    assert "recurring_lessons" in payload
