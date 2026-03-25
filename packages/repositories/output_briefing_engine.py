from sqlalchemy.orm import Session

from packages.domain.output_briefing_engine import (
    OutputBriefingEngineSnapshot,
    OutputBriefingEngineStatus,
    OutputBriefingEngineWorkspace,
)
from packages.storage.orm_output_briefing_engine import (
    OutputBriefingEngineSnapshotORM,
    OutputBriefingEngineWorkspaceORM,
)


class OutputBriefingEngineWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[OutputBriefingEngineWorkspace]:
        rows = self.db.query(OutputBriefingEngineWorkspaceORM).order_by(OutputBriefingEngineWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: OutputBriefingEngineWorkspace) -> OutputBriefingEngineWorkspace:
        row = OutputBriefingEngineWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            briefing_domains=workspace.briefing_domains,
            output_goals=workspace.output_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> OutputBriefingEngineWorkspace | None:
        row = self.db.get(OutputBriefingEngineWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: OutputBriefingEngineStatus) -> OutputBriefingEngineWorkspace | None:
        row = self.db.get(OutputBriefingEngineWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: OutputBriefingEngineWorkspaceORM) -> OutputBriefingEngineWorkspace:
        return OutputBriefingEngineWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=OutputBriefingEngineStatus(row.status),
            briefing_domains=row.briefing_domains or [],
            output_goals=row.output_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class OutputBriefingEngineSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: OutputBriefingEngineSnapshot) -> OutputBriefingEngineSnapshot:
        row = self.db.get(OutputBriefingEngineSnapshotORM, snapshot.workspace_id)
        if row is None:
            row = OutputBriefingEngineSnapshotORM(workspace_id=snapshot.workspace_id)
        row.briefing_templates = snapshot.briefing_templates
        row.distribution_rules = snapshot.distribution_rules
        row.alert_formats = snapshot.alert_formats
        row.evidence_packs = snapshot.evidence_packs
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.output_quality_score = snapshot.output_quality_score
        row.briefing_readiness_score = snapshot.briefing_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return OutputBriefingEngineSnapshot(
            workspace_id=row.workspace_id,
            briefing_templates=row.briefing_templates or [],
            distribution_rules=row.distribution_rules or [],
            alert_formats=row.alert_formats or [],
            evidence_packs=row.evidence_packs or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            output_quality_score=row.output_quality_score,
            briefing_readiness_score=row.briefing_readiness_score,
        )

    def get(self, workspace_id: str) -> OutputBriefingEngineSnapshot | None:
        row = self.db.get(OutputBriefingEngineSnapshotORM, workspace_id)
        if row is None:
            return None
        return OutputBriefingEngineSnapshot(
            workspace_id=row.workspace_id,
            briefing_templates=row.briefing_templates or [],
            distribution_rules=row.distribution_rules or [],
            alert_formats=row.alert_formats or [],
            evidence_packs=row.evidence_packs or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            output_quality_score=row.output_quality_score,
            briefing_readiness_score=row.briefing_readiness_score,
        )
