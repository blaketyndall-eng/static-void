from pydantic import BaseModel, Field


class CreateSignalsForecastingWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    tracked_domains: list[str] = Field(default_factory=list)
    forecast_targets: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateSignalsForecastingStatusRequest(BaseModel):
    status: str


class UpsertSignalsForecastingSnapshotRequest(BaseModel):
    trend_signals: list[str] = Field(default_factory=list)
    forecast_hypotheses: list[str] = Field(default_factory=list)
    anomaly_alerts: list[str] = Field(default_factory=list)
    regime_shift_notes: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    signal_quality_score: float = Field(default=0.0, ge=0, le=100)
    forecast_confidence_score: float = Field(default=0.0, ge=0, le=100)
