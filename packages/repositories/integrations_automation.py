from sqlalchemy.orm import Session

from packages.domain.integrations_automation import (
    IntegrationsAutomationSnapshot,
    IntegrationsAutomationStatus,
    IntegrationsAutomationWorkspace,
)
from packages.storage.orm_integrations_automation import (
    IntegrationsAutomationSnapshotORM,
    IntegrationsAutomationWorkspaceORM,
)


class IntegrationsAutomationWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[IntegrationsAutomationWorkspace]:
        rows = self.db.query(IntegrationsAutomationWorkspaceORM).order_by(IntegrationsAutomationWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: IntegrationsAutomationWorkspace) -> IntegrationsAutomationWorkspace:
        row = IntegrationsAutomationWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            integration_targets=workspace.integration_targets,
            automation_goals=workspace.automation_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> IntegrationsAutomationWorkspace | None:
        row = self.db.get(IntegrationsAutomationWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: IntegrationsAutomationStatus) -> IntegrationsAutomationWorkspace | None:
        row = self.db.get(IntegrationsAutomationWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: IntegrationsAutomationWorkspaceORM) -> IntegrationsAutomationWorkspace:
        return IntegrationsAutomationWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=IntegrationsAutomationStatus(row.status),
            integration_targets=row.integration_targets or [],
            automation_goals=row.automation_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class IntegrationsAutomationSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: IntegrationsAutomationSnapshot) -> IntegrationsAutomationSnapshot:
        row = self.db.get(IntegrationsAutomationSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = IntegrationsAutomationSnapshotORM(workspace_id=snapshot.workspace_id)
        row.integration_health_checks = snapshot.integration_health_checks
        row.automation_workflows = snapshot.automation_workflows
        row.webhook_endpoints = snapshot.webhook_endpoints
        row.freshness_alerts = snapshot.freshness_alerts
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.integration_health_score = snapshot.integration_health_score
        row.automation_reliability_score = snapshot.automation_reliability_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return IntegrationsAutomationSnapshot(
            workspace_id=row.workspace_id,
            integration_health_checks=row.integration_health_checks or [],
            automation_workflows=row.automation_workflows or [],
            webhook_endpoints=row.webhook_endpoints or [],
            freshness_alerts=row.freshness_alerts or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            integration_health_score=row.integration_health_score,
            automation_reliability_score=row.automation_reliability_score,
        )

    def get(self, workspace_id: str) -> IntegrationsAutomationSnapshot | None:
        row = self.db.get(IntegrationsAutomationSnapshotORM, workspace_id)
        if row is None:
            return None
        return IntegrationsAutomationSnapshot(
            workspace_id=row.workspace_id,
            integration_health_checks=row.integration_health_checks or [],
            automation_workflows=row.automation_workflows or [],
            webhook_endpoints=row.webhook_endpoints or [],
            freshness_alerts=row.freshness_alerts or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            integration_health_score=row.integration_health_score,
            automation_reliability_score=row.automation_reliability_score,
        )
