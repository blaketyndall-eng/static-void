from sqlalchemy.orm import Session

from packages.domain.venture_builder import (
    VentureBuilderSnapshot,
    VentureBuilderStatus,
    VentureBuilderWorkspace,
)
from packages.storage.orm_venture_builder import (
    VentureBuilderSnapshotORM,
    VentureBuilderWorkspaceORM,
)


class VentureBuilderWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[VentureBuilderWorkspace]:
        rows = self.db.query(VentureBuilderWorkspaceORM).order_by(VentureBuilderWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: VentureBuilderWorkspace) -> VentureBuilderWorkspace:
        row = VentureBuilderWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            venture_ideas=workspace.venture_ideas,
            thesis_points=workspace.thesis_points,
            linked_apps=workspace.linked_apps,
            linked_modules=workspace.linked_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> VentureBuilderWorkspace | None:
        row = self.db.get(VentureBuilderWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: VentureBuilderStatus) -> VentureBuilderWorkspace | None:
        row = self.db.get(VentureBuilderWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: VentureBuilderWorkspaceORM) -> VentureBuilderWorkspace:
        return VentureBuilderWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=VentureBuilderStatus(row.status),
            venture_ideas=row.venture_ideas or [],
            thesis_points=row.thesis_points or [],
            linked_apps=row.linked_apps or [],
            linked_modules=row.linked_modules or [],
        )


class VentureBuilderSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: VentureBuilderSnapshot) -> VentureBuilderSnapshot:
        row = self.db.get(VentureBuilderSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = VentureBuilderSnapshotORM(workspace_id=snapshot.workspace_id)
        row.stages = snapshot.stages
        row.launch_milestones = snapshot.launch_milestones
        row.owners = snapshot.owners
        row.dependencies = snapshot.dependencies
        row.blockers = snapshot.blockers
        row.go_no_go_evidence = snapshot.go_no_go_evidence
        row.decision_launch_links = snapshot.decision_launch_links
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.launch_readiness_score = snapshot.launch_readiness_score
        row.venture_confidence_score = snapshot.venture_confidence_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return VentureBuilderSnapshot(
            workspace_id=row.workspace_id,
            stages=row.stages or [],
            launch_milestones=row.launch_milestones or [],
            owners=row.owners or [],
            dependencies=row.dependencies or [],
            blockers=row.blockers or [],
            go_no_go_evidence=row.go_no_go_evidence or [],
            decision_launch_links=row.decision_launch_links or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            launch_readiness_score=row.launch_readiness_score,
            venture_confidence_score=row.venture_confidence_score,
        )

    def get(self, workspace_id: str) -> VentureBuilderSnapshot | None:
        row = self.db.get(VentureBuilderSnapshotORM, workspace_id)
        if row is None:
            return None
        return VentureBuilderSnapshot(
            workspace_id=row.workspace_id,
            stages=row.stages or [],
            launch_milestones=row.launch_milestones or [],
            owners=row.owners or [],
            dependencies=row.dependencies or [],
            blockers=row.blockers or [],
            go_no_go_evidence=row.go_no_go_evidence or [],
            decision_launch_links=row.decision_launch_links or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            launch_readiness_score=row.launch_readiness_score,
            venture_confidence_score=row.venture_confidence_score,
        )
