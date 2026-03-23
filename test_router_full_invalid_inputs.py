from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM
from app_backend_router_full import app


def reset_state() -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()
    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)


def test_router_full_invalid_inputs_and_missing_records() -> None:
    reset_state()
    client = TestClient(app)

    bad_source = client.post(
        "/api/v1/sources",
        json={"name": "Bad", "source_type": "not_real"},
    )
    assert bad_source.status_code == 400
    assert bad_source.json()["detail"] == "invalid source_type"

    bad_stage = client.post("/api/v1/opportunities/opp_missing/stage/not_real")
    assert bad_stage.status_code == 400
    assert bad_stage.json()["detail"] == "invalid stage"

    bad_status = client.post("/api/v1/evaluations/eval_missing/status/not_real")
    assert bad_status.status_code == 400
    assert bad_status.json()["detail"] == "invalid status"

    missing_eval = client.get("/api/v1/evaluations/eval_missing")
    assert missing_eval.status_code == 404
    assert missing_eval.json()["detail"] == "evaluation not found"

    missing_outputs = client.get("/api/v1/evaluations/eval_missing/outputs")
    assert missing_outputs.status_code == 404
    assert missing_outputs.json()["detail"] == "evaluation not found"

    missing_recommendation = client.get("/api/v1/recommendations/rec_missing")
    assert missing_recommendation.status_code == 404
    assert missing_recommendation.json()["detail"] == "recommendation not found"

    missing_artifact = client.get("/api/v1/artifacts/art_missing")
    assert missing_artifact.status_code == 404
    assert missing_artifact.json()["detail"] == "artifact not found"

    missing_evidence = client.get("/api/v1/evidence/evd_missing")
    assert missing_evidence.status_code == 404
    assert missing_evidence.json()["detail"] == "evidence not found"
