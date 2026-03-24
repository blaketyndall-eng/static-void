from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from app_app_builder_v2 import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/app_builder_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    AppBlueprintORM.metadata.create_all(bind=db_session.engine)
    AppScaffoldPlanORM.metadata.create_all(bind=db_session.engine)


def test_template_aware_blueprint_and_scaffold_plan_v2() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/app-builder/blueprints-v2",
        json={
            "name": "Decision Ops Dashboard",
            "app_type": "operator_console",
            "description": "Runs app ops and analytics workflows.",
            "target_users": ["operators"],
            "workflows": ["monitor", "triage", "summary"],
            "required_engines": ["analytics", "alerts"],
            "primary_views": ["dashboard", "health"],
            "data_sources": ["internal"],
            "notes": "Template-aware build.",
        },
    )
    assert created.status_code == 200
    blueprint_id = created.json()["id"]

    plan = client.post(
        f"/api/v1/app-builder/blueprints-v2/{blueprint_id}/scaffold-plan",
        json={
            "include_observability": True,
            "include_tests": True,
            "include_runtime_apps": True,
            "tech_debt_items": ["Add more dashboard widgets"],
        },
    )
    assert plan.status_code == 200
    payload = plan.json()
    assert payload["blueprint_id"] == blueprint_id
    assert len(payload["generated_files"]) > 0
    assert any("analytics" in item or "health" in item for item in payload["generated_files"])

    plan_get = client.get(f"/api/v1/app-builder/blueprints-v2/{blueprint_id}/scaffold-plan")
    assert plan_get.status_code == 200
    assert plan_get.json()["blueprint_id"] == blueprint_id
