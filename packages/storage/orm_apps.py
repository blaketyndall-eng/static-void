from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class AppRecordORM(Base):
    __tablename__ = "apps"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    app_type: Mapped[str] = mapped_column(String(80), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), index=True)
    deployment_state: Mapped[str] = mapped_column(String(40), index=True)
    version: Mapped[str] = mapped_column(String(40), default="0.1.0")
    runtime_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags_csv: Mapped[str] = mapped_column(Text, default="")
    linked_brain_modules_csv: Mapped[str] = mapped_column(Text, default="")


class AppRunORM(Base):
    __tablename__ = "app_runs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    app_id: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    output_summary: Mapped[str] = mapped_column(Text, default="")
    error_summary: Mapped[str] = mapped_column(Text, default="")


class AppAnalyticsSnapshotORM(Base):
    __tablename__ = "app_analytics_snapshots"

    app_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    sessions: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    completions: Mapped[int] = mapped_column(Integer, default=0)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    outcome_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    model_cost_estimate: Mapped[float] = mapped_column(Float, default=0.0)


class AppHealthCheckORM(Base):
    __tablename__ = "app_health_checks"

    app_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    healthy: Mapped[bool] = mapped_column(Boolean, default=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    notes_csv: Mapped[str] = mapped_column(Text, default="")


class AppFeedbackItemORM(Base):
    __tablename__ = "app_feedback_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[str] = mapped_column(String(40), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(40), default="info")
    message: Mapped[str] = mapped_column(Text)
