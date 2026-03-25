from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ReasoningDecisionEngineWorkspaceORM(Base):
    __tablename__ = 'reasoning_decision_engine_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    decision_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    reasoning_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ReasoningDecisionEngineSnapshotORM(Base):
    __tablename__ = 'reasoning_decision_engine_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    reasoning_policies: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendation_strategies: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    tradeoff_models: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    reasoning_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    recommendation_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
