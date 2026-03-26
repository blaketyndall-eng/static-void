from pydantic import BaseModel, Field


class CreateFeedbackOutcomeScoringWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    outcome_domains: list[str] = Field(default_factory=list)
    scoring_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateFeedbackOutcomeScoringStatusRequest(BaseModel):
    status: str


class UpsertFeedbackOutcomeScoringSnapshotRequest(BaseModel):
    outcome_reviews: list[str] = Field(default_factory=list)
    prediction_checks: list[str] = Field(default_factory=list)
    usefulness_scores: list[str] = Field(default_factory=list)
    regret_signals: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    outcome_quality_score: float = Field(default=0.0, ge=0, le=100)
    feedback_readiness_score: float = Field(default=0.0, ge=0, le=100)
