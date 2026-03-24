from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class AppProductionDecisionORM(Base):
    __tablename__ = 'app_production_decisions'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    blueprint_id: Mapped[str] = mapped_column(String(40), index=True)
    decision: Mapped[str] = mapped_column(String(20), index=True)
    rationale: Mapped[str] = mapped_column(Text, default='')
    action_items: Mapped[list[str]] = mapped_column(JSON, default=list)
    advisory_score: Mapped[float] = mapped_column(Float, default=0.0)
