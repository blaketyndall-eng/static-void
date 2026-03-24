from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class BrainLinkRecordORM(Base):
    __tablename__ = "brain_links"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    source_arm: Mapped[str] = mapped_column(String(80), index=True)
    source_id: Mapped[str] = mapped_column(String(80), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True)
    target_id: Mapped[str] = mapped_column(String(120), index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
