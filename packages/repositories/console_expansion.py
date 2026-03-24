from sqlalchemy.orm import Session

from packages.domain.console_expansion import (
    ConsoleArmSnapshot,
    ConsoleArmStatus,
    ConsoleArmType,
    ConsoleArmWorkspace,
)
from packages.storage.orm_console_expansion import ConsoleArmSnapshotORM, ConsoleArmWorkspaceORM


class ConsoleArmWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ConsoleArmWorkspace]:
        rows = self.db.query(ConsoleArmWorkspaceORM).order_by(ConsoleArmWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: ConsoleArmWorkspace) -> ConsoleArmWorkspace:
        row = ConsoleArmWorkspaceORM(
            id=workspace.id,
            arm_type=workspace.arm_type.value,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            goals=workspace.goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> ConsoleArmWorkspace | None:
        row = self.db.get(ConsoleArmWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: ConsoleArmStatus) -> ConsoleArmWorkspace | None:
        row = self.db.get(ConsoleArmWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ConsoleArmWorkspaceORM) -> ConsoleArmWorkspace:
        return ConsoleArmWorkspace(
            id=row.id,
            arm_type=ConsoleArmType(row.arm_type),
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=ConsoleArmStatus(row.status),
            goals=row.goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class ConsoleArmSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: ConsoleArmSnapshot) -> ConsoleArmSnapshot:
        row = self.db.get(ConsoleArmSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = ConsoleArmSnapshotORM(workspace_id=snapshot.workspace_id)
        row.focus_areas = snapshot.focus_areas
        row.active_tracks = snapshot.active_tracks
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.maturity_score = snapshot.maturity_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ConsoleArmSnapshot(
            workspace_id=row.workspace_id,
            focus_areas=row.focus_areas or [],
            active_tracks=row.active_tracks or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            maturity_score=row.maturity_score,
        )

    def get(self, workspace_id: str) -> ConsoleArmSnapshot | None:
        row = self.db.get(ConsoleArmSnapshotORM, workspace_id)
        if row is None:
            return None
        return ConsoleArmSnapshot(
            workspace_id=row.workspace_id,
            focus_areas=row.focus_areas or [],
            active_tracks=row.active_tracks or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            maturity_score=row.maturity_score,
        )
