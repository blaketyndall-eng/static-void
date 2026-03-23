from sqlalchemy.orm import Session

from packages.domain.core import SourceRecord, SourceType
from packages.storage.orm_core import SourceORM


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[SourceRecord]:
        rows = self.db.query(SourceORM).order_by(SourceORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, *, source: SourceRecord) -> SourceRecord:
        row = SourceORM(
            id=source.id,
            name=source.name,
            source_type=source.source_type.value,
            trust_score=source.trust_score,
            freshness_label=source.freshness_label,
            owner=source.owner,
            notes=source.notes,
            tags=source.tags,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, source_id: str) -> SourceRecord | None:
        row = self.db.get(SourceORM, source_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: SourceORM) -> SourceRecord:
        return SourceRecord(
            id=row.id,
            name=row.name,
            source_type=SourceType(row.source_type),
            trust_score=row.trust_score,
            freshness_label=row.freshness_label,
            owner=row.owner,
            notes=row.notes,
            tags=row.tags or [],
        )
