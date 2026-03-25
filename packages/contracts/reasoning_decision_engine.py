from pydantic import BaseModel, Field


class CreateReasoningDecisionEngineWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    decision_domains: list[str] = Field(default_factory=list)
    reasoning_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateReasoningDecisionEngineStatusRequest(BaseModel):
    status: str


class UpsertReasoningDecisionEngineSnapshotRequest(BaseModel):
    reasoning_policies: list[str] = Field(default_factory=list)
    recommendation_strategies: list[str] = Field(default_factory=list)
    confidence_rules: list[str] = Field(default_factory=list)
    tradeoff_models: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    reasoning_quality_score: float = Field(default=0.0, ge=0, le=100)
    recommendation_confidence_score: float = Field(default=0.0, ge=0, le=100)
