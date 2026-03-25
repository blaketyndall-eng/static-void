from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_output_workspace_id(prefix: str = 'brief') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class OutputBriefingEngineStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class OutputBriefingEngineWorkspace(BaseModel):
    id: str = Field(default_factory=new_output_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: OutputBriefingEngineStatus = OutputBriefingEngineStatus.draft
    briefing_domains: list[str] = Field(default_factory=list)
    output_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class OutputBriefingEngineSnapshot(BaseModel):
    workspace_id: str
    briefing_templates: list[str] = Field(default_factory=list)
    distribution_rules: list[str] = Field(default_factory=list)
    alert_formats: list[str] = Field(default_factory=list)
    evidence_packs: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    output_quality_score: float = Field(default=0.0, ge=0, le=100)
    briefing_readiness_score: float = Field(default=0.0, ge=0, le=100)


class OutputBriefingEngineReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    output_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
