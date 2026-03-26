from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ActionWorkflowExecutionWorkspaceORM(Base):
    __tablename__ = 'action_workflow_execution_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    execution_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    workflow_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ActionWorkflowExecutionSnapshotORM(Base):
    __tablename__ = 'action_workflow_execution_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    workflow_templates: Mapped[list[str]] = mapped_column(JSON, default=list)
    approval_checkpoints: Mapped[list[str]] = mapped_column(JSON, default=list)
    connector_actions: Mapped[list[str]] = mapped_column(JSON, default=list)
    execution_logs: Mapped[list[str]] = mapped_column(JSON, default=list)
    failure_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    execution_reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    approval_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
