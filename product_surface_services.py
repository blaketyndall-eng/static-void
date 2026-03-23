from repository_decision_outputs import ArtifactRepository, EvidenceRepository, RecommendationRepository
from repository_evaluations import EvaluationRepository
from repository_opportunities import OpportunityRepository
from repository_sources import SourceRepository
from recommendation_ranking import rank_recommendations


def build_decision_board_summary(db) -> dict:
    source_repo = SourceRepository(db)
    opportunity_repo = OpportunityRepository(db)
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    sources = [item.model_dump(mode="json") for item in source_repo.list()]
    opportunities = [item.model_dump(mode="json") for item in opportunity_repo.list()]
    evaluations = [item.model_dump(mode="json") for item in evaluation_repo.list()]
    recommendations = [item.model_dump(mode="json") for item in recommendation_repo.list()]

    latest_recommendations = sorted(
        recommendations,
        key=lambda item: item.get("updated_at", item.get("created_at", "")),
        reverse=True,
    )[:5]

    evaluation_status_counts: dict[str, int] = {}
    for item in evaluations:
        status = item.get("status", "unknown")
        evaluation_status_counts[status] = evaluation_status_counts.get(status, 0) + 1

    opportunity_stage_counts: dict[str, int] = {}
    for item in opportunities:
        stage = item.get("stage", "unknown")
        opportunity_stage_counts[stage] = opportunity_stage_counts.get(stage, 0) + 1

    return {
        "counts": {
            "sources": len(sources),
            "opportunities": len(opportunities),
            "evaluations": len(evaluations),
            "recommendations": len(recommendations),
        },
        "evaluation_status_counts": evaluation_status_counts,
        "opportunity_stage_counts": opportunity_stage_counts,
        "latest_recommendations": latest_recommendations,
    }


def build_attention_needed(db) -> dict:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluations = [item.model_dump(mode="json") for item in evaluation_repo.list()]
    recommendations = [item.model_dump(mode="json") for item in recommendation_repo.list()]

    by_evaluation: dict[str, list[dict]] = {}
    for recommendation in recommendations:
        evaluation_id = recommendation.get("linked_entity_id")
        if recommendation.get("linked_entity_type") != "evaluation" or not evaluation_id:
            continue
        by_evaluation.setdefault(evaluation_id, []).append(recommendation)

    items = []
    for evaluation in evaluations:
        evaluation_id = evaluation["id"]
        linked = by_evaluation.get(evaluation_id, [])
        if not linked:
            items.append(
                {
                    "evaluation_id": evaluation_id,
                    "title": evaluation["title"],
                    "reason": "No recommendation exists yet.",
                    "priority": "high",
                }
            )
            continue
        proposed = [item for item in linked if item.get("status") == "proposed"]
        if not proposed:
            items.append(
                {
                    "evaluation_id": evaluation_id,
                    "title": evaluation["title"],
                    "reason": "Recommendation exists but none are proposed yet.",
                    "priority": "medium",
                }
            )

    return {"count": len(items), "items": items}


def build_recent_activity(logger, limit: int = 25) -> dict:
    events = logger.recent(limit=limit)
    items = []
    for event in reversed(events):
        items.append(
            {
                "id": event.get("id"),
                "event_type": event.get("event_type"),
                "entity_type": event.get("entity_type"),
                "entity_id": event.get("entity_id"),
                "category": event.get("category"),
                "time": event.get("created_at", event.get("timestamp")),
                "payload": event.get("payload", {}),
            }
        )
    return {"count": len(items), "items": items}


def build_evaluation_summary(db, evaluation_id: str) -> dict | None:
    evaluation_repo = EvaluationRepository(db)
    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        return None

    artifacts = [
        item.model_dump(mode="json")
        for item in artifact_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    evidence = [
        item.model_dump(mode="json")
        for item in evidence_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]

    latest_recommendation = recommendations[-1] if recommendations else None

    return {
        "evaluation": evaluation.model_dump(mode="json"),
        "counts": {
            "criteria": len(evaluation.criteria),
            "evidence": len(evidence),
            "artifacts": len(artifacts),
            "recommendations": len(recommendations),
        },
        "latest_recommendation": latest_recommendation,
        "artifacts": artifacts,
        "evidence": evidence,
    }


def build_recommendation_cards(db, evaluation_id: str) -> dict | None:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)
    artifact_repo = ArtifactRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        return None

    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    artifacts = {item.id: item.model_dump(mode="json") for item in artifact_repo.list()}

    cards = []
    for recommendation in recommendations:
        linked_artifacts = [artifacts[item_id] for item_id in recommendation.get("artifact_ids", []) if item_id in artifacts]
        cards.append(
            {
                "id": recommendation["id"],
                "title": recommendation["title"],
                "summary": recommendation["summary"],
                "status": recommendation["status"],
                "why": recommendation.get("rationale", ""),
                "artifact_count": len(recommendation.get("artifact_ids", [])),
                "evidence_count": len(recommendation.get("evidence_ids", [])),
                "artifacts": linked_artifacts,
            }
        )

    return {"evaluation_id": evaluation_id, "cards": cards}


def build_ranked_recommendation_summary(db, evaluation_id: str) -> dict | None:
    evaluation_repo = EvaluationRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        return None

    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    ranked = rank_recommendations(recommendations)
    top_recommendation = ranked[0] if ranked else None

    return {
        "evaluation_id": evaluation_id,
        "count": len(ranked),
        "top_recommendation": top_recommendation,
        "recommendations": ranked,
    }


def build_evaluation_readiness(db, evaluation_id: str) -> dict | None:
    evaluation_repo = EvaluationRepository(db)
    artifact_repo = ArtifactRepository(db)
    evidence_repo = EvidenceRepository(db)
    recommendation_repo = RecommendationRepository(db)

    evaluation = evaluation_repo.get(evaluation_id)
    if evaluation is None:
        return None

    artifacts = [
        item.model_dump(mode="json")
        for item in artifact_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    evidence = [
        item.model_dump(mode="json")
        for item in evidence_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]
    recommendations = [
        item.model_dump(mode="json")
        for item in recommendation_repo.list()
        if item.linked_entity_type == "evaluation" and item.linked_entity_id == evaluation_id
    ]

    criteria_count = len(evaluation.criteria)
    evidence_count = len(evidence)
    artifact_count = len(artifacts)
    recommendation_count = len(recommendations)

    score = 0
    score += min(criteria_count, 4) * 20
    score += min(evidence_count, 3) * 15
    score += min(artifact_count, 2) * 10
    score += 20 if recommendation_count > 0 else 0
    score = min(score, 100)

    if score >= 80:
        level = "ready"
    elif score >= 50:
        level = "developing"
    else:
        level = "early"

    blockers = []
    if criteria_count == 0:
        blockers.append("No criteria defined.")
    if evidence_count == 0:
        blockers.append("No evidence attached.")
    if recommendation_count == 0:
        blockers.append("No recommendation generated yet.")

    return {
        "evaluation_id": evaluation_id,
        "score": score,
        "level": level,
        "counts": {
            "criteria": criteria_count,
            "evidence": evidence_count,
            "artifacts": artifact_count,
            "recommendations": recommendation_count,
        },
        "blockers": blockers,
    }
