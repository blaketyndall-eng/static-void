from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class VentureBuilderWorkspaceORM(Base):
    __tablename__ = 'venture_builder_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    venture_ideas: Mapped[list[str]] = mapped_column(JSON, default=list)
    thesis_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class VentureBuilderSnapshotORM(Base):
    __tablename__ = 'venture_builder_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    stages: Mapped[list[str]] = mapped_column(JSON, default=list)
    launch_milestones: Mapped[list[str]] = mapped_column(JSON, default=list)
    owners: Mapped[list[str]] = mapped_column(JSON, default=list)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list)
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    go_no_go_evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    decision_launch_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    launch_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    venture_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
