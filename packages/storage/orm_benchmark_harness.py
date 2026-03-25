from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class BenchmarkHarnessWorkspaceORM(Base):
    __tablename__ = 'benchmark_harness_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    benchmark_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    benchmark_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class BenchmarkHarnessSnapshotORM(Base):
    __tablename__ = 'benchmark_harness_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    benchmark_suites: Mapped[list[str]] = mapped_column(JSON, default=list)
    replay_datasets: Mapped[list[str]] = mapped_column(JSON, default=list)
    challenger_models: Mapped[list[str]] = mapped_column(JSON, default=list)
    rollback_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    benchmark_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    harness_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
