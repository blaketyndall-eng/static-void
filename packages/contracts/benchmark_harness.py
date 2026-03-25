from pydantic import BaseModel, Field


class CreateBenchmarkHarnessWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    benchmark_domains: list[str] = Field(default_factory=list)
    benchmark_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateBenchmarkHarnessStatusRequest(BaseModel):
    status: str


class UpsertBenchmarkHarnessSnapshotRequest(BaseModel):
    benchmark_suites: list[str] = Field(default_factory=list)
    replay_datasets: list[str] = Field(default_factory=list)
    challenger_models: list[str] = Field(default_factory=list)
    rollback_rules: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    benchmark_quality_score: float = Field(default=0.0, ge=0, le=100)
    harness_readiness_score: float = Field(default=0.0, ge=0, le=100)
