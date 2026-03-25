from sqlalchemy.orm import Session

from packages.domain.agent_studio import AgentStudioSnapshot, AgentStudioStatus, AgentStudioWorkspace
from packages.storage.orm_agent_studio import AgentStudioSnapshotORM, AgentStudioWorkspaceORM


class AgentStudioWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[AgentStudioWorkspace]:
        rows = self.db.query(AgentStudioWorkspaceORM).order_by(AgentStudioWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: AgentStudioWorkspace) -> AgentStudioWorkspace:
        row = AgentStudioWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            agent_roles=workspace.agent_roles,
            routing_goals=workspace.routing_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> AgentStudioWorkspace | None:
        row = self.db.get(AgentStudioWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: AgentStudioStatus) -> AgentStudioWorkspace | None:
        row = self.db.get(AgentStudioWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: AgentStudioWorkspaceORM) -> AgentStudioWorkspace:
        return AgentStudioWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=AgentStudioStatus(row.status),
            agent_roles=row.agent_roles or [],
            routing_goals=row.routing_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class AgentStudioSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: AgentStudioSnapshot) -> AgentStudioSnapshot:
        row = self.db.get(AgentStudioSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = AgentStudioSnapshotORM(workspace_id=snapshot.workspace_id)
        row.routing_policies = snapshot.routing_policies
        row.hitl_checkpoints = snapshot.hitl_checkpoints
        row.replay_tracks = snapshot.replay_tracks
        row.budget_controls = snapshot.budget_controls
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.routing_quality_score = snapshot.routing_quality_score
        row.operator_confidence_score = snapshot.operator_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AgentStudioSnapshot(
            workspace_id=row.workspace_id,
            routing_policies=row.routing_policies or [],
            hitl_checkpoints=row.hitl_checkpoints or [],
            replay_tracks=row.replay_tracks or [],
            budget_controls=row.budget_controls or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            routing_quality_score=row.routing_quality_score,
            operator_confidence_score=row.operator_confidence_score,
        )

    def get(self, workspace_id: str) -> AgentStudioSnapshot | None:
        row = self.db.get(AgentStudioSnapshotORM, workspace_id)
        if row is None:
            return None
        return AgentStudioSnapshot(
            workspace_id=row.workspace_id,
            routing_policies=row.routing_policies or [],
            hitl_checkpoints=row.hitl_checkpoints or [],
            replay_tracks=row.replay_tracks or [],
            budget_controls=row.budget_controls or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            routing_quality_score=row.routing_quality_score,
            operator_confidence_score=row.operator_confidence_score,
        )
