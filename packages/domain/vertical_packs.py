from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_vertical_pack_workspace_id(prefix: str = 'pack') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class VerticalPacksStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    designing = 'designing'
    archived = 'archived'


class VerticalPacksWorkspace(BaseModel):
    id: str = Field(default_factory=new_vertical_pack_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: VerticalPacksStatus = VerticalPacksStatus.draft
    industries: list[str] = Field(default_factory=list)
    pack_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class VerticalPacksSnapshot(BaseModel):
    workspace_id: str
    pack_templates: list[str] = Field(default_factory=list)
    scoring_models: list[str] = Field(default_factory=list)
    domain_playbooks: list[str] = Field(default_factory=list)
    knowledge_assets: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    pack_quality_score: float = Field(default=0.0, ge=0, le=100)
    adaptation_readiness_score: float = Field(default=0.0, ge=0, le=100)


class VerticalPacksReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    pack_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
