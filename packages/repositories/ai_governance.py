from sqlalchemy.orm import Session

from packages.domain.ai_governance import (
    AIGovernanceSnapshot,
    AIGovernanceStatus,
    AIGovernanceWorkspace,
)
from packages.storage.orm_ai_governance import AIGovernanceSnapshotORM, AIGovernanceWorkspaceORM


class AIGovernanceWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[AIGovernanceWorkspace]:
        rows = self.db.query(AIGovernanceWorkspaceORM).order_by(AIGovernanceWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: AIGovernanceWorkspace) -> AIGovernanceWorkspace:
        row = AIGovernanceWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            model_scope=workspace.model_scope,
            evaluation_goals=workspace.evaluation_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> AIGovernanceWorkspace | None:
        row = self.db.get(AIGovernanceWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: AIGovernanceStatus) -> AIGovernanceWorkspace | None:
        row = self.db.get(AIGovernanceWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: AIGovernanceWorkspaceORM) -> AIGovernanceWorkspace:
        return AIGovernanceWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=AIGovernanceStatus(row.status),
            model_scope=row.model_scope or [],
            evaluation_goals=row.evaluation_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class AIGovernanceSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: AIGovernanceSnapshot) -> AIGovernanceSnapshot:
        row = self.db.get(AIGovernanceSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = AIGovernanceSnapshotORM(workspace_id=snapshot.workspace_id)
        row.benchmark_tracks = snapshot.benchmark_tracks
        row.policy_checks = snapshot.policy_checks
        row.monitoring_checks = snapshot.monitoring_checks
        row.risks = snapshot.risks
        row.mitigations = snapshot.mitigations
        row.notes = snapshot.notes
        row.governance_score = snapshot.governance_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AIGovernanceSnapshot(
            workspace_id=row.workspace_id,
            benchmark_tracks=row.benchmark_tracks or [],
            policy_checks=row.policy_checks or [],
            monitoring_checks=row.monitoring_checks or [],
            risks=row.risks or [],
            mitigations=row.mitigations or [],
            notes=row.notes or [],
            governance_score=row.governance_score,
        )

    def get(self, workspace_id: str) -> AIGovernanceSnapshot | None:
        row = self.db.get(AIGovernanceSnapshotORM, workspace_id)
        if row is None:
            return None
        return AIGovernanceSnapshot(
            workspace_id=row.workspace_id,
            benchmark_tracks=row.benchmark_tracks or [],
            policy_checks=row.policy_checks or [],
            monitoring_checks=row.monitoring_checks or [],
            risks=row.risks or [],
            mitigations=row.mitigations or [],
            notes=row.notes or [],
            governance_score=row.governance_score,
        )
