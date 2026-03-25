from pydantic import BaseModel, Field


class CreateIngestionDataAcquisitionWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    source_targets: list[str] = Field(default_factory=list)
    ingestion_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateIngestionDataAcquisitionStatusRequest(BaseModel):
    status: str


class UpsertIngestionDataAcquisitionSnapshotRequest(BaseModel):
    connectors: list[str] = Field(default_factory=list)
    sync_jobs: list[str] = Field(default_factory=list)
    normalization_pipelines: list[str] = Field(default_factory=list)
    freshness_windows: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    ingestion_health_score: float = Field(default=0.0, ge=0, le=100)
    normalization_readiness_score: float = Field(default=0.0, ge=0, le=100)
