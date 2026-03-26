from sqlalchemy.orm import Session

from packages.domain.feedback_outcome_scoring import (
    FeedbackOutcomeScoringSnapshot,
    FeedbackOutcomeScoringStatus,
    FeedbackOutcomeScoringWorkspace,
)
from packages.storage.orm_feedback_outcome_scoring import (
    FeedbackOutcomeScoringSnapshotORM,
    FeedbackOutcomeScoringWorkspaceORM,
)


class FeedbackOutcomeScoringWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[FeedbackOutcomeScoringWorkspace]:
        rows = self.db.query(FeedbackOutcomeScoringWorkspaceORM).order_by(FeedbackOutcomeScoringWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: FeedbackOutcomeScoringWorkspace) -> FeedbackOutcomeScoringWorkspace:
        row = FeedbackOutcomeScoringWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            outcome_domains=workspace.outcome_domains,
            scoring_goals=workspace.scoring_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> FeedbackOutcomeScoringWorkspace | None:
        row = self.db.get(FeedbackOutcomeScoringWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: FeedbackOutcomeScoringStatus) -> FeedbackOutcomeScoringWorkspace | None:
        row = self.db.get(FeedbackOutcomeScoringWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: FeedbackOutcomeScoringWorkspaceORM) -> FeedbackOutcomeScoringWorkspace:
        return FeedbackOutcomeScoringWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=FeedbackOutcomeScoringStatus(row.status),
            outcome_domains=row.outcome_domains or [],
            scoring_goals=row.scoring_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class FeedbackOutcomeScoringSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: FeedbackOutcomeScoringSnapshot) -> FeedbackOutcomeScoringSnapshot:
        row = self.db.get(FeedbackOutcomeScoringSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = FeedbackOutcomeScoringSnapshotORM(workspace_id=snapshot.workspace_id)
        row.outcome_reviews = snapshot.outcome_reviews
        row.prediction_checks = snapshot.prediction_checks
        row.usefulness_scores = snapshot.usefulness_scores
        row.regret_signals = snapshot.regret_signals
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.outcome_quality_score = snapshot.outcome_quality_score
        row.feedback_readiness_score = snapshot.feedback_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return FeedbackOutcomeScoringSnapshot(
            workspace_id=row.workspace_id,
            outcome_reviews=row.outcome_reviews or [],
            prediction_checks=row.prediction_checks or [],
            usefulness_scores=row.usefulness_scores or [],
            regret_signals=row.regret_signals or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            outcome_quality_score=row.outcome_quality_score,
            feedback_readiness_score=row.feedback_readiness_score,
        )

    def get(self, workspace_id: str) -> FeedbackOutcomeScoringSnapshot | None:
        row = self.db.get(FeedbackOutcomeScoringSnapshotORM, workspace_id)
        if row is None:
            return None
        return FeedbackOutcomeScoringSnapshot(
            workspace_id=row.workspace_id,
            outcome_reviews=row.outcome_reviews or [],
            prediction_checks=row.prediction_checks or [],
            usefulness_scores=row.usefulness_scores or [],
            regret_signals=row.regret_signals or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            outcome_quality_score=row.outcome_quality_score,
            feedback_readiness_score=row.feedback_readiness_score,
        )
