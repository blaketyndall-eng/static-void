from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_marketing_project_id(prefix: str = "mkt") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class MarketingProjectType(str, Enum):
    research = "research"
    campaign = "campaign"
    content_system = "content_system"
    launch = "launch"
    seo = "seo"
    brand = "brand"


class MarketingProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"


class ContentAssetType(str, Enum):
    brief = "brief"
    blog_post = "blog_post"
    landing_page = "landing_page"
    email = "email"
    social_post = "social_post"
    case_study = "case_study"
    ad_copy = "ad_copy"


class MarketingProject(BaseModel):
    id: str = Field(default_factory=new_marketing_project_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    name: str
    project_type: MarketingProjectType
    owner: str
    description: str = ""
    status: MarketingProjectStatus = MarketingProjectStatus.draft
    audience: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class MarketingResearchRecord(BaseModel):
    project_id: str
    market_summary: str = ""
    competitor_summary: str = ""
    audience_insights: list[str] = Field(default_factory=list)
    channel_insights: list[str] = Field(default_factory=list)
    source_notes: list[dict[str, Any]] = Field(default_factory=list)
    opportunity_score: float = Field(default=0.0, ge=0, le=100)


class ContentAsset(BaseModel):
    project_id: str
    asset_type: ContentAssetType
    title: str
    status: str = "draft"
    target_channel: str = ""
    source_brief: str = ""
    generated_outline: list[str] = Field(default_factory=list)
    body: str = ""
    call_to_action: str = ""


class MarketingAnalyticsSnapshot(BaseModel):
    project_id: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement_rate: float = 0.0
    content_velocity: int = 0
    quality_score: float = Field(default=0.0, ge=0, le=100)
