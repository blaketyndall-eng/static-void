from sqlalchemy.orm import Session

from packages.domain.company_operator import CompanyOperatorSnapshot, CompanyOperatorStatus, CompanyOperatorWorkspace
from packages.storage.orm_company_operator_v2 import CompanyOperatorSnapshotORM, CompanyOperatorWorkspaceORM


class CompanyOperatorWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[CompanyOperatorWorkspace]:
        rows = self.db.query(CompanyOperatorWorkspaceORM).order_by(CompanyOperatorWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: CompanyOperatorWorkspace) -> CompanyOperatorWorkspace:
        row = CompanyOperatorWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            company_names=workspace.company_names,
            operating_goals=workspace.operating_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> CompanyOperatorWorkspace | None:
        row = self.db.get(CompanyOperatorWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: CompanyOperatorStatus) -> CompanyOperatorWorkspace | None:
        row = self.db.get(CompanyOperatorWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: CompanyOperatorWorkspaceORM) -> CompanyOperatorWorkspace:
        return CompanyOperatorWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=CompanyOperatorStatus(row.status),
            company_names=row.company_names or [],
            operating_goals=row.operating_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class CompanyOperatorSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: CompanyOperatorSnapshot) -> CompanyOperatorSnapshot:
        row = self.db.get(CompanyOperatorSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = CompanyOperatorSnapshotORM(workspace_id=snapshot.workspace_id)
        row.company_goals = snapshot.company_goals
        row.operating_cadences = snapshot.operating_cadences
        row.kpis = snapshot.kpis
        row.initiatives = snapshot.initiatives
        row.owners = snapshot.owners
        row.blockers = snapshot.blockers
        row.decision_execution_links = snapshot.decision_execution_links
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.operating_health_score = snapshot.operating_health_score
        row.execution_alignment_score = snapshot.execution_alignment_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return CompanyOperatorSnapshot(
            workspace_id=row.workspace_id,
            company_goals=row.company_goals or [],
            operating_cadences=row.operating_cadences or [],
            kpis=row.kpis or [],
            initiatives=row.initiatives or [],
            owners=row.owners or [],
            blockers=row.blockers or [],
            decision_execution_links=row.decision_execution_links or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            operating_health_score=row.operating_health_score,
            execution_alignment_score=row.execution_alignment_score,
        )

    def get(self, workspace_id: str) -> CompanyOperatorSnapshot | None:
        row = self.db.get(CompanyOperatorSnapshotORM, workspace_id)
        if row is None:
            return None
        return CompanyOperatorSnapshot(
            workspace_id=row.workspace_id,
            company_goals=row.company_goals or [],
            operating_cadences=row.operating_cadences or [],
            kpis=row.kpis or [],
            initiatives=row.initiatives or [],
            owners=row.owners or [],
            blockers=row.blockers or [],
            decision_execution_links=row.decision_execution_links or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            operating_health_score=row.operating_health_score,
            execution_alignment_score=row.execution_alignment_score,
        )
