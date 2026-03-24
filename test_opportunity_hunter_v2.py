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
from packages.storage.orm_brain_links import BrainLinkRecordORM
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
from app_system_console_v4 import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    for path in [
        Path("var/apps_telemetry.jsonl"),
        Path("var/marketing_telemetry.jsonl"),
        Path("var/opportunity_hunter_telemetry.jsonl"),
        Path("var/brain_links_telemetry.jsonl"),
    ]:
        if path.exists():
            path.unlink()
    AppRecordORM.metadata.create_all(bind=db_session.engine)
    AppRunORM.metadata.create_all(bind=db_session.engine)
    AppAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppHealthCheckORM.metadata.create_all(bind=db_session.engine)
    AppFeedbackItemORM.metadata.create_all(bind=db_session.engine)
    MarketingProjectORM.metadata.create_all(bind=db_session.engine)
    MarketingResearchRecordORM.metadata.create_all(bind=db_session.engine)
    ContentAssetORM.metadata.create_all(bind=db_session.engine)
    MarketingAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    BrainLinkRecordORM.metadata.create_all(bind=db_session.engine)
    OpportunityScanORM.metadata.create_all(bind=db_session.engine)
    OpportunityCandidateORM.metadata.create_all(bind=db_session.engine)
    OpportunityMarketSignalORM.metadata.create_all(bind=db_session.engine)


def test_auto_scan_v2_uses_brain_links_and_creates_candidates() -> None:
    reset_state()
    client = TestClient(app)

    app_resp = client.post(
        "/api/v1/apps",
        json={
            "name": "Ops Console",
            "app_type": "operator_console",
            "owner": "blake",
            "description": "Runs ops workflows.",
            "version": "0.1.0",
            "runtime_url": "https://local/ops",
            "tags": ["ops", "analytics"],
            "linked_brain_modules": ["memory"],
        },
    )
    assert app_resp.status_code == 200

    project_resp = client.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Growth Campaign",
            "project_type": "campaign",
            "owner": "blake",
            "description": "Campaign for buyers.",
            "audience": ["sales leaders"],
            "channels": ["email", "social"],
            "goals": ["pipeline"],
            "linked_apps": [],
            "linked_brain_modules": ["memory"],
        },
    )
    assert project_resp.status_code == 200

    link_resp = client.post(
        "/api/v1/brain-links",
        json={
            "source_arm": "marketing",
            "source_id": project_resp.json()["id"],
            "target_type": "marketing_to_module",
            "target_id": "memory",
            "notes": "Marketing uses memory",
        },
    )
    assert link_resp.status_code == 200

    auto_scan = client.post("/api/v1/opportunities/auto-scan-v2")
    assert auto_scan.status_code == 200
    payload = auto_scan.json()
    assert payload["brain_link_count"] >= 1
    assert payload["count"] >= 1
    assert len(payload["items"]) >= 1
