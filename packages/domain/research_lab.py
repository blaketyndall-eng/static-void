from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_research_lab_workspace_id(prefix: str = 'lab') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ResearchLabStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    experimenting = 'experimenting'
    archived = 'archived'


class ResearchLabWorkspace(BaseModel):
    id: str = Field(default_factory=new_research_lab_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: ResearchLabStatus = ResearchLabStatus.draft
    experiment_domains: list[str] = Field(default_factory=list)
    benchmark_targets: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class ResearchLabSnapshot(BaseModel):
    workspace_id: str
    active_experiments: list[str] = Field(default_factory=list)
    benchmark_tracks: list[str] = Field(default_factory=list)
    winning_variants: list[str] = Field(default_factory=list)
    challenger_variants: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    experiment_quality_score: float = Field(default=0.0, ge=0, le=100)
    benchmark_confidence_score: float = Field(default=0.0, ge=0, le=100)


class ResearchLabReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    experiment_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
