from sqlalchemy.orm import Session

from packages.domain.system_events import SystemEventRecord, SystemEventType
from packages.repositories.system_events import SystemEventRepository


def record_system_event(
    db: Session,
    *,
    event_type: SystemEventType,
    source_arm: str,
    source_id: str,
    summary: str,
    metadata: dict | None = None,
) -> SystemEventRecord:
    repo = SystemEventRepository(db)
    event = SystemEventRecord(
        event_type=event_type,
        source_arm=source_arm,
        source_id=source_id,
        summary=summary,
        metadata=metadata or {},
    )
    return repo.create(event)
