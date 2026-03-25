from sqlalchemy.orm import Session

from packages.domain.bias_judgment_quality import (
    BiasJudgmentQualitySnapshot,
    BiasJudgmentQualityStatus,
    BiasJudgmentQualityWorkspace,
)
from packages.storage.orm_bias_judgment_quality import (
    BiasJudgmentQualitySnapshotORM,
    BiasJudgmentQualityWorkspaceORM,
)


class BiasJudgmentQualityWorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[BiasJudgmentQualityWorkspace]:
        rows = self.db.query(BiasJudgmentQualityWorkspaceORM).order_by(BiasJudgmentQualityWorkspaceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, workspace: BiasJudgmentQualityWorkspace) -> BiasJudgmentQualityWorkspace:
        row = BiasJudgmentQualityWorkspaceORM(
            id=workspace.id,
            name=workspace.name,
            owner=workspace.owner,
            description=workspace.description,
            status=workspace.status.value,
            judgment_domains=workspace.judgment_domains,
            quality_goals=workspace.quality_goals,
            linked_apps=workspace.linked_apps,
            linked_brain_modules=workspace.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, workspace_id: str) -> BiasJudgmentQualityWorkspace | None:
        row = self.db.get(BiasJudgmentQualityWorkspaceORM, workspace_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, workspace_id: str, status: BiasJudgmentQualityStatus) -> BiasJudgmentQualityWorkspace | None:
        row = self.db.get(BiasJudgmentQualityWorkspaceORM, workspace_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: BiasJudgmentQualityWorkspaceORM) -> BiasJudgmentQualityWorkspace:
        return BiasJudgmentQualityWorkspace(
            id=row.id,
            name=row.name,
            owner=row.owner,
            description=row.description,
            status=BiasJudgmentQualityStatus(row.status),
            judgment_domains=row.judgment_domains or [],
            quality_goals=row.quality_goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class BiasJudgmentQualitySnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, snapshot: BiasJudgmentQualitySnapshot) -> BiasJudgmentQualitySnapshot:
        row = self.db.get(BiasJudgmentQualitySnapshotORM, snapshot.workspace_id)
        if row is None:
            row = BiasJudgmentQualitySnapshotORM(workspace_id=snapshot.workspace_id)
        row.bias_checks = snapshot.bias_checks
        row.calibration_rules = snapshot.calibration_rules
        row.dissent_prompts = snapshot.dissent_prompts
        row.assumption_audits = snapshot.assumption_audits
        row.risks = snapshot.risks
        row.opportunities = snapshot.opportunities
        row.notes = snapshot.notes
        row.judgment_quality_score = snapshot.judgment_quality_score
        row.calibration_readiness_score = snapshot.calibration_readiness_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return BiasJudgmentQualitySnapshot(
            workspace_id=row.workspace_id,
            bias_checks=row.bias_checks or [],
            calibration_rules=row.calibration_rules or [],
            dissent_prompts=row.dissent_prompts or [],
            assumption_audits=row.assumption_audits or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            judgment_quality_score=row.judgment_quality_score,
            calibration_readiness_score=row.calibration_readiness_score,
        )

    def get(self, workspace_id: str) -> BiasJudgmentQualitySnapshot | None:
        row = self.db.get(BiasJudgmentQualitySnapshotORM, workspace_id)
        if row is None:
            return None
        return BiasJudgmentQualitySnapshot(
            workspace_id=row.workspace_id,
            bias_checks=row.bias_checks or [],
            calibration_rules=row.calibration_rules or [],
            dissent_prompts=row.dissent_prompts or [],
            assumption_audits=row.assumption_audits or [],
            risks=row.risks or [],
            opportunities=row.opportunities or [],
            notes=row.notes or [],
            judgment_quality_score=row.judgment_quality_score,
            calibration_readiness_score=row.calibration_readiness_score,
        )
