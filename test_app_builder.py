from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from app_app_builder import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/app_builder_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    AppBlueprintORM.metadata.create_all(bind=db_session.engine)
    AppScaffoldPlanORM.metadata.create_all(bind=db_session.engine)


def test_persistent_app_builder_blueprints_and_scaffold_plan() -> None:
    reset_state()
    client = TestClient(app)

    created = client.post(
        "/api/v1/app-builder/persistent-blueprints",
        json={
            "name": "Vendor Evidence Console",
            "app_type": "operator_console",
            "description": "Runs vendor evidence workflows.",
            "target_users": ["operators", "analysts"],
            "workflows": ["intake", "evaluation", "summary"],
            "required_engines": ["evidence", "ranking"],
            "primary_views": ["dashboard", "review_queue"],
            "data_sources": ["sec", "news", "internal"],
            "notes": "High-priority blueprint.",
        },
    )
    assert created.status_code == 200
    blueprint_id = created.json()["id"]

    listed = client.get("/api/v1/app-builder/persistent-blueprints")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/app-builder/persistent-blueprints/{blueprint_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == blueprint_id

    plan = client.post(
        f"/api/v1/app-builder/persistent-blueprints/{blueprint_id}/scaffold-plan",
        json={
            "include_observability": True,
            "include_tests": True,
            "include_runtime_apps": True,
            "tech_debt_items": ["Add deeper template specialization"],
        },
    )
    assert plan.status_code == 200
    assert len(plan.json()["generated_files"]) > 0

    plan_get = client.get(f"/api/v1/app-builder/persistent-blueprints/{blueprint_id}/scaffold-plan")
    assert plan_get.status_code == 200
    assert plan_get.json()["blueprint_id"] == blueprint_id
