from sqlalchemy.orm import Session

from packages.domain.system_events import SystemEventRecord, SystemEventType
from packages.storage.orm_system_events import SystemEventRecordORM


class SystemEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: SystemEventRecord) -> SystemEventRecord:
        row = SystemEventRecordORM(
            id=event.id,
            event_type=event.event_type.value,
            source_arm=event.source_arm,
            source_id=event.source_id,
            summary=event.summary,
            metadata=event.metadata,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SystemEventRecord(
            id=row.id,
            event_type=SystemEventType(row.event_type),
            source_arm=row.source_arm,
            source_id=row.source_id,
            summary=row.summary,
            metadata=row.metadata or {},
        )

    def list(self) -> list[SystemEventRecord]:
        rows = self.db.query(SystemEventRecordORM).all()
        return [
            SystemEventRecord(
                id=row.id,
                event_type=SystemEventType(row.event_type),
                source_arm=row.source_arm,
                source_id=row.source_id,
                summary=row.summary,
                metadata=row.metadata or {},
            )
            for row in rows
        ]

    def list_for_source(self, source_arm: str, source_id: str) -> list[SystemEventRecord]:
        rows = self.db.query(SystemEventRecordORM).filter(
            SystemEventRecordORM.source_arm == source_arm,
            SystemEventRecordORM.source_id == source_id,
        ).all()
        return [
            SystemEventRecord(
                id=row.id,
                event_type=SystemEventType(row.event_type),
                source_arm=row.source_arm,
                source_id=row.source_id,
                summary=row.summary,
                metadata=row.metadata or {},
            )
            for row in rows
        ]
