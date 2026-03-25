from pydantic import BaseModel, Field


class CreateDataSourceIntelligenceWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    source_domains: list[str] = Field(default_factory=list)
    intelligence_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateDataSourceIntelligenceStatusRequest(BaseModel):
    status: str


class UpsertDataSourceIntelligenceSnapshotRequest(BaseModel):
    source_health_checks: list[str] = Field(default_factory=list)
    freshness_monitors: list[str] = Field(default_factory=list)
    reliability_flags: list[str] = Field(default_factory=list)
    conflict_detections: list[str] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    source_quality_score: float = Field(default=0.0, ge=0, le=100)
    freshness_confidence_score: float = Field(default=0.0, ge=0, le=100)
