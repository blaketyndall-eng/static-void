from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class BlueprintEngineeringLinkORM(Base):
    __tablename__ = 'blueprint_engineering_links'

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    blueprint_id: Mapped[str] = mapped_column(String(40), index=True)
    engineering_project_id: Mapped[str] = mapped_column(String(40), index=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    linkage_reason: Mapped[str] = mapped_column(Text, default='')
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False)
