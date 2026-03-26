from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_creative_ops_bridge_id(prefix: str = 'creativeops') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class CreativeOpsBridgeStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class CreativeOpsBridgeWorkspace(BaseModel):
    id: str = Field(default_factory=new_creative_ops_bridge_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    linked_ventures: list[str] = Field(default_factory=list)
    linked_marketing_programs: list[str] = Field(default_factory=list)
    linked_execution_workflows: list[str] = Field(default_factory=list)
    status: CreativeOpsBridgeStatus = CreativeOpsBridgeStatus.draft
    linked_modules: list[str] = Field(default_factory=list)


class CreativeOpsBridgeSnapshot(BaseModel):
    workspace_id: str
    creative_asset_paths: list[str] = Field(default_factory=list)
    venture_asset_links: list[str] = Field(default_factory=list)
    marketing_asset_links: list[str] = Field(default_factory=list)
    execution_job_links: list[str] = Field(default_factory=list)
    approval_records: list[str] = Field(default_factory=list)
    distribution_targets: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    integration_reliability_score: float = Field(default=0.0, ge=0, le=100)
    launch_readiness_score: float = Field(default=0.0, ge=0, le=100)


class CreativeOpsBridgeReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    bridge_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
