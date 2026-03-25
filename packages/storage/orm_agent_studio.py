from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class AgentStudioWorkspaceORM(Base):
    __tablename__ = 'agent_studio_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    agent_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    routing_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class AgentStudioSnapshotORM(Base):
    __tablename__ = 'agent_studio_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    routing_policies: Mapped[list[str]] = mapped_column(JSON, default=list)
    hitl_checkpoints: Mapped[list[str]] = mapped_column(JSON, default=list)
    replay_tracks: Mapped[list[str]] = mapped_column(JSON, default=list)
    budget_controls: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    routing_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    operator_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
