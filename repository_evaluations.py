from sqlalchemy.orm import Session

from db_models_sqlalchemy import EvaluationORM
from domain_models import EvaluationRecord, EvaluationStatus


class EvaluationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[EvaluationRecord]:
        rows = self.db.query(EvaluationORM).order_by(EvaluationORM.title.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, *, evaluation: EvaluationRecord) -> EvaluationRecord:
        row = EvaluationORM(
            id=evaluation.id,
            title=evaluation.title,
            status=evaluation.status.value,
            decision_owner=evaluation.decision_owner,
            criteria=evaluation.criteria,
            evidence_ids=evaluation.evidence_ids,
            recommendation_summary=evaluation.recommendation_summary,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, evaluation_id: str) -> EvaluationRecord | None:
        row = self.db.get(EvaluationORM, evaluation_id)
        if row is None:
            return None
        return self._to_domain(row)

    def update_status(
        self, evaluation_id: str, status: EvaluationStatus
    ) -> EvaluationRecord | None:
        row = self.db.get(EvaluationORM, evaluation_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def attach_evidence(self, evaluation_id: str, evidence_id: str) -> EvaluationRecord | None:
        row = self.db.get(EvaluationORM, evaluation_id)
        if row is None:
            return None
        current = row.evidence_ids or []
        row.evidence_ids = [*current, evidence_id]
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: EvaluationORM) -> EvaluationRecord:
        return EvaluationRecord(
            id=row.id,
            title=row.title,
            status=EvaluationStatus(row.status),
            decision_owner=row.decision_owner,
            criteria=row.criteria or [],
            evidence_ids=row.evidence_ids or [],
            recommendation_summary=row.recommendation_summary,
        )
