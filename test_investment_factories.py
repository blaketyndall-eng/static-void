from fastapi.testclient import TestClient


def create_investment_thesis(
    client: TestClient,
    *,
    asset_class: str = "equity",
    instrument_type: str = "stock",
    ticker: str = "NVDA",
    asset_name: str = "NVIDIA",
    thesis_type: str = "swing_long",
    timeframe: str = "2-6 weeks",
) -> dict:
    response = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": asset_class,
            "instrument_type": instrument_type,
            "ticker": ticker,
            "asset_name": asset_name,
            "thesis_type": thesis_type,
            "timeframe": timeframe,
            "conviction": 0.7,
            "entry_zone": "118-121",
            "target_zone": "132-138",
            "invalidation": "Daily close below 114",
            "recommendation_state": "starter",
            "portfolio_role": "tactical",
            "notes": "Factory thesis",
        },
    )
    response.raise_for_status()
    return response.json()


def create_swing_profile(client: TestClient, thesis_id: str) -> dict:
    response = client.post(
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
    response.raise_for_status()
    return response.json()


def create_options_profile(client: TestClient, thesis_id: str) -> dict:
    response = client.post(
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
    response.raise_for_status()
    return response.json()


def create_crypto_profile(client: TestClient, thesis_id: str) -> dict:
    response = client.post(
        f"/api/v1/investment/theses/{thesis_id}/crypto-profile",
        json={
            "token": "BTC",
            "chain_or_ecosystem": "Bitcoin",
            "narrative": "institutional adoption and ETF demand",
            "exchange_liquidity_score": 0.95,
            "regime_bucket": "risk_on",
        },
    )
    response.raise_for_status()
    return response.json()


def create_prediction_profile(client: TestClient, thesis_id: str) -> dict:
    response = client.post(
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
    response.raise_for_status()
    return response.json()
