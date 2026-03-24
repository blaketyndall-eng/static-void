from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_app_id(prefix: str = "app") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def new_app_run_id(prefix: str = "app_run") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AppType(str, Enum):
    operator_console = "operator_console"
    analyst_app = "analyst_app"
    workflow_app = "workflow_app"
    monitoring_app = "monitoring_app"
    reporting_app = "reporting_app"
    consumer_decision_app = "consumer_decision_app"
    internal_research_tool = "internal_research_tool"


class AppStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    degraded = "degraded"
    archived = "archived"


class DeploymentState(str, Enum):
    local = "local"
    staging = "staging"
    production = "production"
    failed = "failed"


class AppRecord(BaseModel):
    id: str = Field(default_factory=new_app_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    name: str
    app_type: AppType
    owner: str
    description: str = ""
    status: AppStatus = AppStatus.draft
    deployment_state: DeploymentState = DeploymentState.local
    version: str = "0.1.0"
    runtime_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class AppRun(BaseModel):
    id: str = Field(default_factory=new_app_run_id)
    app_id: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    status: str = "running"
    stages: list[dict[str, Any]] = Field(default_factory=list)
    output_summary: str = ""
    error_summary: str = ""


class AppAnalyticsSnapshot(BaseModel):
    app_id: str
    sessions: int = 0
    active_users: int = 0
    completions: int = 0
    failures: int = 0
    outcome_quality_score: float = Field(default=0.0, ge=0, le=100)
    latency_ms: float = 0.0
    model_cost_estimate: float = 0.0


class AppHealthCheck(BaseModel):
    app_id: str
    checked_at: datetime = Field(default_factory=utc_now)
    healthy: bool = True
    error_count: int = 0
    warning_count: int = 0
    notes: list[str] = Field(default_factory=list)


class AppFeedbackItem(BaseModel):
    app_id: str
    created_at: datetime = Field(default_factory=utc_now)
    category: str
    severity: str = "info"
    message: str
