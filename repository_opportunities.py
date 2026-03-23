from sqlalchemy.orm import Session

from db_models_sqlalchemy import OpportunityORM
from domain_models import OpportunityRecord, OpportunityStage


class OpportunityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[OpportunityRecord]:
        rows = self.db.query(OpportunityORM).order_by(OpportunityORM.title.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, *, opportunity: OpportunityRecord) -> OpportunityRecord:
        row = OpportunityORM(
            id=opportunity.id,
            title=opportunity.title,
            summary=opportunity.summary,
            stage=opportunity.stage.value,
            score=opportunity.score,
            source_ids=opportunity.source_ids,
            themes=opportunity.themes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, opportunity_id: str) -> OpportunityRecord | None:
        row = self.db.get(OpportunityORM, opportunity_id)
        if row is None:
            return None
        return self._to_domain(row)

    def update_stage(
        self, opportunity_id: str, stage: OpportunityStage
    ) -> OpportunityRecord | None:
        row = self.db.get(OpportunityORM, opportunity_id)
        if row is None:
            return None
        row.stage = stage.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: OpportunityORM) -> OpportunityRecord:
        return OpportunityRecord(
            id=row.id,
            title=row.title,
            summary=row.summary,
            stage=OpportunityStage(row.stage),
            score=row.score,
            source_ids=row.source_ids or [],
            themes=row.themes or [],
        )
