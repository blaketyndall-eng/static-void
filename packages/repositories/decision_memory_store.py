from sqlalchemy.orm import Session

from packages.domain.decision_memory import DecisionMemorySnapshot, DecisionMemoryStatus, DecisionMemoryWorkspace
from packages.storage.orm_decision_memory import DecisionMemorySnapshotORM, DecisionMemoryWorkspaceORM


class DecisionMemoryWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[DecisionMemoryWorkspace]:
        rows = self.db.query(DecisionMemoryWorkspaceORM).order_by(DecisionMemoryWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: DecisionMemoryWorkspace) -> DecisionMemoryWorkspace:
        row = DecisionMemoryWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            memory_domains=workspace.memory_domains,
            review_goals=workspace.review_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> DecisionMemoryWorkspace | None:
        row = self.db.get(DecisionMemoryWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: DecisionMemoryStatus) -> DecisionMemoryWorkspace | None:
        row = self.db.get(DecisionMemoryWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: DecisionMemoryWorkspaceORM) -> DecisionMemoryWorkspace:
        return DecisionMemoryWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=DecisionMemoryStatus(row.status),
            memory_domains=row.memory_domains or [],
            review_goals=row.review_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class DecisionMemorySnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: DecisionMemorySnapshot) -> DecisionMemorySnapshot:
        row = self.db.get(DecisionMemorySnapshotORM, snapshot.workspace_id)
        if row is None:
            row = DecisionMemorySnapshotORM(workspace_id=snapshot.workspace_id)
        row.captured_decisions = snapshot.captured_decisions
        row.outcome_reviews = snapshot.outcome_reviews
        row.regret_patterns = snapshot.regret_patterns
        row.reuse_candidates = snapshot.reuse_candidates
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.memory_quality_score = snapshot.memory_quality_score
        row.calibration_score = snapshot.calibration_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return DecisionMemorySnapshot(
            workspace_id=row.workspace_id,
            captured_decisions=row.captured_decisions or [],
            outcome_reviews=row.outcome_reviews or [],
            regret_patterns=row.regret_patterns or [],
            reuse_candidates=row.reuse_candidates or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            memory_quality_score=row.memory_quality_score,
            calibration_score=row.calibration_score,
        )

    def get(self, workspace_id: str) -> DecisionMemorySnapshot | None:
        row = self.db.get(DecisionMemorySnapshotORM, workspace_id)
        if row is None:
            return None
        return DecisionMemorySnapshot(
            workspace_id=row.workspace_id,
            captured_decisions=row.captured_decisions or [],
            outcome_reviews=row.outcome_reviews or [],
            regret_patterns=row.regret_patterns or [],
            reuse_candidates=row.reuse_candidates or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            memory_quality_score=row.memory_quality_score,
            calibration_score=row.calibration_score,
        )
