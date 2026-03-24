from pydantic import BaseModel, Field


class CreateMarketingProjectRequest(BaseModel):
    name: str
    project_type: str
    owner: str
    description: str = ""
    audience: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateMarketingProjectStatusRequest(BaseModel):
    status: str


class UpsertMarketingResearchRequest(BaseModel):
    market_summary: str = ""
    competitor_summary: str = ""
    audience_insights: list[str] = Field(default_factory=list)
    channel_insights: list[str] = Field(default_factory=list)
    source_notes: list[dict] = Field(default_factory=list)
    opportunity_score: float = Field(default=0.0, ge=0, le=100)


class CreateContentAssetRequest(BaseModel):
    asset_type: str
    title: str
    status: str = "draft"
    target_channel: str = ""
    source_brief: str = ""
    generated_outline: list[str] = Field(default_factory=list)
    body: str = ""
    call_to_action: str = ""


class UpsertMarketingAnalyticsRequest(BaseModel):
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    engagement_rate: float = 0.0
    content_velocity: int = 0
    quality_score: float = Field(default=0.0, ge=0, le=100)
