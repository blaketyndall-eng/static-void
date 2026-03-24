from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class AIGovernanceWorkspaceORM(Base):
    __tablename__ = 'ai_governance_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    model_scope: Mapped[list[str]] = mapped_column(JSON, default=list)
    evaluation_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class AIGovernanceSnapshotORM(Base):
    __tablename__ = 'ai_governance_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    benchmark_tracks: Mapped[list[str]] = mapped_column(JSON, default=list)
    policy_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    monitoring_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    mitigations: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    governance_score: Mapped[float] = mapped_column(Float, default=0.0)
