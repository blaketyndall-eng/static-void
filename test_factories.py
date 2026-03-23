from fastapi.testclient import TestClient


def create_source(client: TestClient, *, name: str = "G2") -> dict:
    response = client.post(
        "/api/v1/sources",
        json={
            "name": name,
            "source_type": "website",
            "trust_score": 0.8,
            "freshness_label": "weekly",
            "tags": ["reviews"],
        },
    )
    response.raise_for_status()
    return response.json()


def create_opportunity(client: TestClient, *, title: str = "Decision opportunity") -> dict:
    response = client.post(
        "/api/v1/opportunities",
        json={
            "title": title,
            "summary": "Track vendor signals for evaluations.",
            "themes": ["signals"],
            "score": 81,
        },
    )
    response.raise_for_status()
    return response.json()


def create_evaluation(client: TestClient, *, title: str = "Evaluation", decision_owner: str = "blake") -> dict:
    response = client.post(
        "/api/v1/evaluations",
        json={
            "title": title,
            "decision_owner": decision_owner,
            "criteria": [{"name": "Security", "weight": 0.4}],
        },
    )
    response.raise_for_status()
    return response.json()


def create_evidence_record(client: TestClient, evaluation_id: str, *, title: str = "Security note") -> dict:
    response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/evidence-records",
        json={
            "title": title,
            "evidence_kind": "note",
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "detail": "Vendor supports SSO and SOC 2.",
        },
    )
    response.raise_for_status()
    return response.json()


def create_recommendation(client: TestClient, evaluation_id: str, *, title: str = "Advance vendor") -> dict:
    response = client.post(
        f"/api/v1/evaluations/{evaluation_id}/recommendations",
        json={
            "title": title,
            "linked_entity_type": "evaluation",
            "linked_entity_id": evaluation_id,
            "summary": "Advance to pricing review.",
            "rationale": "Best fit on security and workflow.",
            "status": "proposed",
        },
    )
    response.raise_for_status()
    return response.json()


def create_seeded_evaluation_flow(client: TestClient, *, title: str = "Seeded evaluation") -> dict:
    evaluation = create_evaluation(client, title=title)
    evidence = create_evidence_record(client, evaluation["id"])
    recommendation = create_recommendation(client, evaluation["id"])
    return {
        "evaluation": evaluation,
        "evidence": evidence,
        "recommendation": recommendation,
    }
