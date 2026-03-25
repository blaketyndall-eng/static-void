from pydantic import BaseModel, Field


class CreateVerticalPacksWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    industries: list[str] = Field(default_factory=list)
    pack_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateVerticalPacksStatusRequest(BaseModel):
    status: str


class UpsertVerticalPacksSnapshotRequest(BaseModel):
    pack_templates: list[str] = Field(default_factory=list)
    scoring_models: list[str] = Field(default_factory=list)
    domain_playbooks: list[str] = Field(default_factory=list)
    knowledge_assets: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    pack_quality_score: float = Field(default=0.0, ge=0, le=100)
    adaptation_readiness_score: float = Field(default=0.0, ge=0, le=100)
