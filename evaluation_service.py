from typing import Any

from domain_models import EvaluationRecord, EvaluationStatus, new_id


class EvaluationService:
    def __init__(self) -> None:
        self._evaluations: dict[str, EvaluationRecord] = {}

    def create(
        self,
        *,
        title: str,
        decision_owner: str | None = None,
        criteria: list[dict[str, Any]] | None = None,
    ) -> EvaluationRecord:
        record = EvaluationRecord(
            id=new_id("eval"),
            title=title,
            decision_owner=decision_owner,
            criteria=criteria or [],
        )
        self._evaluations[record.id] = record
        return record

    def list(self) -> list[EvaluationRecord]:
        return list(self._evaluations.values())

    def update_status(self, evaluation_id: str, status: EvaluationStatus) -> EvaluationRecord | None:
        record = self._evaluations.get(evaluation_id)
        if record is None:
            return None
        record.status = status
        return record

    def attach_evidence(self, evaluation_id: str, evidence_id: str) -> EvaluationRecord | None:
        record = self._evaluations.get(evaluation_id)
        if record is None:
            return None
        record.evidence_ids.append(evidence_id)
        return record
