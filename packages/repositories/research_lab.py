from sqlalchemy.orm import Session

from packages.domain.research_lab import (
    ResearchLabSnapshot,
    ResearchLabStatus,
    ResearchLabWorkspace,
)
from packages.storage.orm_research_lab import (
    ResearchLabSnapshotORM,
    ResearchLabWorkspaceORM,
)


class ResearchLabWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ResearchLabWorkspace]:
        rows = self.db.query(ResearchLabWorkspaceORM).order_by(ResearchLabWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: ResearchLabWorkspace) -> ResearchLabWorkspace:
        row = ResearchLabWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            experiment_domains=workspace.experiment_domains,
            benchmark_targets=workspace.benchmark_targets,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> ResearchLabWorkspace | None:
        row = self.db.get(ResearchLabWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: ResearchLabStatus) -> ResearchLabWorkspace | None:
        row = self.db.get(ResearchLabWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ResearchLabWorkspaceORM) -> ResearchLabWorkspace:
        return ResearchLabWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=ResearchLabStatus(row.status),
            experiment_domains=row.experiment_domains or [],
            benchmark_targets=row.benchmark_targets or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class ResearchLabSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: ResearchLabSnapshot) -> ResearchLabSnapshot:
        row = self.db.get(ResearchLabSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = ResearchLabSnapshotORM(workspace_id=snapshot.workspace_id)
        row.active_experiments = snapshot.active_experiments
        row.benchmark_tracks = snapshot.benchmark_tracks
        row.winning_variants = snapshot.winning_variants
        row.challenger_variants = snapshot.challenger_variants
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.experiment_quality_score = snapshot.experiment_quality_score
        row.benchmark_confidence_score = snapshot.benchmark_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ResearchLabSnapshot(
            workspace_id=row.workspace_id,
            active_experiments=row.active_experiments or [],
            benchmark_tracks=row.benchmark_tracks or [],
            winning_variants=row.winning_variants or [],
            challenger_variants=row.challenger_variants or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            experiment_quality_score=row.experiment_quality_score,
            benchmark_confidence_score=row.benchmark_confidence_score,
        )

    def get(self, workspace_id: str) -> ResearchLabSnapshot | None:
        row = self.db.get(ResearchLabSnapshotORM, workspace_id)
        if row is None:
            return None
        return ResearchLabSnapshot(
            workspace_id=row.workspace_id,
            active_experiments=row.active_experiments or [],
            benchmark_tracks=row.benchmark_tracks or [],
            winning_variants=row.winning_variants or [],
            challenger_variants=row.challenger_variants or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            experiment_quality_score=row.experiment_quality_score,
            benchmark_confidence_score=row.benchmark_confidence_score,
        )
