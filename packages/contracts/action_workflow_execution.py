from pydantic import BaseModel, Field


class CreateActionWorkflowExecutionWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    execution_domains: list[str] = Field(default_factory=list)
    workflow_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateActionWorkflowExecutionStatusRequest(BaseModel):
    status: str


class UpsertActionWorkflowExecutionSnapshotRequest(BaseModel):
    workflow_templates: list[str] = Field(default_factory=list)
    approval_checkpoints: list[str] = Field(default_factory=list)
    connector_actions: list[str] = Field(default_factory=list)
    execution_logs: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    execution_reliability_score: float = Field(default=0.0, ge=0, le=100)
    approval_readiness_score: float = Field(default=0.0, ge=0, le=100)
