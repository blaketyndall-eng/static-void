from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_signal_workspace_id(prefix: str = 'sig') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class SignalsForecastingStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class SignalsForecastingWorkspace(BaseModel):
    id: str = Field(default_factory=new_signal_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: SignalsForecastingStatus = SignalsForecastingStatus.draft
    tracked_domains: list[str] = Field(default_factory=list)
    forecast_targets: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class SignalsForecastingSnapshot(BaseModel):
    workspace_id: str
    trend_signals: list[str] = Field(default_factory=list)
    forecast_hypotheses: list[str] = Field(default_factory=list)
    anomaly_alerts: list[str] = Field(default_factory=list)
    regime_shift_notes: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    signal_quality_score: float = Field(default=0.0, ge=0, le=100)
    forecast_confidence_score: float = Field(default=0.0, ge=0, le=100)


class SignalsForecastingReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    signal_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
