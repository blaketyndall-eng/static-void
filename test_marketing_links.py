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
from app_marketing_console_v3 import app as marketing_app
from app_operator_console_v2 import app as operator_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    for path in [Path("var/marketing_telemetry.jsonl"), Path("var/apps_telemetry.jsonl")]:
        if path.exists():
            path.unlink()
    MarketingProjectORM.metadata.create_all(bind=db_session.engine)
    MarketingResearchRecordORM.metadata.create_all(bind=db_session.engine)
    ContentAssetORM.metadata.create_all(bind=db_session.engine)
    MarketingAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppRecordORM.metadata.create_all(bind=db_session.engine)
    AppRunORM.metadata.create_all(bind=db_session.engine)
    AppAnalyticsSnapshotORM.metadata.create_all(bind=db_session.engine)
    AppHealthCheckORM.metadata.create_all(bind=db_session.engine)
    AppFeedbackItemORM.metadata.create_all(bind=db_session.engine)


def test_marketing_project_can_link_and_view_operator_apps() -> None:
    reset_state()
    operator = TestClient(operator_app)
    marketing = TestClient(marketing_app)

    created_app = operator.post(
        "/api/v1/apps",
        json={
            "name": "Marketing Ops Console",
            "app_type": "operator_console",
            "owner": "blake",
            "description": "Runs marketing execution analytics.",
            "version": "0.1.0",
            "runtime_url": "https://local/marketing-ops",
            "tags": ["marketing", "ops"],
            "linked_brain_modules": ["memory", "learning"],
        },
    )
    assert created_app.status_code == 200
    app_id = created_app.json()["id"]

    project = marketing.post(
        "/api/v1/marketing/projects",
        json={
            "name": "Launch Research Hub",
            "project_type": "launch",
            "owner": "blake",
            "description": "Coordinates launch messaging.",
            "audience": ["operators", "buyers"],
            "channels": ["email", "social"],
            "goals": ["awareness"],
            "linked_apps": [],
            "linked_brain_modules": ["memory"],
        },
    )
    assert project.status_code == 200
    project_id = project.json()["id"]

    linked = marketing.post(f"/api/v1/marketing/projects/{project_id}/link-app-v2/{app_id}")
    assert linked.status_code == 200
    assert app_id in linked.json()["linked_apps"]

    linked_apps = marketing.get(f"/api/v1/marketing/projects/{project_id}/linked-apps-v2")
    assert linked_apps.status_code == 200
    payload = linked_apps.json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == app_id
