from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class MarketingProjectORM(Base):
    __tablename__ = "marketing_projects"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    project_type: Mapped[str] = mapped_column(String(80), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), index=True)
    audience: Mapped[list[str]] = mapped_column(JSON, default=list)
    channels: Mapped[list[str]] = mapped_column(JSON, default=list)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class MarketingResearchRecordORM(Base):
    __tablename__ = "marketing_research_records"

    project_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    market_summary: Mapped[str] = mapped_column(Text, default="")
    competitor_summary: Mapped[str] = mapped_column(Text, default="")
    audience_insights: Mapped[list[str]] = mapped_column(JSON, default=list)
    channel_insights: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    opportunity_score: Mapped[float] = mapped_column(Float, default=0.0)


class ContentAssetORM(Base):
    __tablename__ = "marketing_content_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(40), index=True)
    asset_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    target_channel: Mapped[str] = mapped_column(String(120), default="")
    source_brief: Mapped[str] = mapped_column(Text, default="")
    generated_outline: Mapped[list[str]] = mapped_column(JSON, default=list)
    body: Mapped[str] = mapped_column(Text, default="")
    call_to_action: Mapped[str] = mapped_column(Text, default="")


class MarketingAnalyticsSnapshotORM(Base):
    __tablename__ = "marketing_analytics_snapshots"

    project_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    content_velocity: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
