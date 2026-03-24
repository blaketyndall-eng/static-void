from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class OpportunityScanORM(Base):
    __tablename__ = "opportunity_scans"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    focus: Mapped[str] = mapped_column(Text)
    source_arms: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_queries: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")


class OpportunityCandidateORM(Base):
    __tablename__ = "opportunity_candidates"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    scan_id: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    opportunity_type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    target_users: Mapped[list[str]] = mapped_column(JSON, default=list)
    related_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    related_industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    demand_score: Mapped[float] = mapped_column(Float, default=0.0)
    competition_score: Mapped[float] = mapped_column(Float, default=0.0)
    whitespace_score: Mapped[float] = mapped_column(Float, default=0.0)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)


class OpportunityMarketSignalORM(Base):
    __tablename__ = "opportunity_market_signals"

    candidate_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    trend_signal: Mapped[str] = mapped_column(Text, default="")
    labor_signal: Mapped[str] = mapped_column(Text, default="")
    industry_signal: Mapped[str] = mapped_column(Text, default="")
    research_signal: Mapped[str] = mapped_column(Text, default="")
    source_stack: Mapped[list[str]] = mapped_column(JSON, default=list)
