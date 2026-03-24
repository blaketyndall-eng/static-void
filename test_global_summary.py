from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_brain_links import BrainLinkRecordORM
from packages.storage.orm_opportunity_hunter import OpportunityCandidateORM, OpportunityMarketSignalORM, OpportunityScanORM
from packages.storage.orm_system_events import SystemEventRecordORM
from app_system_console_v4 import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    for path in [Path("var/system_events_telemetry.jsonl"), Path("var/brain_links_telemetry.jsonl"), Path("var/opportunity_hunter_telemetry.jsonl")]:
        if path.exists():
            path.unlink()
    BrainLinkRecordORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)
    OpportunityScanORM.metadata.create_all(bind=db_session.engine)
    OpportunityCandidateORM.metadata.create_all(bind=db_session.engine)
    OpportunityMarketSignalORM.metadata.create_all(bind=db_session.engine)


def test_global_summary_returns_brain_links_events_and_opportunities() -> None:
    reset_state()
    client = TestClient(app)

    link = client.post(
        "/api/v1/brain-links",
        json={
            "source_arm": "apps",
            "source_id": "app_1",
            "target_type": "app_to_module",
            "target_id": "memory",
            "notes": "App uses memory",
        },
    )
    assert link.status_code == 200

    event = client.post(
        "/api/v1/system-events",
        json={
            "event_type": "app_created",
            "source_arm": "apps",
            "source_id": "app_1",
            "summary": "Created app",
            "metadata": {"kind": "operator_console"},
        },
    )
    assert event.status_code == 200

    scan = client.post(
        "/api/v1/opportunities/scans",
        json={
            "name": "Global Sweep",
            "focus": "Find opportunities",
            "source_arms": ["apps"],
            "source_queries": ["automation"],
            "notes": "seed",
        },
    )
    assert scan.status_code == 200
    scan_id = scan.json()["id"]

    candidate = client.post(
        f"/api/v1/opportunities/scans/{scan_id}/candidates",
        json={
            "title": "Workflow Wedge",
            "opportunity_type": "workflow_gap",
            "summary": "Fill workflow gap",
            "target_users": ["ops"],
            "related_apps": ["app_1"],
            "related_industries": ["ops"],
            "evidence_notes": [{"source": "seed", "note": "manual process"}],
            "demand_score": 60,
            "competition_score": 40,
            "whitespace_score": 70,
            "priority_score": 68,
        },
    )
    assert candidate.status_code == 200

    summary = client.get("/api/v1/global/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["brain_links"]["count"] >= 1
    assert payload["system_events"]["count"] >= 1
    assert payload["opportunity_hunter"]["scan_count"] >= 1
    assert payload["opportunity_hunter"]["candidate_count"] >= 1
