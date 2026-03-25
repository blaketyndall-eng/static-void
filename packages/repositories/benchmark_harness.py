from sqlalchemy.orm import Session

from packages.domain.benchmark_harness import (
    BenchmarkHarnessSnapshot,
    BenchmarkHarnessStatus,
    BenchmarkHarnessWorkspace,
)
from packages.storage.orm_benchmark_harness import (
    BenchmarkHarnessSnapshotORM,
    BenchmarkHarnessWorkspaceORM,
)


class BenchmarkHarnessWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[BenchmarkHarnessWorkspace]:
        rows = self.db.query(BenchmarkHarnessWorkspaceORM).order_by(BenchmarkHarnessWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: BenchmarkHarnessWorkspace) -> BenchmarkHarnessWorkspace:
        row = BenchmarkHarnessWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            benchmark_domains=workspace.benchmark_domains,
            benchmark_goals=workspace.benchmark_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> BenchmarkHarnessWorkspace | None:
        row = self.db.get(BenchmarkHarnessWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: BenchmarkHarnessStatus) -> BenchmarkHarnessWorkspace | None:
        row = self.db.get(BenchmarkHarnessWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: BenchmarkHarnessWorkspaceORM) -> BenchmarkHarnessWorkspace:
        return BenchmarkHarnessWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=BenchmarkHarnessStatus(row.status),
            benchmark_domains=row.benchmark_domains or [],
            benchmark_goals=row.benchmark_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class BenchmarkHarnessSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: BenchmarkHarnessSnapshot) -> BenchmarkHarnessSnapshot:
        row = self.db.get(BenchmarkHarnessSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = BenchmarkHarnessSnapshotORM(workspace_id=snapshot.workspace_id)
        row.benchmark_suites = snapshot.benchmark_suites
        row.replay_datasets = snapshot.replay_datasets
        row.challenger_models = snapshot.challenger_models
        row.rollback_rules = snapshot.rollback_rules
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.benchmark_quality_score = snapshot.benchmark_quality_score
        row.harness_readiness_score = snapshot.harness_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return BenchmarkHarnessSnapshot(
            workspace_id=row.workspace_id,
            benchmark_suites=row.benchmark_suites or [],
            replay_datasets=row.replay_datasets or [],
            challenger_models=row.challenger_models or [],
            rollback_rules=row.rollback_rules or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            benchmark_quality_score=row.benchmark_quality_score,
            harness_readiness_score=row.harness_readiness_score,
        )

    def get(self, workspace_id: str) -> BenchmarkHarnessSnapshot | None:
        row = self.db.get(BenchmarkHarnessSnapshotORM, workspace_id)
        if row is None:
            return None
        return BenchmarkHarnessSnapshot(
            workspace_id=row.workspace_id,
            benchmark_suites=row.benchmark_suites or [],
            replay_datasets=row.replay_datasets or [],
            challenger_models=row.challenger_models or [],
            rollback_rules=row.rollback_rules or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            benchmark_quality_score=row.benchmark_quality_score,
            harness_readiness_score=row.harness_readiness_score,
        )
