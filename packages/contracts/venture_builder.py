from pydantic import BaseModel, Field


class CreateVentureBuilderWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    venture_ideas: list[str] = Field(default_factory=list)
    thesis_points: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class UpdateVentureBuilderStatusRequest(BaseModel):
    status: str


class UpsertVentureBuilderSnapshotRequest(BaseModel):
    stages: list[str] = Field(default_factory=list)
    launch_milestones: list[str] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    go_no_go_evidence: list[str] = Field(default_factory=list)
    decision_launch_links: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    launch_readiness_score: float = Field(default=0.0, ge=0, le=100)
    venture_confidence_score: float = Field(default=0.0, ge=0, le=100)
