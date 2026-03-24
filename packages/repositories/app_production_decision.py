from sqlalchemy.orm import Session

from packages.domain.app_production_decision import AppProductionDecision, AppProductionDecisionState
from packages.storage.orm_app_production_decision import AppProductionDecisionORM


class AppProductionDecisionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, decision: AppProductionDecision) -> AppProductionDecision:
        row = self.db.query(AppProductionDecisionORM).filter(
            AppProductionDecisionORM.blueprint_id == decision.blueprint_id
        ).first()
        if row is None:
            row = AppProductionDecisionORM(id=decision.id, blueprint_id=decision.blueprint_id)
        row.decision = decision.decision.value
        row.rationale = decision.rationale
        row.action_items = decision.action_items
        row.advisory_score = decision.advisory_score
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return AppProductionDecision(
            id=row.id,
            blueprint_id=row.blueprint_id,
            decision=AppProductionDecisionState(row.decision),
            rationale=row.rationale,
            action_items=row.action_items or [],
            advisory_score=row.advisory_score,
        )

    def get_for_blueprint(self, blueprint_id: str) -> AppProductionDecision | None:
        row = self.db.query(AppProductionDecisionORM).filter(
            AppProductionDecisionORM.blueprint_id == blueprint_id
        ).first()
        if row is None:
            return None
        return AppProductionDecision(
            id=row.id,
            blueprint_id=row.blueprint_id,
            decision=AppProductionDecisionState(row.decision),
            rationale=row.rationale,
            action_items=row.action_items or [],
            advisory_score=row.advisory_score,
        )

    def list(self) -> list[AppProductionDecision]:
        rows = self.db.query(AppProductionDecisionORM).all()
        return [
            AppProductionDecision(
                id=row.id,
                blueprint_id=row.blueprint_id,
                decision=AppProductionDecisionState(row.decision),
                rationale=row.rationale,
                action_items=row.action_items or [],
                advisory_score=row.advisory_score,
            )
            for row in rows
        ]
