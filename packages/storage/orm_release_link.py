from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class ReleaseLinkWorkspaceORM(Base):
    __tablename__ = 'release_link_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    venture_workspaces: Mapped[list[str]] = mapped_column(JSON, default=list)
    image_workspaces: Mapped[list[str]] = mapped_column(JSON, default=list)
    action_workspaces: Mapped[list[str]] = mapped_column(JSON, default=list)
    company_workspaces: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class ReleaseLinkSnapshotORM(Base):
    __tablename__ = 'release_link_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    venture_asset_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    launch_asset_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    execution_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    operating_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    approval_records: Mapped[list[str]] = mapped_column(JSON, default=list)
    distribution_targets: Mapped[list[str]] = mapped_column(JSON, default=list)
    milestone_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    blocker_links: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    integration_reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    launch_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
