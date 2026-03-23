from domain_models import OpportunityRecord, OpportunityStage, new_id


class OpportunityService:
    def __init__(self) -> None:
        self._opportunities: dict[str, OpportunityRecord] = {}

    def create(
        self,
        *,
        title: str,
        summary: str,
        source_ids: list[str] | None = None,
        themes: list[str] | None = None,
        score: float | None = None,
    ) -> OpportunityRecord:
        record = OpportunityRecord(
            id=new_id("opp"),
            title=title,
            summary=summary,
            source_ids=source_ids or [],
            themes=themes or [],
            score=score,
        )
        self._opportunities[record.id] = record
        return record

    def list(self) -> list[OpportunityRecord]:
        return list(self._opportunities.values())

    def update_stage(self, opportunity_id: str, stage: OpportunityStage) -> OpportunityRecord | None:
        record = self._opportunities.get(opportunity_id)
        if record is None:
            return None
        record.stage = stage
        return record
