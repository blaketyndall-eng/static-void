from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from decision_workflow_api import app as workflow_app
from recommendation_ranking_api import app as ranking_app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_ranked_recommendations_orders_best_supported_first() -> None:
    reset_state()
    workflow_client = TestClient(workflow_app)
    ranking_client = TestClient(ranking_app)

    evaluation = workflow_client.post(
        "/api/v1/evaluations",
        json={
            "title": "Ranking review",
            "decision_owner": "blake",
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["id"]

    evidence = workflow_client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": "Security note",
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor supports SSO and SOC 2.",
        },
    )
    assert evidence.status_code == 200
    evidence_id = evidence.json()["id"]

    artifact = workflow_client.post(
        f"/api/v1/evaluations/{evaluation_id}/artifacts",
        json={
            "title": "Comparison brief",
            "artifact_type": "comparison_brief",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "content": "Vendor A remains strongest.",
        },
    )
    assert artifact.status_code == 200
    artifact_id = artifact.json()["id"]

    better = workflow_client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Advance Vendor A",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Proceed with Vendor A.",
            "rationale": "Strongest security and workflow fit with supporting evidence.",
            "status": "proposed",
            "artifact_ids": [artifact_id],
            "evidence_ids": [evidence_id],
        },
    )
    assert better.status_code == 200

    weaker = workflow_client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": "Hold Vendor B",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Keep Vendor B in reserve.",
            "rationale": "Needs more support.",
            "status": "draft",
            "artifact_ids": [],
            "evidence_ids": [],
        },
    )
    assert weaker.status_code == 200

    ranked = ranking_client.get(f"/api/v1/evaluations/{evaluation_id}/ranked-recommendations")
    assert ranked.status_code == 200
    payload = ranked.json()
    assert payload["count"] == 2
    assert payload["recommendations"][0]["title"] == "Advance Vendor A"
    assert payload["recommendations"][0]["rank"] == 1
    assert payload["recommendations"][1]["title"] == "Hold Vendor B"
    assert payload["recommendations"][1]["rank"] == 2
