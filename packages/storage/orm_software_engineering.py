from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class EngineeringProjectORM(Base):
    __tablename__ = "engineering_projects"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    project_type: Mapped[str] = mapped_column(String(80), index=True)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), index=True)
    languages: Mapped[list[str]] = mapped_column(JSON, default=list)
    frameworks: Mapped[list[str]] = mapped_column(JSON, default=list)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_apps: Mapped[list[str]] = mapped_column(JSON, default=list)
    linked_brain_modules: Mapped[list[str]] = mapped_column(JSON, default=list)


class EngineeringResearchRecordORM(Base):
    __tablename__ = "engineering_research_records"

    project_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    architecture_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    tool_recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    performance_findings: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_notes: Mapped[list[dict]] = mapped_column(JSON, default=list)
    modernization_score: Mapped[float] = mapped_column(Float, default=0.0)


class EngineeringExecutionRecordORM(Base):
    __tablename__ = "engineering_execution_records"

    project_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    milestones: Mapped[list[str]] = mapped_column(JSON, default=list)
    active_work: Mapped[list[str]] = mapped_column(JSON, default=list)
    blockers: Mapped[list[str]] = mapped_column(JSON, default=list)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    delivery_score: Mapped[float] = mapped_column(Float, default=0.0)


class EngineeringExperimentRecordORM(Base):
    __tablename__ = "engineering_experiment_records"

    project_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    experiments: Mapped[list[str]] = mapped_column(JSON, default=list)
    hypotheses: Mapped[list[str]] = mapped_column(JSON, default=list)
    findings: Mapped[list[str]] = mapped_column(JSON, default=list)
    adoption_candidates: Mapped[list[str]] = mapped_column(JSON, default=list)
    experimentation_score: Mapped[float] = mapped_column(Float, default=0.0)
