from decision_outputs_models import RecommendationStatus


STATUS_PRIORITY = {
    RecommendationStatus.accepted.value: 4,
    RecommendationStatus.proposed.value: 3,
    RecommendationStatus.draft.value: 2,
    RecommendationStatus.rejected.value: 1,
}


def recommendation_rank_key(recommendation: dict) -> tuple:
    status_value = recommendation.get("status", RecommendationStatus.draft.value)
    status_priority = STATUS_PRIORITY.get(status_value, 0)
    artifact_count = len(recommendation.get("artifact_ids", []))
    evidence_count = len(recommendation.get("evidence_ids", []))
    rationale_length = len(recommendation.get("rationale", ""))
    return (
        status_priority,
        evidence_count,
        artifact_count,
        rationale_length,
        recommendation.get("title", ""),
    )


def rank_recommendations(recommendations: list[dict]) -> list[dict]:
    ordered = sorted(recommendations, key=recommendation_rank_key, reverse=True)
    ranked: list[dict] = []
    for index, item in enumerate(ordered, start=1):
        ranked.append({**item, "rank": index})
    return ranked
