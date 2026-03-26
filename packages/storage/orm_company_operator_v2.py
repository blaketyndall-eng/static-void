from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class CompanyOperatorWorkspaceORM(Base):
    __tablename__ = 'company_operator_workspaces_v2'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    company_names: Mapped[list[str]] = mapped_column(JSON, default=list)
    operating_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class CompanyOperatorSnapshotORM(Base):
    __tablename__ = 'company_operator_snapshots_v2'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    company_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    operating_cadences: Mapped[list[str]] = mapped_column(JSON, default=list)
    kpis: Mapped[list[str]] = mapped_column(JSON, default=list)
    initiatives: Mapped[list[str]] = mapped_column(JSON, default=list)
    owners: Mapped[list[str]] = mapped_column(JSON, default=list)
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    decision_execution_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    operating_health_score: Mapped[float] = mapped_column(Float, default=0.0)
    execution_alignment_score: Mapped[float] = mapped_column(Float, default=0.0)
