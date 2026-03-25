from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class BiasJudgmentQualityWorkspaceORM(Base):
    __tablename__ = 'bias_judgment_quality_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    judgment_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    quality_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class BiasJudgmentQualitySnapshotORM(Base):
    __tablename__ = 'bias_judgment_quality_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    bias_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    calibration_rules: Mapped[list[str]] = mapped_column(JSON, default=list)
    dissent_prompts: Mapped[list[str]] = mapped_column(JSON, default=list)
    assumption_audits: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    judgment_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    calibration_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
