from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_venture_builder_workspace_id(prefix: str = 'venture') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class VentureBuilderStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class VentureBuilderWorkspace(BaseModel):
    id: str = Field(default_factory=new_venture_builder_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    venture_ideas: list[str] = Field(default_factory=list)
    thesis_points: list[str] = Field(default_factory=list)
    status: VentureBuilderStatus = VentureBuilderStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class VentureBuilderSnapshot(BaseModel):
    workspace_id: str
    stages: list[str] = Field(default_factory=list)
    launch_milestones: list[str] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    go_no_go_evidence: list[str] = Field(default_factory=list)
    decision_launch_links: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    launch_readiness_score: float = Field(default=0.0, ge=0, le=100)
    venture_confidence_score: float = Field(default=0.0, ge=0, le=100)


class VentureBuilderReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    venture_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
