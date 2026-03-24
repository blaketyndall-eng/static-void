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
from app_investment_analyst import app
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


def test_investment_views_return_watchlist_active_catalysts_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    watch = create_investment_thesis(client, ticker="NVDA", thesis_type="swing_long")
    active = create_investment_thesis(client, asset_class="crypto", instrument_type="spot", ticker="BTC", asset_name="Bitcoin", thesis_type="crypto_trend")
    status = client.post(f"/api/v1/investment/theses/{active['id']}/status", json={"status": "active"})
    assert status.status_code == 200

    watchlist = client.get("/api/v1/investment/watchlist")
    assert watchlist.status_code == 200
    assert watchlist.json()["count"] >= 1

    active_resp = client.get("/api/v1/investment/active")
    assert active_resp.status_code == 200
    assert active_resp.json()["count"] >= 1

    catalysts = client.get("/api/v1/investment/catalysts")
    assert catalysts.status_code == 200
    assert "items" in catalysts.json()

    summary = client.get("/api/v1/investment/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["count"] >= 2
    assert "by_asset_class" in payload
    assert "by_status" in payload
    assert "by_recommendation" in payload
