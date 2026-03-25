from pydantic import BaseModel, Field


class CreateIntegrationsAutomationWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    integration_targets: list[str] = Field(default_factory=list)
    automation_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateIntegrationsAutomationStatusRequest(BaseModel):
    status: str


class UpsertIntegrationsAutomationSnapshotRequest(BaseModel):
    integration_health_checks: list[str] = Field(default_factory=list)
    automation_workflows: list[str] = Field(default_factory=list)
    webhook_endpoints: list[str] = Field(default_factory=list)
    freshness_alerts: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    integration_health_score: float = Field(default=0.0, ge=0, le=100)
    automation_reliability_score: float = Field(default=0.0, ge=0, le=100)
