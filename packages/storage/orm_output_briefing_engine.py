from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class OutputBriefingEngineWorkspaceORM(Base):
    __tablename__ = 'output_briefing_engine_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    briefing_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class OutputBriefingEngineSnapshotORM(Base):
    __tablename__ = 'output_briefing_engine_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    briefing_templates: Mapped[list[str]] = mapped_column(JSON, default=list)
    distribution_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    alert_formats: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_packs: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    output_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    briefing_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
