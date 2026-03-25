from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class VerticalPacksWorkspaceORM(Base):
    __tablename__ = 'vertical_packs_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    pack_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class VerticalPacksSnapshotORM(Base):
    __tablename__ = 'vertical_packs_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    pack_templates: Mapped[list[str]] = mapped_column(JSON, default=list)
    scoring_models: Mapped[list[str]] = mapped_column(JSON, default=list)
    domain_playbooks: Mapped[list[str]] = mapped_column(JSON, default=list)
    knowledge_assets: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    pack_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    adaptation_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
