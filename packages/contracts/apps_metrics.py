from pydantic import BaseModel, Field


class UpsertAppAnalyticsRequest(BaseModel):
    sessions: int = 0
    active_users: int = 0
    completions: int = 0
    failures: int = 0
    outcome_quality_score: float = Field(default=0.0, ge=0, le=100)
    latency_ms: float = 0.0
    model_cost_estimate: float = 0.0


class UpsertAppHealthRequest(BaseModel):
    healthy: bool = True
    error_count: int = 0
    warning_count: int = 0
    notes: list[str] = Field(default_factory=list)
