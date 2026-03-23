from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class SourceORM(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    trust_score: Mapped[float] = mapped_column(Float, default=0.5)
    freshness_label: Mapped[str] = mapped_column(String(50), default="unknown")
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)


class OpportunityORM(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(50), index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    themes: Mapped[list[str]] = mapped_column(JSON, default=list)


class EvaluationORM(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    decision_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criteria: Mapped[list[dict]] = mapped_column(JSON, default=list)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendation_summary: Mapped[str] = mapped_column(Text, default="")
