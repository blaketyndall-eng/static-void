from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_venture_launch_bridge_id(prefix: str = 'vbridge') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class VentureLaunchBridgeStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class VentureLaunchBridgeWorkspace(BaseModel):
    id: str = Field(default_factory=new_venture_launch_bridge_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    linked_venture_workspaces: list[str] = Field(default_factory=list)
    linked_image_workspaces: list[str] = Field(default_factory=list)
    linked_action_workspaces: list[str] = Field(default_factory=list)
    linked_company_workspaces: list[str] = Field(default_factory=list)
    status: VentureLaunchBridgeStatus = VentureLaunchBridgeStatus.draft
    linked_modules: list[str] = Field(default_factory=list)


class VentureLaunchBridgeSnapshot(BaseModel):
    workspace_id: str
    venture_asset_links: list[str] = Field(default_factory=list)
    launch_creative_links: list[str] = Field(default_factory=list)
    execution_workflow_links: list[str] = Field(default_factory=list)
    operating_plan_links: list[str] = Field(default_factory=list)
    approval_records: list[str] = Field(default_factory=list)
    distribution_targets: list[str] = Field(default_factory=list)
    milestone_links: list[str] = Field(default_factory=list)
    blocker_links: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    integration_reliability_score: float = Field(default=0.0, ge=0, le=100)
    launch_operating_readiness_score: float = Field(default=0.0, ge=0, le=100)


class VentureLaunchBridgeReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    bridge_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
