from typing import Any

from pydantic import BaseModel, Field


class DecisionBoardCounts(BaseModel):
    sources: int
    opportunities: int
    evaluations: int
    recommendations: int


class DecisionBoardSummaryResponse(BaseModel):
    counts: DecisionBoardCounts
    evaluation_status_counts: dict[str, int] = Field(default_factory=dict)
    opportunity_stage_counts: dict[str, int] = Field(default_factory=dict)
    latest_recommendations: list[dict[str, Any]] = Field(default_factory=list)


class AttentionItem(BaseModel):
    evaluation_id: str
    title: str
    reason: str
    priority: str


class AttentionNeededResponse(BaseModel):
    count: int
    items: list[AttentionItem] = Field(default_factory=list)


class ActivityItem(BaseModel):
    id: str | None = None
    event_type: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    category: str | None = None
    time: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RecentActivityResponse(BaseModel):
    count: int
    items: list[ActivityItem] = Field(default_factory=list)


class EvaluationSummaryCounts(BaseModel):
    criteria: int
    evidence: int
    artifacts: int
    recommendations: int


class EvaluationSummaryResponse(BaseModel):
    evaluation: dict[str, Any]
    counts: EvaluationSummaryCounts
    latest_recommendation: dict[str, Any] | None = None
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class RecommendationCard(BaseModel):
    id: str
    title: str
    summary: str
    status: str
    why: str = ""
    artifact_count: int = 0
    evidence_count: int = 0
    artifacts: list[dict[str, Any]] = Field(default_factory=list)


class RecommendationCardsResponse(BaseModel):
    evaluation_id: str
    cards: list[RecommendationCard] = Field(default_factory=list)


class RankedRecommendationSummaryResponse(BaseModel):
    evaluation_id: str
    count: int
    top_recommendation: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]] = Field(default_factory=list)


class EvaluationReadinessCounts(BaseModel):
    criteria: int
    evidence: int
    artifacts: int
    recommendations: int


class EvaluationReadinessResponse(BaseModel):
    evaluation_id: str
    score: int
    level: str
    counts: EvaluationReadinessCounts
    blockers: list[str] = Field(default_factory=list)
