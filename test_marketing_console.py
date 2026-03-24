from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_marketing import (
    ContentAssetORM,
    MarketingAnalyticsSnapshotORM,
    MarketingProjectORM,
    MarketingResearchRecordORM,
)
from app_marketing_console_v2 import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/marketing_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    MarketingProjectORM.metadata.create_all(bind=db_session.engine)
    MarketingResearchRecordORM.metadata.create_all(bind=db_session.engine)
    ContentAssetORM.metadata.create_all(bind=db_session.engine)
    MarketingAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)


def test_marketing_console_review_learning_operator_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    project = client.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Q3 Content Engine",
            "project_type": "content_system",
            "owner": "blake",
            "description": "Run content and research engine.",
            "audience": ["sales leaders"],
            "channels": ["email", "landing_page"],
            "goals": ["pipeline"],
            "linked_apps": ["app_builder"],
            "linked_brain_modules": ["memory", "learning"],
        },
    )
    assert project.status_code == 200
    project_id = project.json()["id"]

    research = client.post(
        f"/api/v1/marketing/projects/{project_id}/research",
        json={
            "market_summary": "Proposal automation demand remains strong.",
            "competitor_summary": "Competitors emphasize collaboration and speed.",
            "audience_insights": ["Need proof", "Need time savings"],
            "channel_insights": ["Email converts warm traffic"],
            "source_notes": [{"source": "notes", "note": "validated"}],
            "opportunity_score": 76.0,
        },
    )
    assert research.status_code == 200

    asset = client.post(
        f"/api/v1/marketing/projects/{project_id}/content-assets",
        json={
            "asset_type": "email",
            "title": "Why Decision Evidence Wins",
            "status": "draft",
            "target_channel": "email",
            "source_brief": "Focus on proof, speed, and clarity.",
            "generated_outline": ["Hook", "Pain", "Proof", "CTA"],
            "body": "Evidence-first buying improves outcomes.",
            "call_to_action": "Book a working session.",
        },
    )
    assert asset.status_code == 200

    analytics = client.post(
        f"/api/v1/marketing/projects/{project_id}/analytics",
        json={
            "impressions": 500,
            "clicks": 55,
            "conversions": 6,
            "engagement_rate": 0.11,
            "content_velocity": 2,
            "quality_score": 73.0,
        },
    )
    assert analytics.status_code == 200

    review = client.get(f"/api/v1/marketing/projects/{project_id}/review")
    assert review.status_code == 200
    assert review.json()["review_score"] >= 0

    operator = client.get(f"/api/v1/marketing/projects/{project_id}/operator-run")
    assert operator.status_code == 200
    operator_payload = operator.json()
    assert operator_payload["project_id"] == project_id
    assert "debate" in operator_payload
    assert "risk_review" in operator_payload
    assert "action_plan" in operator_payload

    learning = client.get("/api/v1/marketing/learning/summary")
    assert learning.status_code == 200
    assert learning.json()["total_projects"] >= 1

    summary = client.get("/api/v1/marketing/console-summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["total_projects"] >= 1
    assert "learning_summary" in payload
    assert "operator_notes" in payload
