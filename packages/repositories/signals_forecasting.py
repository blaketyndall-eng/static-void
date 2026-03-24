from sqlalchemy.orm import Session

from packages.domain.signals_forecasting import (
    SignalsForecastingReview,
    SignalsForecastingSnapshot,
    SignalsForecastingStatus,
    SignalsForecastingWorkspace,
)
from packages.storage.orm_signals_forecasting import (
    SignalsForecastingSnapshotORM,
    SignalsForecastingWorkspaceORM,
)


class SignalsForecastingWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[SignalsForecastingWorkspace]:
        rows = self.db.query(SignalsForecastingWorkspaceORM).order_by(SignalsForecastingWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: SignalsForecastingWorkspace) -> SignalsForecastingWorkspace:
        row = SignalsForecastingWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            tracked_domains=workspace.tracked_domains,
            forecast_targets=workspace.forecast_targets,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> SignalsForecastingWorkspace | None:
        row = self.db.get(SignalsForecastingWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: SignalsForecastingStatus) -> SignalsForecastingWorkspace | None:
        row = self.db.get(SignalsForecastingWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: SignalsForecastingWorkspaceORM) -> SignalsForecastingWorkspace:
        return SignalsForecastingWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=SignalsForecastingStatus(row.status),
            tracked_domains=row.tracked_domains or [],
            forecast_targets=row.forecast_targets or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class SignalsForecastingSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: SignalsForecastingSnapshot) -> SignalsForecastingSnapshot:
        row = self.db.get(SignalsForecastingSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = SignalsForecastingSnapshotORM(workspace_id=snapshot.workspace_id)
        row.trend_signals = snapshot.trend_signals
        row.forecast_hypotheses = snapshot.forecast_hypotheses
        row.anomaly_alerts = snapshot.anomaly_alerts
        row.regime_shift_notes = snapshot.regime_shift_notes
        row.opportunities = snapshot.opportunities
        row.risks = snapshot.risks
        row.notes = snapshot.notes
        row.signal_quality_score = snapshot.signal_quality_score
        row.forecast_confidence_score = snapshot.forecast_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SignalsForecastingSnapshot(
            workspace_id=row.workspace_id,
            trend_signals=row.trend_signals or [],
            forecast_hypotheses=row.forecast_hypotheses or [],
            anomaly_alerts=row.anomaly_alerts or [],
            regime_shift_notes=row.regime_shift_notes or [],
            opportunities=row.opportunities or [],
            risks=row.risks or [],
            notes=row.notes or [],
            signal_quality_score=row.signal_quality_score,
            forecast_confidence_score=row.forecast_confidence_score,
        )

    def get(self, workspace_id: str) -> SignalsForecastingSnapshot | None:
        row = self.db.get(SignalsForecastingSnapshotORM, workspace_id)
        if row is None:
            return None
        return SignalsForecastingSnapshot(
            workspace_id=row.workspace_id,
            trend_signals=row.trend_signals or [],
            forecast_hypotheses=row.forecast_hypotheses or [],
            anomaly_alerts=row.anomaly_alerts or [],
            regime_shift_notes=row.regime_shift_notes or [],
            opportunities=row.opportunities or [],
            risks=row.risks or [],
            notes=row.notes or [],
            signal_quality_score=row.signal_quality_score,
            forecast_confidence_score=row.forecast_confidence_score,
        )
