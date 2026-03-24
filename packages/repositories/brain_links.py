from sqlalchemy.orm import Session

from packages.domain.brain_links import BrainLinkRecord, BrainLinkType, BrainModuleSummary
from packages.storage.orm_brain_links import BrainLinkRecordORM


class BrainLinkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, record: BrainLinkRecord) -> BrainLinkRecord:
        row = BrainLinkRecordORM(
            id=record.id,
            source_arm=record.source_arm,
            source_id=record.source_id,
            target_type=record.target_type.value,
            target_id=record.target_id,
            notes=record.notes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return BrainLinkRecord(
            id=row.id,
            source_arm=row.source_arm,
            source_id=row.source_id,
            target_type=BrainLinkType(row.target_type),
            target_id=row.target_id,
            notes=row.notes,
        )

    def list(self) -> list[BrainLinkRecord]:
        rows = self.db.query(BrainLinkRecordORM).all()
        return [
            BrainLinkRecord(
                id=row.id,
                source_arm=row.source_arm,
                source_id=row.source_id,
                target_type=BrainLinkType(row.target_type),
                target_id=row.target_id,
                notes=row.notes,
            )
            for row in rows
        ]

    def list_for_source(self, source_arm: str, source_id: str) -> list[BrainLinkRecord]:
        rows = self.db.query(BrainLinkRecordORM).filter(
            BrainLinkRecordORM.source_arm == source_arm,
            BrainLinkRecordORM.source_id == source_id,
        ).all()
        return [
            BrainLinkRecord(
                id=row.id,
                source_arm=row.source_arm,
                source_id=row.source_id,
                target_type=BrainLinkType(row.target_type),
                target_id=row.target_id,
                notes=row.notes,
            )
            for row in rows
        ]

    def summarize_modules(self) -> list[BrainModuleSummary]:
        records = self.list()
        buckets: dict[str, BrainModuleSummary] = {}
        for record in records:
            if record.target_type not in {BrainLinkType.app_to_module, BrainLinkType.marketing_to_module, BrainLinkType.investment_to_module}:
                continue
            summary = buckets.get(record.target_id)
            if summary is None:
                summary = BrainModuleSummary(module_name=record.target_id, linked_count=0, source_arms=[])
                buckets[record.target_id] = summary
            summary.linked_count += 1
            if record.source_arm not in summary.source_arms:
                summary.source_arms.append(record.source_arm)
        return list(buckets.values())
