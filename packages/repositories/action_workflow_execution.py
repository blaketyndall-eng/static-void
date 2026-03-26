from sqlalchemy.orm import Session

from packages.domain.action_workflow_execution import (
    ActionWorkflowExecutionSnapshot,
    ActionWorkflowExecutionStatus,
    ActionWorkflowExecutionWorkspace,
)
from packages.storage.orm_action_workflow_execution import (
    ActionWorkflowExecutionSnapshotORM,
    ActionWorkflowExecutionWorkspaceORM,
)


class ActionWorkflowExecutionWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ActionWorkflowExecutionWorkspace]:
        rows = self.db.query(ActionWorkflowExecutionWorkspaceORM).order_by(ActionWorkflowExecutionWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: ActionWorkflowExecutionWorkspace) -> ActionWorkflowExecutionWorkspace:
        row = ActionWorkflowExecutionWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            execution_domains=workspace.execution_domains,
            workflow_goals=workspace.workflow_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> ActionWorkflowExecutionWorkspace | None:
        row = self.db.get(ActionWorkflowExecutionWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: ActionWorkflowExecutionStatus) -> ActionWorkflowExecutionWorkspace | None:
        row = self.db.get(ActionWorkflowExecutionWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ActionWorkflowExecutionWorkspaceORM) -> ActionWorkflowExecutionWorkspace:
        return ActionWorkflowExecutionWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=ActionWorkflowExecutionStatus(row.status),
            execution_domains=row.execution_domains or [],
            workflow_goals=row.workflow_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class ActionWorkflowExecutionSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: ActionWorkflowExecutionSnapshot) -> ActionWorkflowExecutionSnapshot:
        row = self.db.get(ActionWorkflowExecutionSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = ActionWorkflowExecutionSnapshotORM(workspace_id=snapshot.workspace_id)
        row.workflow_templates = snapshot.workflow_templates
        row.approval_checkpoints = snapshot.approval_checkpoints
        row.connector_actions = snapshot.connector_actions
        row.execution_logs = snapshot.execution_logs
        row.failure_modes = snapshot.failure_modes
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.execution_reliability_score = snapshot.execution_reliability_score
        row.approval_readiness_score = snapshot.approval_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ActionWorkflowExecutionSnapshot(
            workspace_id=row.workspace_id,
            workflow_templates=row.workflow_templates or [],
            approval_checkpoints=row.approval_checkpoints or [],
            connector_actions=row.connector_actions or [],
            execution_logs=row.execution_logs or [],
            failure_modes=row.failure_modes or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            execution_reliability_score=row.execution_reliability_score,
            approval_readiness_score=row.approval_readiness_score,
        )

    def get(self, workspace_id: str) -> ActionWorkflowExecutionSnapshot | None:
        row = self.db.get(ActionWorkflowExecutionSnapshotORM, workspace_id)
        if row is None:
            return None
        return ActionWorkflowExecutionSnapshot(
            workspace_id=row.workspace_id,
            workflow_templates=row.workflow_templates or [],
            approval_checkpoints=row.approval_checkpoints or [],
            connector_actions=row.connector_actions or [],
            execution_logs=row.execution_logs or [],
            failure_modes=row.failure_modes or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            execution_reliability_score=row.execution_reliability_score,
            approval_readiness_score=row.approval_readiness_score,
        )
