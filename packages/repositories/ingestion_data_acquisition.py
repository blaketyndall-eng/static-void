from sqlalchemy.orm import Session

from packages.domain.ingestion_data_acquisition import (
    IngestionDataAcquisitionSnapshot,
    IngestionDataAcquisitionStatus,
    IngestionDataAcquisitionWorkspace,
)
from packages.storage.orm_ingestion_data_acquisition import (
    IngestionDataAcquisitionSnapshotORM,
    IngestionDataAcquisitionWorkspaceORM,
)


class IngestionDataAcquisitionWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[IngestionDataAcquisitionWorkspace]:
        rows = self.db.query(IngestionDataAcquisitionWorkspaceORM).order_by(IngestionDataAcquisitionWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: IngestionDataAcquisitionWorkspace) -> IngestionDataAcquisitionWorkspace:
        row = IngestionDataAcquisitionWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            source_targets=workspace.source_targets,
            ingestion_goals=workspace.ingestion_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> IngestionDataAcquisitionWorkspace | None:
        row = self.db.get(IngestionDataAcquisitionWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: IngestionDataAcquisitionStatus) -> IngestionDataAcquisitionWorkspace | None:
        row = self.db.get(IngestionDataAcquisitionWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: IngestionDataAcquisitionWorkspaceORM) -> IngestionDataAcquisitionWorkspace:
        return IngestionDataAcquisitionWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=IngestionDataAcquisitionStatus(row.status),
            source_targets=row.source_targets or [],
            ingestion_goals=row.ingestion_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class IngestionDataAcquisitionSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: IngestionDataAcquisitionSnapshot) -> IngestionDataAcquisitionSnapshot:
        row = self.db.get(IngestionDataAcquisitionSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = IngestionDataAcquisitionSnapshotORM(workspace_id=snapshot.workspace_id)
        row.connectors = snapshot.connectors
        row.sync_jobs = snapshot.sync_jobs
        row.normalization_pipelines = snapshot.normalization_pipelines
        row.freshness_windows = snapshot.freshness_windows
        row.failures = snapshot.failures
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.ingestion_health_score = snapshot.ingestion_health_score
        row.normalization_readiness_score = snapshot.normalization_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return IngestionDataAcquisitionSnapshot(
            workspace_id=row.workspace_id,
            connectors=row.connectors or [],
            sync_jobs=row.sync_jobs or [],
            normalization_pipelines=row.normalization_pipelines or [],
            freshness_windows=row.freshness_windows or [],
            failures=row.failures or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            ingestion_health_score=row.ingestion_health_score,
            normalization_readiness_score=row.normalization_readiness_score,
        )

    def get(self, workspace_id: str) -> IngestionDataAcquisitionSnapshot | None:
        row = self.db.get(IngestionDataAcquisitionSnapshotORM, workspace_id)
        if row is None:
            return None
        return IngestionDataAcquisitionSnapshot(
            workspace_id=row.workspace_id,
            connectors=row.connectors or [],
            sync_jobs=row.sync_jobs or [],
            normalization_pipelines=row.normalization_pipelines or [],
            freshness_windows=row.freshness_windows or [],
            failures=row.failures or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            ingestion_health_score=row.ingestion_health_score,
            normalization_readiness_score=row.normalization_readiness_score,
        )
