from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class FeedbackOutcomeScoringWorkspaceORM(Base):
    __tablename__ = 'feedback_outcome_scoring_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    outcome_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    scoring_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class FeedbackOutcomeScoringSnapshotORM(Base):
    __tablename__ = 'feedback_outcome_scoring_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    outcome_reviews: Mapped[list[str]] = mapped_column(JSON, default=list)
    prediction_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    usefulness_scores: Mapped[list[str]] = mapped_column(JSON, default=list)
    regret_signals: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    outcome_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    feedback_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
