from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_apps import (
    AppAnalyticsSnapshotORM,
    AppFeedbackItemORM,
    AppHealthCheckORM,
    AppRecordORM,
    AppRunORM,
)
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from packages.storage.orm_marketing import (
    ContentAssetORM,
    MarketingAnalyticsSnapshotORM,
    MarketingProjectORM,
    MarketingResearchRecordORM,
)
from packages.storage.orm_opportunity_hunter import (
    OpportunityCandidateORM,
    OpportunityMarketSignalORM,
    OpportunityScanORM,
)
from packages.storage.orm_investment import (
    CryptoProfileORM,
    InvestmentThesisORM,
    OptionsProfileORM,
    PredictionMarketProfileORM,
    SwingTradeProfileORM,
)
from app_system_console import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/master_console_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    AppRecordORM.metadata.create_all(bind=db_session.engine)
    AppRunORM.metadata.create_all(bind=db_session.engine)
    AppAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppHealthCheckORM.metadata.create_all(bind=db_session.engine)
    AppFeedbackItemORM.metadata.create_all(bind=db_session.engine)
    AppBlueprintORM.metadata.create_all(bind=db_session.engine)
    AppScaffoldPlanORM.metadata.create_all(bind=db_session.engine)
    MarketingProjectORM.metadata.create_all(bind=db_session.engine)
    MarketingResearchRecordORM.metadata.create_all(bind=db_session.engine)
    ContentAssetORM.metadata.create_all(bind=db_session.engine)
    MarketingAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    OpportunityScanORM.metadata.create_all(bind=db_session.engine)
    OpportunityCandidateORM.metadata.create_all(bind=db_session.engine)
    OpportunityMarketSignalORM.metadata.create_all(bind=db_session.engine)
    InvestmentThesisORM.metadata.create_all(bind=db_session.engine)
    SwingTradeProfileORM.metadata.create_all(bind=db_session.engine)
    OptionsProfileORM.metadata.create_all(bind=db_session.engine)
    CryptoProfileORM.metadata.create_all(bind=db_session.engine)
    PredictionMarketProfileORM.metadata.create_all(bind=db_session.engine)


def test_master_console_summary_returns_counts_across_arms() -> None:
    reset_state()
    client = TestClient(app)

    app_resp = client.post(
        "/api/v1/apps",
        json={
            "name": "Ops Console",
            "app_type": "operator_console",
            "owner": "blake",
            "description": "Runs ops.",
            "version": "0.1.0",
            "runtime_url": "https://local/ops",
            "tags": ["ops"],
            "linked_brain_modules": ["memory"],
        },
    )
    assert app_resp.status_code == 200

    blueprint_resp = client.post(
        "/api/v1/app-builder/persistent-blueprints",
        json={
            "name": "Marketing Builder",
            "app_type": "operator_console",
            "description": "Build marketing workflows.",
            "target_users": ["operators"],
            "workflows": ["research", "content"],
            "required_engines": ["analytics"],
            "primary_views": ["dashboard"],
            "data_sources": ["internal"],
            "notes": "seed",
        },
    )
    assert blueprint_resp.status_code == 200

    marketing_resp = client.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Growth Campaign",
            "project_type": "campaign",
            "owner": "blake",
            "description": "Marketing push.",
            "audience": ["buyers"],
            "channels": ["email"],
            "goals": ["pipeline"],
            "linked_apps": [],
            "linked_brain_modules": ["memory"],
        },
    )
    assert marketing_resp.status_code == 200

    opp_scan = client.post(
        "/api/v1/opportunities/scans",
        json={
            "name": "Sweep",
            "focus": "Find opportunities.",
            "source_arms": ["apps", "marketing"],
            "source_queries": ["automation"],
            "notes": "seed",
        },
    )
    assert opp_scan.status_code == 200

    inv_resp = client.post(
        "/api/v1/investment/theses",
        json={
            "asset_class": "equity",
            "instrument_type": "stock",
            "ticker": "NVDA",
            "asset_name": "NVIDIA",
            "thesis_type": "swing_long",
            "timeframe": "2-6 weeks",
            "conviction": 0.7,
            "entry_zone": "118-121",
            "target_zone": "132-138",
            "invalidation": "Below 114",
            "recommendation_state": "starter",
            "portfolio_role": "tactical",
            "notes": "seed",
        },
    )
    assert inv_resp.status_code == 200

    summary = client.get("/api/v1/master-console/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["apps"]["count"] >= 1
    assert payload["app_builder"]["count"] >= 1
    assert payload["marketing"]["count"] >= 1
    assert payload["opportunity_hunter"]["scan_count"] >= 1
    assert payload["investment"]["count"] >= 1
