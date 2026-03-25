from sqlalchemy.orm import Session

from packages.domain.vertical_packs import VerticalPacksSnapshot, VerticalPacksStatus, VerticalPacksWorkspace
from packages.storage.orm_verticalization import VerticalPacksSnapshotORM, VerticalPacksWorkspaceORM


class VerticalPacksWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[VerticalPacksWorkspace]:
        rows = self.db.query(VerticalPacksWorkspaceORM).order_by(VerticalPacksWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: VerticalPacksWorkspace) -> VerticalPacksWorkspace:
        row = VerticalPacksWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            industries=workspace.industries,
            pack_goals=workspace.pack_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> VerticalPacksWorkspace | None:
        row = self.db.get(VerticalPacksWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: VerticalPacksStatus) -> VerticalPacksWorkspace | None:
        row = self.db.get(VerticalPacksWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: VerticalPacksWorkspaceORM) -> VerticalPacksWorkspace:
        return VerticalPacksWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=VerticalPacksStatus(row.status),
            industries=row.industries or [],
            pack_goals=row.pack_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class VerticalPacksSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: VerticalPacksSnapshot) -> VerticalPacksSnapshot:
        row = self.db.get(VerticalPacksSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = VerticalPacksSnapshotORM(workspace_id=snapshot.workspace_id)
        row.pack_templates = snapshot.pack_templates
        row.scoring_models = snapshot.scoring_models
        row.domain_playbooks = snapshot.domain_playbooks
        row.knowledge_assets = snapshot.knowledge_assets
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.pack_quality_score = snapshot.pack_quality_score
        row.adaptation_readiness_score = snapshot.adaptation_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return VerticalPacksSnapshot(
            workspace_id=row.workspace_id,
            pack_templates=row.pack_templates or [],
            scoring_models=row.scoring_models or [],
            domain_playbooks=row.domain_playbooks or [],
            knowledge_assets=row.knowledge_assets or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            pack_quality_score=row.pack_quality_score,
            adaptation_readiness_score=row.adaptation_readiness_score,
        )

    def get(self, workspace_id: str) -> VerticalPacksSnapshot | None:
        row = self.db.get(VerticalPacksSnapshotORM, workspace_id)
        if row is None:
            return None
        return VerticalPacksSnapshot(
            workspace_id=row.workspace_id,
            pack_templates=row.pack_templates or [],
            scoring_models=row.scoring_models or [],
            domain_playbooks=row.domain_playbooks or [],
            knowledge_assets=row.knowledge_assets or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            pack_quality_score=row.pack_quality_score,
            adaptation_readiness_score=row.adaptation_readiness_score,
        )
