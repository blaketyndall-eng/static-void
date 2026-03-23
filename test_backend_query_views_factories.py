from fastapi.testclient import TestClient

from app_backend_router_plus import app
from test_factories import create_opportunity, create_recommendation, create_seeded_evaluation_flow, create_source
from test_support import reset_database_state


def test_backend_query_views_with_shared_factories() -> None:
    reset_database_state()
    client = TestClient(app)

    source = create_source(client, name="Factory G2")
    opportunity = create_opportunity(client, title="Factory opportunity")
    flow = create_seeded_evaluation_flow(client, title="Factory evaluation")
    evaluation_id = flow["evaluation"]["id"]

    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert sources.json()[0]["id"] == source["id"]

    opportunities = client.get("/api/v1/opportunities")
    assert opportunities.status_code == 200
    assert opportunities.json()[0]["id"] == opportunity["id"]

    evaluations = client.get("/api/v1/evaluations")
    assert evaluations.status_code == 200
    assert evaluations.json()[0]["id"] == evaluation_id

    outputs = client.get(f"/api/v1/evaluations/{evaluation_id}/outputs")
    assert outputs.status_code == 200
    payload = outputs.json()
    assert payload["evaluation"]["id"] == evaluation_id
    assert len(payload["evidence"]) == 1
    assert len(payload["recommendations"]) == 1
