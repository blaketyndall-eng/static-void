from pydantic import BaseModel, Field


class CreateResearchLabWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    experiment_domains: list[str] = Field(default_factory=list)
    benchmark_targets: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateResearchLabStatusRequest(BaseModel):
    status: str


class UpsertResearchLabSnapshotRequest(BaseModel):
    active_experiments: list[str] = Field(default_factory=list)
    benchmark_tracks: list[str] = Field(default_factory=list)
    winning_variants: list[str] = Field(default_factory=list)
    challenger_variants: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    experiment_quality_score: float = Field(default=0.0, ge=0, le=100)
    benchmark_confidence_score: float = Field(default=0.0, ge=0, le=100)
