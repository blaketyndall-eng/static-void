from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_packaged import app as backend_app
from app_product_router_packaged import app as product_app
from telemetry_logger import TelemetryLogger


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    telemetry_path = Path("var/product_surface_packaged_telemetry.jsonl")
    if telemetry_path.exists():
        telemetry_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_product_router_emits_observability_events() -> None:
    reset_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    evaluation = backend.post(
        "/api/v1/evaluations",
        json={
            "title": "Telemetry product review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    backend.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Security note",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor supports SSO and SOC 2.",
        },
    )

    backend.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Advance vendor",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Advance to pricing review.",
            "rationale": "Best fit on security and workflow.",
            "status": "proposed",
        },
    )

    assert product.get("/api/v1/decision-board/summary").status_code == 200
    assert product.get("/api/v1/decision-board/attention-needed").status_code == 200
    assert product.get("/api/v1/activity/recent").status_code == 200
    assert product.get(f"/api/v1/evaluations/{evaluation_id}/summary").status_code == 200
    assert product.get(f"/api/v1/evaluations/{evaluation_id}/readiness").status_code == 200
    assert product.get(f"/api/v1/evaluations/{evaluation_id}/recommendation-cards").status_code == 200
    assert product.get(f"/api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary").status_code == 200

    telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")
    events = telemetry.recent(limit=30)
    names = [row.get("event_name") for row in events]
    assert "decision_board.summary_viewed" in names
    assert "decision_board.attention_needed_viewed" in names
    assert "activity.recent_viewed" in names
    assert "evaluation.summary_viewed" in names
    assert "evaluation.readiness_viewed" in names
    assert "recommendation.cards_viewed" in names
    assert "recommendation.ranked" in names
