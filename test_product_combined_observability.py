from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_full import app as backend_app
from app_product_router_full import app as product_app
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


def test_product_combined_view_emits_observability_events() -> None:
    reset_state()
    backend = TestClient(backend_app)
    product = TestClient(product_app)

    backend.post(
        "/api/v1/sources",
        json={
            "name": "G2",
            "source_type": "website",
            "trust_score": 0.8,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )
    backend.post(
        "/api/v1/opportunities",
        json={
            "title": "Combined telemetry opportunity",
            "summary": "Track vendor signals for evaluations.",
            "themes": ["signals"],
            "score": 81,
        },
    )
    evaluation = backend.post(
        "/api/v1/evaluations",
        json={
            "title": "Combined telemetry evaluation",
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

    combined = product.get("/api/v1/decision-board/combined")
    assert combined.status_code == 200

    telemetry = TelemetryLogger(filepath="var/product_surface_packaged_telemetry.jsonl")
    events = telemetry.recent(limit=20)
    names = [row.get("event_name") for row in events]
    assert "decision_board.summary_viewed" in names
