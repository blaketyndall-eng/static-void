from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class IngestionDataAcquisitionWorkspaceORM(Base):
    __tablename__ = 'ingestion_data_acquisition_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    source_targets: Mapped[list[str]] = mapped_column(JSON, default=list)
    ingestion_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class IngestionDataAcquisitionSnapshotORM(Base):
    __tablename__ = 'ingestion_data_acquisition_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    connectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    sync_jobs: Mapped[list[str]] = mapped_column(JSON, default=list)
    normalization_pipelines: Mapped[list[str]] = mapped_column(JSON, default=list)
    freshness_windows: Mapped[list[str]] = mapped_column(JSON, default=list)
    failures: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    ingestion_health_score: Mapped[float] = mapped_column(Float, default=0.0)
    normalization_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
