from sqlalchemy.orm import Session

from packages.domain.data_source_intelligence import (
    DataSourceIntelligenceSnapshot,
    DataSourceIntelligenceStatus,
    DataSourceIntelligenceWorkspace,
)
from packages.storage.orm_data_source_intelligence import (
    DataSourceIntelligenceSnapshotORM,
    DataSourceIntelligenceWorkspaceORM,
)


class DataSourceIntelligenceWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[DataSourceIntelligenceWorkspace]:
        rows = self.db.query(DataSourceIntelligenceWorkspaceORM).order_by(DataSourceIntelligenceWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: DataSourceIntelligenceWorkspace) -> DataSourceIntelligenceWorkspace:
        row = DataSourceIntelligenceWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            source_domains=workspace.source_domains,
            intelligence_goals=workspace.intelligence_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> DataSourceIntelligenceWorkspace | None:
        row = self.db.get(DataSourceIntelligenceWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: DataSourceIntelligenceStatus) -> DataSourceIntelligenceWorkspace | None:
        row = self.db.get(DataSourceIntelligenceWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: DataSourceIntelligenceWorkspaceORM) -> DataSourceIntelligenceWorkspace:
        return DataSourceIntelligenceWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=DataSourceIntelligenceStatus(row.status),
            source_domains=row.source_domains or [],
            intelligence_goals=row.intelligence_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class DataSourceIntelligenceSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: DataSourceIntelligenceSnapshot) -> DataSourceIntelligenceSnapshot:
        row = self.db.get(DataSourceIntelligenceSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = DataSourceIntelligenceSnapshotORM(workspace_id=snapshot.workspace_id)
        row.source_health_checks = snapshot.source_health_checks
        row.freshness_monitors = snapshot.freshness_monitors
        row.reliability_flags = snapshot.reliability_flags
        row.conflict_detections = snapshot.conflict_detections
        row.coverage_gaps = snapshot.coverage_gaps
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.source_quality_score = snapshot.source_quality_score
        row.freshness_confidence_score = snapshot.freshness_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return DataSourceIntelligenceSnapshot(
            workspace_id=row.workspace_id,
            source_health_checks=row.source_health_checks or [],
            freshness_monitors=row.freshness_monitors or [],
            reliability_flags=row.reliability_flags or [],
            conflict_detections=row.conflict_detections or [],
            coverage_gaps=row.coverage_gaps or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            source_quality_score=row.source_quality_score,
            freshness_confidence_score=row.freshness_confidence_score,
        )

    def get(self, workspace_id: str) -> DataSourceIntelligenceSnapshot | None:
        row = self.db.get(DataSourceIntelligenceSnapshotORM, workspace_id)
        if row is None:
            return None
        return DataSourceIntelligenceSnapshot(
            workspace_id=row.workspace_id,
            source_health_checks=row.source_health_checks or [],
            freshness_monitors=row.freshness_monitors or [],
            reliability_flags=row.reliability_flags or [],
            conflict_detections=row.conflict_detections or [],
            coverage_gaps=row.coverage_gaps or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            source_quality_score=row.source_quality_score,
            freshness_confidence_score=row.freshness_confidence_score,
        )
