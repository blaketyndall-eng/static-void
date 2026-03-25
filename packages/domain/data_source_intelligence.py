from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_data_source_workspace_id(prefix: str = 'source') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class DataSourceIntelligenceStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class DataSourceIntelligenceWorkspace(BaseModel):
    id: str = Field(default_factory=new_data_source_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: DataSourceIntelligenceStatus = DataSourceIntelligenceStatus.draft
    source_domains: list[str] = Field(default_factory=list)
    intelligence_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class DataSourceIntelligenceSnapshot(BaseModel):
    workspace_id: str
    source_health_checks: list[str] = Field(default_factory=list)
    freshness_monitors: list[str] = Field(default_factory=list)
    reliability_flags: list[str] = Field(default_factory=list)
    conflict_detections: list[str] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    source_quality_score: float = Field(default=0.0, ge=0, le=100)
    freshness_confidence_score: float = Field(default=0.0, ge=0, le=100)


class DataSourceIntelligenceReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    source_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
