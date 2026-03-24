from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class SignalsForecastingWorkspaceORM(Base):
    __tablename__ = 'signals_forecasting_workspaces'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(40), index=True)
    tracked_domains: Mapped[list[str]] = mapped_column(JSON, default=list)
    forecast_targets: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class SignalsForecastingSnapshotORM(Base):
    __tablename__ = 'signals_forecasting_snapshots'

    workspace_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    trend_signals: Mapped[list[str]] = mapped_column(JSON, default=list)
    forecast_hypotheses: Mapped[list[str]] = mapped_column(JSON, default=list)
    anomaly_alerts: Mapped[list[str]] = mapped_column(JSON, default=list)
    regime_shift_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    signal_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    forecast_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
