from dataclasses import dataclass
from statistics import mean
from typing import Any

from decision_outputs_models import RecommendationStatus


@dataclass
class ScoreComponent:
    name: str
    score: float
    weight: float
    rationale: str


@dataclass
class RecommendationDraft:
    title: str
    summary: str
    rationale: str
    status: RecommendationStatus
    total_score: float
    components: list[ScoreComponent]
    evidence_notes: list[str]


def _bounded_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def generate_recommendation_draft(
    *,
    evaluation_title: str,
    criteria: list[dict[str, Any]],
    evidence_records: list[dict[str, Any]],
    artifact_records: list[dict[str, Any]],
) -> RecommendationDraft:
    criteria_strength = _bounded_score(len(criteria) * 20)
    evidence_strength = _bounded_score(len(evidence_records) * 18)
    artifact_strength = _bounded_score(len(artifact_records) * 22)

    weights_present = [float(item.get("weight", 0)) for item in criteria if item.get("weight") is not None]
    rigor_signal = _bounded_score((sum(weights_present) if weights_present else 0.25) * 100)

    components = [
        ScoreComponent(
            name="criteria_coverage",
            score=criteria_strength,
            weight=0.30,
            rationale=f"{len(criteria)} criteria captured in the evaluation.",
        ),
        ScoreComponent(
            name="evidence_depth",
            score=evidence_strength,
            weight=0.35,
            rationale=f"{len(evidence_records)} evidence records linked to the evaluation.",
        ),
        ScoreComponent(
            name="artifact_support",
            score=artifact_strength,
            weight=0.20,
            rationale=f"{len(artifact_records)} artifacts attached to the evaluation.",
        ),
        ScoreComponent(
            name="decision_rigor",
            score=rigor_signal,
            weight=0.15,
            rationale="Weighted criteria were used to assess structure and rigor.",
        ),
    ]

    weighted_total = sum(component.score * component.weight for component in components)
    total_score = round(_bounded_score(weighted_total), 2)

    if total_score >= 75:
        status = RecommendationStatus.proposed
        summary = "Evaluation is strong enough to advance with a proposed recommendation."
    elif total_score >= 50:
        status = RecommendationStatus.draft
        summary = "Evaluation shows promise but needs more support before a firm proposal."
    else:
        status = RecommendationStatus.draft
        summary = "Evaluation needs more evidence and structure before recommendation." 

    component_lines = [
        f"{component.name}: {round(component.score, 1)}/100 ({component.rationale})"
        for component in components
    ]
    rationale = (
        f"Recommendation score for '{evaluation_title}' is {total_score}/100 based on "
        + "; ".join(component_lines)
    )

    evidence_notes = [
        record.get("title", "Untitled evidence") for record in evidence_records[:5]
    ]
    if not evidence_notes and criteria:
        evidence_notes = [item.get("name", "Unnamed criterion") for item in criteria[:5]]

    return RecommendationDraft(
        title=f"Draft recommendation for {evaluation_title}",
        summary=summary,
        rationale=rationale,
        status=status,
        total_score=total_score,
        components=components,
        evidence_notes=evidence_notes,
    )


def summarize_component_scores(components: list[ScoreComponent]) -> dict[str, float]:
    return {component.name: round(component.score, 2) for component in components}


def average_component_score(components: list[ScoreComponent]) -> float:
    if not components:
        return 0.0
    return round(mean(component.score for component in components), 2)
