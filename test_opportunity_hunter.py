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
from app_operator_console_v2 import app as operator_app
from app_marketing_console_v3 import app as marketing_app
from app_opportunity_hunter import app as opportunity_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    for path in [
        Path("var/opportunity_hunter_telemetry.jsonl"),
        Path("var/apps_telemetry.jsonl"),
        Path("var/marketing_telemetry.jsonl"),
    ]:
        if path.exists():
            path.unlink()
    OpportunityScanORM.metadata.create_all(bind=db_session.engine)
    OpportunityCandidateORM.metadata.create_all(bind=db_session.engine)
    OpportunityMarketSignalORM.metadata.create_all(bind=db_session.engine)
    AppRecordORM.metadata.create_all(bind=db_session.engine)
    AppRunORM.metadata.create_all(bind=db_session.engine)
    AppAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppHealthCheckORM.metadata.create_all(bind=db_session.engine)
    AppFeedbackItemORM.metadata.create_all(bind=db_session.engine)
    MarketingProjectORM.metadata.create_all(bind=db_session.engine)
    MarketingResearchRecordORM.metadata.create_all(bind=db_session.engine)
    ContentAssetORM.metadata.create_all(bind=db_session.engine)
    MarketingAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)


def test_opportunity_hunter_scan_candidates_signals_and_summaries() -> None:
    reset_state()
    operator = TestClient(operator_app)
    marketing = TestClient(marketing_app)
    hunter = TestClient(opportunity_app)

    created_app = operator.post(
        "/api/v1/apps",
        json={
            "name": "Decision Ops Console",
            "app_type": "operator_console",
            "owner": "blake",
            "description": "Runs internal ops workflows.",
            "version": "0.1.0",
            "runtime_url": "https://local/decision-ops",
            "tags": ["ops", "analytics"],
            "linked_brain_modules": ["memory", "learning"],
        },
    )
    assert created_app.status_code == 200

    project = marketing.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Pipeline Campaign",
            "project_type": "campaign",
            "owner": "blake",
            "description": "Campaign for new demand generation.",
            "audience": ["sales leaders"],
            "channels": ["email", "social"],
            "goals": ["pipeline"],
            "linked_apps": [],
            "linked_brain_modules": ["memory"],
        },
    )
    assert project.status_code == 200

    scan = hunter.post(
        "/api/v1/opportunities/scans",
        json={
            "name": "Q3 Opportunity Sweep",
            "focus": "Find app-adjacent, niche, and underserved opportunities.",
            "source_arms": ["apps", "marketing"],
            "source_queries": ["proposal ops", "sales enablement", "campaign analytics"],
            "notes": "Initial sweep.",
        },
    )
    assert scan.status_code == 200
    scan_id = scan.json()["id"]

    app_scan = hunter.post(f"/api/v1/opportunities/scans/{scan_id}/scan-active-apps")
    assert app_scan.status_code == 200
    assert app_scan.json()["count"] >= 1

    marketing_scan = hunter.post(f"/api/v1/opportunities/scans/{scan_id}/scan-marketing-adjacencies")
    assert marketing_scan.status_code == 200
    assert marketing_scan.json()["count"] >= 1

    niche_scan = hunter.post(f"/api/v1/opportunities/scans/{scan_id}/scan-niches?terms=proposal automation,revops niche")
    assert niche_scan.status_code == 200
    assert niche_scan.json()["count"] >= 1

    candidates = hunter.get(f"/api/v1/opportunities/scans/{scan_id}/candidates")
    assert candidates.status_code == 200
    payload = candidates.json()
    assert payload["count"] >= 3
    candidate_id = payload["items"][0]["id"]

    signal = hunter.post(
        f"/api/v1/opportunities/candidates/{candidate_id}/signals",
        json={
            "trend_signal": "Interest rising in workflow automation.",
            "labor_signal": "Team strain suggests demand for leverage.",
            "industry_signal": "Mid-market segment appears fragmented.",
            "research_signal": "Search and research signals support deeper validation.",
            "source_stack": ["Google Trends", "BLS API", "FRED API"],
        },
    )
    assert signal.status_code == 200

    evaluation = hunter.get(f"/api/v1/opportunities/candidates/{candidate_id}/evaluation")
    assert evaluation.status_code == 200
    assert evaluation.json()["priority_score"] >= 0

    summary = hunter.get(f"/api/v1/opportunities/scans/{scan_id}/summary")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["candidate_count"] >= 3
    assert "source_stack" in summary_payload

    source_stack = hunter.get("/api/v1/opportunities/source-stack")
    assert source_stack.status_code == 200
    assert "trend_research" in source_stack.json()
