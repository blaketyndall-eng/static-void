from pydantic import BaseModel, Field


class CreateDecisionMemoryWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    memory_domains: list[str] = Field(default_factory=list)
    review_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateDecisionMemoryStatusRequest(BaseModel):
    status: str


class UpsertDecisionMemorySnapshotRequest(BaseModel):
    captured_decisions: list[str] = Field(default_factory=list)
    outcome_reviews: list[str] = Field(default_factory=list)
    regret_patterns: list[str] = Field(default_factory=list)
    reuse_candidates: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    memory_quality_score: float = Field(default=0.0, ge=0, le=100)
    calibration_score: float = Field(default=0.0, ge=0, le=100)
