from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_launch_integration_id(prefix: str = 'launchint') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class LaunchIntegrationStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class LaunchIntegrationWorkspace(BaseModel):
    id: str = Field(default_factory=new_launch_integration_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    venture_workspaces: list[str] = Field(default_factory=list)
    image_workspaces: list[str] = Field(default_factory=list)
    action_workspaces: list[str] = Field(default_factory=list)
    company_workspaces: list[str] = Field(default_factory=list)
    status: LaunchIntegrationStatus = LaunchIntegrationStatus.draft
    linked_modules: list[str] = Field(default_factory=list)


class LaunchIntegrationSnapshot(BaseModel):
    workspace_id: str
    venture_asset_links: list[str] = Field(default_factory=list)
    launch_asset_links: list[str] = Field(default_factory=list)
    execution_links: list[str] = Field(default_factory=list)
    operating_links: list[str] = Field(default_factory=list)
    approval_records: list[str] = Field(default_factory=list)
    distribution_targets: list[str] = Field(default_factory=list)
    milestone_links: list[str] = Field(default_factory=list)
    blocker_links: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    integration_reliability_score: float = Field(default=0.0, ge=0, le=100)
    launch_readiness_score: float = Field(default=0.0, ge=0, le=100)


class LaunchIntegrationReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    integration_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
