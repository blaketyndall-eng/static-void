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
from app_operator_console import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/apps_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    AppRecordORM.metadata.create_all(bind=db_session.engine)
    AppRunORM.metadata.create_all(bind=db_session.engine)
    AppAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppHealthCheckORM.metadata.create_all(bind=db_session.engine)
    AppFeedbackItemORM.metadata.create_all(bind=db_session.engine)


def test_apps_router_and_summary_views() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/apps",
        json={
            "name": "Investment Console",
            "app_type": "operator_console",
            "owner": "blake",
            "description": "Runs investment decision workflows.",
            "version": "0.1.0",
            "runtime_url": "https://local/investment-console",
            "tags": ["investment", "console"],
            "linked_brain_modules": ["memory", "evidence", "learning"],
        },
    )
    assert created.status_code == 200
    app_id = created.json()["id"]

    listed = client.get("/api/v1/apps")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/apps/{app_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == app_id

    status = client.post(f"/api/v1/apps/{app_id}/status", json={"status": "active"})
    assert status.status_code == 200
    assert status.json()["status"] == "active"

    deployment = client.post(f"/api/v1/apps/{app_id}/deployment", json={"deployment_state": "staging"})
    assert deployment.status_code == 200
    assert deployment.json()["deployment_state"] == "staging"

    run = client.post(f"/api/v1/apps/{app_id}/runs", json={"output_summary": "Run completed", "error_summary": ""})
    assert run.status_code == 200

    feedback = client.post(
        f"/api/v1/apps/{app_id}/feedback",
        json={"category": "ux", "severity": "warning", "message": "Users abandon step 2."},
    )
    assert feedback.status_code == 200

    summary = client.get("/api/v1/apps/summary")
    assert summary.status_code == 200
    assert summary.json()["count"] == 1
    assert "by_type" in summary.json()

    operator_summary = client.get(f"/api/v1/apps/{app_id}/operator-summary")
    assert operator_summary.status_code == 200
    payload = operator_summary.json()
    assert payload["app"]["id"] == app_id
    assert payload["run_count"] == 1
    assert payload["feedback_count"] == 1
    assert payload["open_feedback_count"] == 1
