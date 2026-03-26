from pydantic import BaseModel, Field


class CreateWorkforceCoordinationWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    role_groups: list[str] = Field(default_factory=list)
    coordination_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class UpdateWorkforceCoordinationStatusRequest(BaseModel):
    status: str


class UpsertWorkforceCoordinationSnapshotRequest(BaseModel):
    access_rules: list[str] = Field(default_factory=list)
    spend_limits: list[str] = Field(default_factory=list)
    routing_rules: list[str] = Field(default_factory=list)
    work_queues: list[str] = Field(default_factory=list)
    review_points: list[str] = Field(default_factory=list)
    linked_tools: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    reliability_score: float = Field(default=0.0, ge=0, le=100)
    readiness_score: float = Field(default=0.0, ge=0, le=100)
