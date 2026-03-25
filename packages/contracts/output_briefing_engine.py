from pydantic import BaseModel, Field


class CreateOutputBriefingEngineWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    briefing_domains: list[str] = Field(default_factory=list)
    output_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateOutputBriefingEngineStatusRequest(BaseModel):
    status: str


class UpsertOutputBriefingEngineSnapshotRequest(BaseModel):
    briefing_templates: list[str] = Field(default_factory=list)
    distribution_rules: list[str] = Field(default_factory=list)
    alert_formats: list[str] = Field(default_factory=list)
    evidence_packs: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    output_quality_score: float = Field(default=0.0, ge=0, le=100)
    briefing_readiness_score: float = Field(default=0.0, ge=0, le=100)
