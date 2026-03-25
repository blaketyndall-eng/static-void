from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class IntegrationsAutomationWorkspaceORM(Base):
    __tablename__ = 'integrations_automation_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    integration_targets: Mapped[list[str]] = mapped_column(JSON, default=list)
    automation_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class IntegrationsAutomationSnapshotORM(Base):
    __tablename__ = 'integrations_automation_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    integration_health_checks: Mapped[list[str]] = mapped_column(JSON, default=list)
    automation_workflows: Mapped[list[str]] = mapped_column(JSON, default=list)
    webhook_endpoints: Mapped[list[str]] = mapped_column(JSON, default=list)
    freshness_alerts: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    integration_health_score: Mapped[float] = mapped_column(Float, default=0.0)
    automation_reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
