from sqlalchemy.orm import Session

from packages.domain.decision_outputs import (
    ArtifactRecord,
    ArtifactType,
    EvidenceKind,
    EvidenceRecord,
    RecommendationRecord,
    RecommendationStatus,
)
from packages.storage.orm_outputs import ArtifactORM, EvidenceORM, RecommendationORM


class ArtifactRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ArtifactRecord]:
        rows = self.db.query(ArtifactORM).order_by(ArtifactORM.title.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, artifact: ArtifactRecord) -> ArtifactRecord:
        row = ArtifactORM(
            id=artifact.id,
            title=artifact.title,
            artifact_type=artifact.artifact_type.value,
            linked_entity_type=artifact.linked_entity_type,
            linked_entity_id=artifact.linked_entity_id,
            content=artifact.content,
            metadata_json=artifact.metadata,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ArtifactORM) -> ArtifactRecord:
        return ArtifactRecord(
            id=row.id,
            title=row.title,
            artifact_type=ArtifactType(row.artifact_type),
            linked_entity_type=row.linked_entity_type,
            linked_entity_id=row.linked_entity_id,
            content=row.content,
            metadata=row.metadata_json or {},
        )


class RecommendationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[RecommendationRecord]:
        rows = self.db.query(RecommendationORM).order_by(RecommendationORM.title.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, recommendation: RecommendationRecord) -> RecommendationRecord:
        row = RecommendationORM(
            id=recommendation.id,
            title=recommendation.title,
            linked_entity_type=recommendation.linked_entity_type,
            linked_entity_id=recommendation.linked_entity_id,
            summary=recommendation.summary,
            rationale=recommendation.rationale,
            status=recommendation.status.value,
            artifact_ids=recommendation.artifact_ids,
            evidence_ids=recommendation.evidence_ids,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: RecommendationORM) -> RecommendationRecord:
        return RecommendationRecord(
            id=row.id,
            title=row.title,
            linked_entity_type=row.linked_entity_type,
            linked_entity_id=row.linked_entity_id,
            summary=row.summary,
            rationale=row.rationale,
            status=RecommendationStatus(row.status),
            artifact_ids=row.artifact_ids or [],
            evidence_ids=row.evidence_ids or [],
        )


class EvidenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[EvidenceRecord]:
        rows = self.db.query(EvidenceORM).order_by(EvidenceORM.title.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, evidence: EvidenceRecord) -> EvidenceRecord:
        row = EvidenceORM(
            id=evidence.id,
            title=evidence.title,
            evidence_kind=evidence.evidence_kind.value,
            linked_entity_type=evidence.linked_entity_type,
            linked_entity_id=evidence.linked_entity_id,
            source_id=evidence.source_id,
            artifact_id=evidence.artifact_id,
            detail=evidence.detail,
            metadata_json=evidence.metadata,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: EvidenceORM) -> EvidenceRecord:
        return EvidenceRecord(
            id=row.id,
            title=row.title,
            evidence_kind=EvidenceKind(row.evidence_kind),
            linked_entity_type=row.linked_entity_type,
            linked_entity_id=row.linked_entity_id,
            source_id=row.source_id,
            artifact_id=row.artifact_id,
            detail=row.detail,
            metadata=row.metadata_json or {},
        )
