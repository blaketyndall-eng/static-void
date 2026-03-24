from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_marketing import (
    ContentAssetORM,
    MarketingAnalyticsSnapshotORM,
    MarketingProjectORM,
    MarketingResearchRecordORM,
)
from app_marketing_v2 import app


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


def test_marketing_hub_project_research_content_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    project = client.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Q2 Demand Engine",
            "project_type": "campaign",
            "owner": "blake",
            "description": "Run marketing research and execution for Q2.",
            "audience": ["sales leaders"],
            "channels": ["email", "landing_page", "social"],
            "goals": ["pipeline", "engagement"],
            "linked_apps": ["app_console"],
            "linked_brain_modules": ["memory", "evidence"],
        },
    )
    assert project.status_code == 200
    project_id = project.json()["id"]

    research = client.post(
        f"/api/v1/marketing/projects/{project_id}/research",
        json={
            "market_summary": "Demand for proposal automation remains strong.",
            "competitor_summary": "Main alternatives push speed and collaboration.",
            "audience_insights": ["Buyers want proof", "Leaders care about time savings"],
            "channel_insights": ["Email works for warm segments", "LinkedIn supports awareness"],
            "source_notes": [{"source": "official_docs", "note": "validated positioning"}],
            "opportunity_score": 78.0,
        },
    )
    assert research.status_code == 200

    research_eval = client.get(f"/api/v1/marketing/projects/{project_id}/research-evaluation")
    assert research_eval.status_code == 200
    assert research_eval.json()["confidence_score"] >= 0

    asset = client.post(
        f"/api/v1/marketing/projects/{project_id}/content-assets",
        json={
            "asset_type": "landing_page",
            "title": "Why Qvidian Now",
            "status": "draft",
            "target_channel": "landing_page",
            "source_brief": "Show value, proof, and workflow benefits.",
            "generated_outline": ["Hero", "Pain", "Proof", "CTA"],
            "body": "Teams need stronger evidence and faster execution.",
            "call_to_action": "Book a strategy session.",
        },
    )
    assert asset.status_code == 200

    content_eval = client.get(f"/api/v1/marketing/projects/{project_id}/content-evaluation")
    assert content_eval.status_code == 200
    assert content_eval.json()["confidence_score"] >= 0

    analytics = client.post(
        f"/api/v1/marketing/projects/{project_id}/analytics",
        json={
            "impressions": 1000,
            "clicks": 120,
            "conversions": 15,
            "engagement_rate": 0.12,
            "content_velocity": 4,
            "quality_score": 81.0,
        },
    )
    assert analytics.status_code == 200

    summary = client.get("/api/v1/marketing/summary")
    assert summary.status_code == 200
    assert summary.json()["count"] == 1

    operator_summary = client.get(f"/api/v1/marketing/projects/{project_id}/operator-summary")
    assert operator_summary.status_code == 200
    payload = operator_summary.json()
    assert payload["project"]["id"] == project_id
    assert payload["content_count"] == 1

    tools = client.get("/api/v1/marketing/tools")
    assert tools.status_code == 200
    assert "frontend" in tools.json()
