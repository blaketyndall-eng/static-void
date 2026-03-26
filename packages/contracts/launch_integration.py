from pydantic import BaseModel, Field


class CreateLaunchIntegrationWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    venture_workspaces: list[str] = Field(default_factory=list)
    image_workspaces: list[str] = Field(default_factory=list)
    action_workspaces: list[str] = Field(default_factory=list)
    company_workspaces: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class UpdateLaunchIntegrationStatusRequest(BaseModel):
    status: str


class UpsertLaunchIntegrationSnapshotRequest(BaseModel):
    venture_asset_links: list[str] = Field(default_factory=list)
    launch_asset_links: list[str] = Field(default_factory=list)
    execution_links: list[str] = Field(default_factory=list)
    operating_links: list[str] = Field(default_factory=list)
    approval_records: list[str] = Field(default_factory=list)
    distribution_targets: list[str] = Field(default_factory=list)
    milestone_links: list[str] = Field(default_factory=list)
    blocker_links: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    integration_reliability_score: float = Field(default=0.0, ge=0, le=100)
    launch_readiness_score: float = Field(default=0.0, ge=0, le=100)
