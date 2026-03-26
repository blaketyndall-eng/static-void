from pydantic import BaseModel, Field


class CreateOperatorTeamWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    team_roles: list[str] = Field(default_factory=list)
    team_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class UpdateOperatorTeamStatusRequest(BaseModel):
    status: str


class UpsertOperatorTeamSnapshotRequest(BaseModel):
    access_rules: list[str] = Field(default_factory=list)
    credit_limits: list[str] = Field(default_factory=list)
    routing_rules: list[str] = Field(default_factory=list)
    work_queues: list[str] = Field(default_factory=list)
    human_review_points: list[str] = Field(default_factory=list)
    tool_links: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    reliability_score: float = Field(default=0.0, ge=0, le=100)
    readiness_score: float = Field(default=0.0, ge=0, le=100)
