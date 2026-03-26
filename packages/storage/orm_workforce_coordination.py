from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class WorkforceCoordinationWorkspaceORM(Base):
    __tablename__ = 'workforce_coordination_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    role_groups: Mapped[list[str]] = mapped_column(JSON, default=list)
    coordination_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class WorkforceCoordinationSnapshotORM(Base):
    __tablename__ = 'workforce_coordination_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    access_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    spend_limits: Mapped[list[str]] = mapped_column(JSON, default=list)
    routing_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    work_queues: Mapped[list[str]] = mapped_column(JSON, default=list)
    review_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_tools: Mapped[list[str]] = mapped_column(JSON, default=list)
    escalation_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
