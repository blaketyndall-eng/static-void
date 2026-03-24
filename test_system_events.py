from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_system_events import SystemEventRecordORM
from app_system_console_v4 import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/system_events_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_system_events_create_list_and_source_filters() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/system-events",
        json={
            "event_type": "app_created",
            "source_arm": "apps",
            "source_id": "app_123",
            "summary": "Created operator app",
            "metadata": {"owner": "blake"},
        },
    )
    assert created.status_code == 200
    assert created.json()["event_type"] == "app_created"

    listed = client.get("/api/v1/system-events")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    source = client.get("/api/v1/system-events/source/apps/app_123")
    assert source.status_code == 200
    assert source.json()["count"] == 1
    assert source.json()["items"][0]["source_arm"] == "apps"
