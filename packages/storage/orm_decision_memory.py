from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class DecisionMemoryWorkspaceORM(Base):
    __tablename__ = 'decision_memory_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    memory_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    review_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class DecisionMemorySnapshotORM(Base):
    __tablename__ = 'decision_memory_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    captured_decisions: Mapped[list[str]] = mapped_column(JSON, default=list)
    outcome_reviews: Mapped[list[str]] = mapped_column(JSON, default=list)
    regret_patterns: Mapped[list[str]] = mapped_column(JSON, default=list)
    reuse_candidates: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    memory_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    calibration_score: Mapped[float] = mapped_column(Float, default=0.0)
