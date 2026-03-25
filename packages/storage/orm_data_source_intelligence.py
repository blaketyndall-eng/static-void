from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class DataSourceIntelligenceWorkspaceORM(Base):
    __tablename__ = 'data_source_intelligence_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    source_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    intelligence_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class DataSourceIntelligenceSnapshotORM(Base):
    __tablename__ = 'data_source_intelligence_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    source_health_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    freshness_monitors: Mapped[list[str]] = mapped_column(JSON, default=list)
    reliability_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    conflict_detections: Mapped[list[str]] = mapped_column(JSON, default=list)
    coverage_gaps: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    source_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    freshness_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
