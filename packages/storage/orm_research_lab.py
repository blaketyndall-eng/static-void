from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ResearchLabWorkspaceORM(Base):
    __tablename__ = 'research_lab_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    experiment_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    benchmark_targets: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ResearchLabSnapshotORM(Base):
    __tablename__ = 'research_lab_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    active_experiments: Mapped[list[str]] = mapped_column(JSON, default=list)
    benchmark_tracks: Mapped[list[str]] = mapped_column(JSON, default=list)
    winning_variants: Mapped[list[str]] = mapped_column(JSON, default=list)
    challenger_variants: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    experiment_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    benchmark_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
