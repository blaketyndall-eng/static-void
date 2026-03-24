from sqlalchemy.orm import Session

from packages.domain.opportunity_hunter import (
    OpportunityCandidate,
    OpportunityLearningSnapshot,
    OpportunityMarketSignal,
    OpportunityScan,
    OpportunityStatus,
    OpportunityType,
)
from packages.storage.orm_opportunity_hunter import (
    OpportunityCandidateORM,
    OpportunityMarketSignalORM,
    OpportunityScanORM,
)


class OpportunityScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[OpportunityScan]:
        rows = self.db.query(OpportunityScanORM).order_by(OpportunityScanORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, scan: OpportunityScan) -> OpportunityScan:
        row = OpportunityScanORM(
            id=scan.id,
            name=scan.name,
            focus=scan.focus,
            source_arms=scan.source_arms,
            source_queries=scan.source_queries,
            notes=scan.notes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, scan_id: str) -> OpportunityScan | None:
        row = self.db.get(OpportunityScanORM, scan_id)
        return None if row is None else self._to_domain(row)

    @staticmethod
    def _to_domain(row: OpportunityScanORM) -> OpportunityScan:
        return OpportunityScan(
            id=row.id,
            name=row.name,
            focus=row.focus,
            source_arms=row.source_arms or [],
            source_queries=row.source_queries or [],
            notes=row.notes,
        )


class OpportunityCandidateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_scan(self, scan_id: str) -> list[OpportunityCandidate]:
        rows = self.db.query(OpportunityCandidateORM).filter(OpportunityCandidateORM.scan_id == scan_id).all()
        return [self._to_domain(row) for row in rows]

    def create(self, candidate: OpportunityCandidate) -> OpportunityCandidate:
        row = OpportunityCandidateORM(
            id=candidate.id,
            scan_id=candidate.scan_id,
            title=candidate.title,
            opportunity_type=candidate.opportunity_type.value,
            status=candidate.status.value,
            summary=candidate.summary,
            target_users=candidate.target_users,
            related_apps=candidate.related_apps,
            related_industries=candidate.related_industries,
            evidence_notes=candidate.evidence_notes,
            demand_score=candidate.demand_score,
            competition_score=candidate.competition_score,
            whitespace_score=candidate.whitespace_score,
            priority_score=candidate.priority_score,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: OpportunityCandidateORM) -> OpportunityCandidate:
        return OpportunityCandidate(
            id=row.id,
            scan_id=row.scan_id,
            title=row.title,
            opportunity_type=OpportunityType(row.opportunity_type),
            status=OpportunityStatus(row.status),
            summary=row.summary,
            target_users=row.target_users or [],
            related_apps=row.related_apps or [],
            related_industries=row.related_industries or [],
            evidence_notes=row.evidence_notes or [],
            demand_score=row.demand_score,
            competition_score=row.competition_score,
            whitespace_score=row.whitespace_score,
            priority_score=row.priority_score,
        )


class OpportunitySignalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, signal: OpportunityMarketSignal) -> OpportunityMarketSignal:
        row = self.db.get(OpportunityMarketSignalORM, signal.candidate_id)
        if row is None:
            row = OpportunityMarketSignalORM(candidate_id=signal.candidate_id)
        row.trend_signal = signal.trend_signal
        row.labor_signal = signal.labor_signal
        row.industry_signal = signal.industry_signal
        row.research_signal = signal.research_signal
        row.source_stack = signal.source_stack
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return OpportunityMarketSignal(
            candidate_id=row.candidate_id,
            trend_signal=row.trend_signal,
            labor_signal=row.labor_signal,
            industry_signal=row.industry_signal,
            research_signal=row.research_signal,
            source_stack=row.source_stack or [],
        )

    def get(self, candidate_id: str) -> OpportunityMarketSignal | None:
        row = self.db.get(OpportunityMarketSignalORM, candidate_id)
        if row is None:
            return None
        return OpportunityMarketSignal(
            candidate_id=row.candidate_id,
            trend_signal=row.trend_signal,
            labor_signal=row.labor_signal,
            industry_signal=row.industry_signal,
            research_signal=row.research_signal,
            source_stack=row.source_stack or [],
        )


def build_learning_snapshot(scan_id: str, candidates: list[OpportunityCandidate]) -> OpportunityLearningSnapshot:
    if not candidates:
        return OpportunityLearningSnapshot(scan_id=scan_id, total_candidates=0, by_type={}, top_patterns=[], average_priority_score=0.0)

    by_type: dict[str, int] = {}
    patterns: list[str] = []
    for candidate in candidates:
        key = candidate.opportunity_type.value
        by_type[key] = by_type.get(key, 0) + 1
        if candidate.related_apps:
            patterns.append("app-adjacent expansion")
        if candidate.related_industries:
            patterns.append("industry adjacency")
        if candidate.whitespace_score >= 70:
            patterns.append("high whitespace")

    average_priority_score = round(sum(candidate.priority_score for candidate in candidates) / len(candidates), 2)
    top_patterns = sorted(set(patterns))[:5]
    return OpportunityLearningSnapshot(
        scan_id=scan_id,
        total_candidates=len(candidates),
        by_type=by_type,
        top_patterns=top_patterns,
        average_priority_score=average_priority_score,
    )
