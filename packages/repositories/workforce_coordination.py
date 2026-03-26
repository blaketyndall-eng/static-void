from sqlalchemy.orm import Session

from packages.domain.workforce_coordination import (
    WorkforceCoordinationSnapshot,
    WorkforceCoordinationStatus,
    WorkforceCoordinationWorkspace,
)
from packages.storage.orm_workforce_coordination import (
    WorkforceCoordinationSnapshotORM,
    WorkforceCoordinationWorkspaceORM,
)


class WorkforceCoordinationWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[WorkforceCoordinationWorkspace]:
        rows = self.db.query(WorkforceCoordinationWorkspaceORM).order_by(WorkforceCoordinationWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: WorkforceCoordinationWorkspace) -> WorkforceCoordinationWorkspace:
        row = WorkforceCoordinationWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            role_groups=workspace.role_groups,
            coordination_goals=workspace.coordination_goals,
            linked_apps=workspace.linked_apps,
            linked_modules=workspace.linked_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> WorkforceCoordinationWorkspace | None:
        row = self.db.get(WorkforceCoordinationWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: WorkforceCoordinationStatus) -> WorkforceCoordinationWorkspace | None:
        row = self.db.get(WorkforceCoordinationWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: WorkforceCoordinationWorkspaceORM) -> WorkforceCoordinationWorkspace:
        return WorkforceCoordinationWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=WorkforceCoordinationStatus(row.status),
            role_groups=row.role_groups or [],
            coordination_goals=row.coordination_goals or [],
            linked_apps=row.linked_apps or [],
            linked_modules=row.linked_modules or [],
        )


class WorkforceCoordinationSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: WorkforceCoordinationSnapshot) -> WorkforceCoordinationSnapshot:
        row = self.db.get(WorkforceCoordinationSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = WorkforceCoordinationSnapshotORM(workspace_id=snapshot.workspace_id)
        row.access_rules = snapshot.access_rules
        row.spend_limits = snapshot.spend_limits
        row.routing_rules = snapshot.routing_rules
        row.work_queues = snapshot.work_queues
        row.review_points = snapshot.review_points
        row.linked_tools = snapshot.linked_tools
        row.escalation_rules = snapshot.escalation_rules
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.reliability_score = snapshot.reliability_score
        row.readiness_score = snapshot.readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return WorkforceCoordinationSnapshot(
            workspace_id=row.workspace_id,
            access_rules=row.access_rules or [],
            spend_limits=row.spend_limits or [],
            routing_rules=row.routing_rules or [],
            work_queues=row.work_queues or [],
            review_points=row.review_points or [],
            linked_tools=row.linked_tools or [],
            escalation_rules=row.escalation_rules or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            reliability_score=row.reliability_score,
            readiness_score=row.readiness_score,
        )

    def get(self, workspace_id: str) -> WorkforceCoordinationSnapshot | None:
        row = self.db.get(WorkforceCoordinationSnapshotORM, workspace_id)
        if row is None:
            return None
        return WorkforceCoordinationSnapshot(
            workspace_id=row.workspace_id,
            access_rules=row.access_rules or [],
            spend_limits=row.spend_limits or [],
            routing_rules=row.routing_rules or [],
            work_queues=row.work_queues or [],
            review_points=row.review_points or [],
            linked_tools=row.linked_tools or [],
            escalation_rules=row.escalation_rules or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            reliability_score=row.reliability_score,
            readiness_score=row.readiness_score,
        )
