from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class SystemEventRecordORM(Base):
    __tablename__ = "system_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    source_arm: Mapped[str] = mapped_column(String(80), index=True)
    source_id: Mapped[str] = mapped_column(String(80), index=True)
    summary: Mapped[str] = mapped_column(Text)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
