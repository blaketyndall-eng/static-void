from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_brain_links import BrainLinkRecordORM
from app_system_console import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/brain_links_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    BrainLinkRecordORM.metadata.create_all(bind=db_session.engine)


def test_brain_links_create_list_source_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/brain-links",
        json={
            "source_arm": "marketing",
            "source_id": "mkt_123",
            "target_type": "marketing_to_module",
            "target_id": "memory",
            "notes": "Marketing project uses memory module.",
        },
    )
    assert created.status_code == 200
    assert created.json()["source_arm"] == "marketing"

    listed = client.get("/api/v1/brain-links")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    source = client.get("/api/v1/brain-links/source/marketing/mkt_123")
    assert source.status_code == 200
    assert source.json()["count"] == 1

    summary = client.get("/api/v1/brain-links/modules/summary")
    assert summary.status_code == 200
    assert summary.json()["count"] >= 1
