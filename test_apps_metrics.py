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
from app_operator_console_v2 import app


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


def test_apps_metrics_and_health_flows() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/apps",
        json={
            "name": "App Builder",
            "app_type": "workflow_app",
            "owner": "blake",
            "description": "Builds decision intelligence apps.",
            "version": "0.1.0",
            "runtime_url": "https://local/app-builder",
            "tags": ["builder"],
            "linked_brain_modules": ["memory", "routing"],
        },
    )
    assert created.status_code == 200
    app_id = created.json()["id"]

    analytics = client.post(
        f"/api/v1/apps/{app_id}/analytics",
        json={
            "sessions": 120,
            "active_users": 12,
            "completions": 80,
            "failures": 4,
            "outcome_quality_score": 78.5,
            "latency_ms": 420.0,
            "model_cost_estimate": 14.25,
        },
    )
    assert analytics.status_code == 200
    assert analytics.json()["sessions"] == 120

    analytics_get = client.get(f"/api/v1/apps/{app_id}/analytics")
    assert analytics_get.status_code == 200
    assert analytics_get.json()["active_users"] == 12

    health = client.post(
        f"/api/v1/apps/{app_id}/health",
        json={
            "healthy": False,
            "error_count": 2,
            "warning_count": 3,
            "notes": ["Queue lag spike", "One failed deployment"],
        },
    )
    assert health.status_code == 200
    assert health.json()["healthy"] is False

    health_get = client.get(f"/api/v1/apps/{app_id}/health")
    assert health_get.status_code == 200
    assert health_get.json()["warning_count"] == 3
