from pydantic import BaseModel, Field


class CreateAIGovernanceWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    model_scope: list[str] = Field(default_factory=list)
    evaluation_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateAIGovernanceStatusRequest(BaseModel):
    status: str


class UpsertAIGovernanceSnapshotRequest(BaseModel):
    benchmark_tracks: list[str] = Field(default_factory=list)
    policy_checks: list[str] = Field(default_factory=list)
    monitoring_checks: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    governance_score: float = Field(default=0.0, ge=0, le=100)
