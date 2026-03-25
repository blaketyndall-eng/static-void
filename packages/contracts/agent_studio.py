from pydantic import BaseModel, Field


class CreateAgentStudioWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    agent_roles: list[str] = Field(default_factory=list)
    routing_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateAgentStudioStatusRequest(BaseModel):
    status: str


class UpsertAgentStudioSnapshotRequest(BaseModel):
    routing_policies: list[str] = Field(default_factory=list)
    hitl_checkpoints: list[str] = Field(default_factory=list)
    replay_tracks: list[str] = Field(default_factory=list)
    budget_controls: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    routing_quality_score: float = Field(default=0.0, ge=0, le=100)
    operator_confidence_score: float = Field(default=0.0, ge=0, le=100)
