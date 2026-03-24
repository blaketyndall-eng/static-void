from sqlalchemy.orm import Session

from packages.domain.blueprint_engineering_link import BlueprintEngineeringLink
from packages.storage.orm_blueprint_engineering_link import BlueprintEngineeringLinkORM


class BlueprintEngineeringLinkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, link: BlueprintEngineeringLink) -> BlueprintEngineeringLink:
        row = self.db.query(BlueprintEngineeringLinkORM).filter(
            BlueprintEngineeringLinkORM.blueprint_id == link.blueprint_id
        ).first()
        if row is None:
            row = BlueprintEngineeringLinkORM(id=link.id, blueprint_id=link.blueprint_id)
        row.engineering_project_id = link.engineering_project_id
        row.match_score = link.match_score
        row.linkage_reason = link.linkage_reason
        row.is_manual_override = link.is_manual_override
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return BlueprintEngineeringLink(
            id=row.id,
            blueprint_id=row.blueprint_id,
            engineering_project_id=row.engineering_project_id,
            match_score=row.match_score,
            linkage_reason=row.linkage_reason,
            is_manual_override=row.is_manual_override,
        )

    def get_for_blueprint(self, blueprint_id: str) -> BlueprintEngineeringLink | None:
        row = self.db.query(BlueprintEngineeringLinkORM).filter(
            BlueprintEngineeringLinkORM.blueprint_id == blueprint_id
        ).first()
        if row is None:
            return None
        return BlueprintEngineeringLink(
            id=row.id,
            blueprint_id=row.blueprint_id,
            engineering_project_id=row.engineering_project_id,
            match_score=row.match_score,
            linkage_reason=row.linkage_reason,
            is_manual_override=row.is_manual_override,
        )

    def list(self) -> list[BlueprintEngineeringLink]:
        rows = self.db.query(BlueprintEngineeringLinkORM).all()
        return [
            BlueprintEngineeringLink(
                id=row.id,
                blueprint_id=row.blueprint_id,
                engineering_project_id=row.engineering_project_id,
                match_score=row.match_score,
                linkage_reason=row.linkage_reason,
                is_manual_override=row.is_manual_override,
            )
            for row in rows
        ]
