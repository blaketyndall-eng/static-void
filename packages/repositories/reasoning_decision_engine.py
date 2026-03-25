from sqlalchemy.orm import Session

from packages.domain.reasoning_decision_engine import (
    ReasoningDecisionEngineSnapshot,
    ReasoningDecisionEngineStatus,
    ReasoningDecisionEngineWorkspace,
)
from packages.storage.orm_reasoning_decision_engine import (
    ReasoningDecisionEngineSnapshotORM,
    ReasoningDecisionEngineWorkspaceORM,
)


class ReasoningDecisionEngineWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ReasoningDecisionEngineWorkspace]:
        rows = self.db.query(ReasoningDecisionEngineWorkspaceORM).order_by(ReasoningDecisionEngineWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: ReasoningDecisionEngineWorkspace) -> ReasoningDecisionEngineWorkspace:
        row = ReasoningDecisionEngineWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            decision_domains=workspace.decision_domains,
            reasoning_goals=workspace.reasoning_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> ReasoningDecisionEngineWorkspace | None:
        row = self.db.get(ReasoningDecisionEngineWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: ReasoningDecisionEngineStatus) -> ReasoningDecisionEngineWorkspace | None:
        row = self.db.get(ReasoningDecisionEngineWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ReasoningDecisionEngineWorkspaceORM) -> ReasoningDecisionEngineWorkspace:
        return ReasoningDecisionEngineWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=ReasoningDecisionEngineStatus(row.status),
            decision_domains=row.decision_domains or [],
            reasoning_goals=row.reasoning_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class ReasoningDecisionEngineSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: ReasoningDecisionEngineSnapshot) -> ReasoningDecisionEngineSnapshot:
        row = self.db.get(ReasoningDecisionEngineSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = ReasoningDecisionEngineSnapshotORM(workspace_id=snapshot.workspace_id)
        row.reasoning_policies = snapshot.reasoning_policies
        row.recommendation_strategies = snapshot.recommendation_strategies
        row.confidence_rules = snapshot.confidence_rules
        row.tradeoff_models = snapshot.tradeoff_models
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.reasoning_quality_score = snapshot.reasoning_quality_score
        row.recommendation_confidence_score = snapshot.recommendation_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ReasoningDecisionEngineSnapshot(
            workspace_id=row.workspace_id,
            reasoning_policies=row.reasoning_policies or [],
            recommendation_strategies=row.recommendation_strategies or [],
            confidence_rules=row.confidence_rules or [],
            tradeoff_models=row.tradeoff_models or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            reasoning_quality_score=row.reasoning_quality_score,
            recommendation_confidence_score=row.recommendation_confidence_score,
        )

    def get(self, workspace_id: str) -> ReasoningDecisionEngineSnapshot | None:
        row = self.db.get(ReasoningDecisionEngineSnapshotORM, workspace_id)
        if row is None:
            return None
        return ReasoningDecisionEngineSnapshot(
            workspace_id=row.workspace_id,
            reasoning_policies=row.reasoning_policies or [],
            recommendation_strategies=row.recommendation_strategies or [],
            confidence_rules=row.confidence_rules or [],
            tradeoff_models=row.tradeoff_models or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            reasoning_quality_score=row.reasoning_quality_score,
            recommendation_confidence_score=row.recommendation_confidence_score,
        )
