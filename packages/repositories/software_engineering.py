from sqlalchemy.orm import Session

from packages.domain.software_engineering import (
    EngineeringExecutionRecord,
    EngineeringExperimentRecord,
    EngineeringProject,
    EngineeringProjectStatus,
    EngineeringProjectType,
    EngineeringResearchRecord,
)
from packages.storage.orm_software_engineering import (
    EngineeringExecutionRecordORM,
    EngineeringExperimentRecordORM,
    EngineeringProjectORM,
    EngineeringResearchRecordORM,
)


class EngineeringProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[EngineeringProject]:
        rows = self.db.query(EngineeringProjectORM).order_by(EngineeringProjectORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, project: EngineeringProject) -> EngineeringProject:
        row = EngineeringProjectORM(
            id=project.id,
            name=project.name,
            project_type=project.project_type.value,
            owner=project.owner,
            description=project.description,
            status=project.status.value,
            languages=project.languages,
            frameworks=project.frameworks,
            goals=project.goals,
            linked_apps=project.linked_apps,
            linked_brain_modules=project.linked_brain_modules,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, project_id: str) -> EngineeringProject | None:
        row = self.db.get(EngineeringProjectORM, project_id)
        return None if row is None else self._to_domain(row)

    def update_status(self, project_id: str, status: EngineeringProjectStatus) -> EngineeringProject | None:
        row = self.db.get(EngineeringProjectORM, project_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: EngineeringProjectORM) -> EngineeringProject:
        return EngineeringProject(
            id=row.id,
            name=row.name,
            project_type=EngineeringProjectType(row.project_type),
            owner=row.owner,
            description=row.description,
            status=EngineeringProjectStatus(row.status),
            languages=row.languages or [],
            frameworks=row.frameworks or [],
            goals=row.goals or [],
            linked_apps=row.linked_apps or [],
            linked_brain_modules=row.linked_brain_modules or [],
        )


class EngineeringResearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, record: EngineeringResearchRecord) -> EngineeringResearchRecord:
        row = self.db.get(EngineeringResearchRecordORM, record.project_id)
        if row is None:
            row = EngineeringResearchRecordORM(project_id=record.project_id)
        row.architecture_notes = record.architecture_notes
        row.tool_recommendations = record.tool_recommendations
        row.performance_findings = record.performance_findings
        row.risk_notes = record.risk_notes
        row.source_notes = record.source_notes
        row.modernization_score = record.modernization_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return EngineeringResearchRecord(
            project_id=row.project_id,
            architecture_notes=row.architecture_notes or [],
            tool_recommendations=row.tool_recommendations or [],
            performance_findings=row.performance_findings or [],
            risk_notes=row.risk_notes or [],
            source_notes=row.source_notes or [],
            modernization_score=row.modernization_score,
        )

    def get(self, project_id: str) -> EngineeringResearchRecord | None:
        row = self.db.get(EngineeringResearchRecordORM, project_id)
        if row is None:
            return None
        return EngineeringResearchRecord(
            project_id=row.project_id,
            architecture_notes=row.architecture_notes or [],
            tool_recommendations=row.tool_recommendations or [],
            performance_findings=row.performance_findings or [],
            risk_notes=row.risk_notes or [],
            source_notes=row.source_notes or [],
            modernization_score=row.modernization_score,
        )


class EngineeringExecutionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, record: EngineeringExecutionRecord) -> EngineeringExecutionRecord:
        row = self.db.get(EngineeringExecutionRecordORM, record.project_id)
        if row is None:
            row = EngineeringExecutionRecordORM(project_id=record.project_id)
        row.milestones = record.milestones
        row.active_work = record.active_work
        row.blockers = record.blockers
        row.reliability_score = record.reliability_score
        row.delivery_score = record.delivery_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return EngineeringExecutionRecord(
            project_id=row.project_id,
            milestones=row.milestones or [],
            active_work=row.active_work or [],
            blockers=row.blockers or [],
            reliability_score=row.reliability_score,
            delivery_score=row.delivery_score,
        )

    def get(self, project_id: str) -> EngineeringExecutionRecord | None:
        row = self.db.get(EngineeringExecutionRecordORM, project_id)
        if row is None:
            return None
        return EngineeringExecutionRecord(
            project_id=row.project_id,
            milestones=row.milestones or [],
            active_work=row.active_work or [],
            blockers=row.blockers or [],
            reliability_score=row.reliability_score,
            delivery_score=row.delivery_score,
        )


class EngineeringExperimentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, record: EngineeringExperimentRecord) -> EngineeringExperimentRecord:
        row = self.db.get(EngineeringExperimentRecordORM, record.project_id)
        if row is None:
            row = EngineeringExperimentRecordORM(project_id=record.project_id)
        row.experiments = record.experiments
        row.hypotheses = record.hypotheses
        row.findings = record.findings
        row.adoption_candidates = record.adoption_candidates
        row.experimentation_score = record.experimentation_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return EngineeringExperimentRecord(
            project_id=row.project_id,
            experiments=row.experiments or [],
            hypotheses=row.hypotheses or [],
            findings=row.findings or [],
            adoption_candidates=row.adoption_candidates or [],
            experimentation_score=row.experimentation_score,
        )

    def get(self, project_id: str) -> EngineeringExperimentRecord | None:
        row = self.db.get(EngineeringExperimentRecordORM, project_id)
        if row is None:
            return None
        return EngineeringExperimentRecord(
            project_id=row.project_id,
            experiments=row.experiments or [],
            hypotheses=row.hypotheses or [],
            findings=row.findings or [],
            adoption_candidates=row.adoption_candidates or [],
            experimentation_score=row.experimentation_score,
        )
