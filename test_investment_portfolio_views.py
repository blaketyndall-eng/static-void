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
from app_investment_operator import app
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


def test_investment_portfolio_views_return_roles_risk_flags_and_exposure() -> None:
    reset_state()
    client = TestClient(app)

    tactical = create_investment_thesis(client, ticker="NVDA", thesis_type="swing_long")
    active = create_investment_thesis(
        client,
        asset_class="crypto",
        instrument_type="spot",
        ticker="BTC",
        asset_name="Bitcoin",
        thesis_type="crypto_trend",
        timeframe="2-8 weeks",
    )

    status = client.post(f"/api/v1/investment/theses/{active['id']}/status", json={"status": "active"})
    assert status.status_code == 200

    roles = client.get("/api/v1/investment/portfolio/roles")
    assert roles.status_code == 200
    assert roles.json()["count"] >= 2
    assert "by_role" in roles.json()

    risk_flags = client.get("/api/v1/investment/portfolio/risk-flags")
    assert risk_flags.status_code == 200
    assert "by_flag" in risk_flags.json()
    assert "items" in risk_flags.json()

    exposure = client.get("/api/v1/investment/portfolio/exposure")
    assert exposure.status_code == 200
    payload = exposure.json()
    assert payload["count"] >= 2
    assert "by_asset_class" in payload
    assert "by_recommendation" in payload
    assert "by_timeframe" in payload
