from sqlalchemy.orm import Session

from packages.domain.app_builder import AppBlueprint, AppTemplateType, BuildPacket, ScaffoldPlan
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from packages.services.app_blueprint_generator import generate_build_packet


class AppBlueprintRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[AppBlueprint]:
        rows = self.db.query(AppBlueprintORM).order_by(AppBlueprintORM.name.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, blueprint: AppBlueprint) -> AppBlueprint:
        row = AppBlueprintORM(
            id=blueprint.id,
            name=blueprint.name,
            app_type=blueprint.app_type.value,
            description=blueprint.description,
            target_users=blueprint.target_users,
            workflows=blueprint.workflows,
            required_engines=blueprint.required_engines,
            primary_views=blueprint.primary_views,
            data_sources=blueprint.data_sources,
            notes=blueprint.notes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, blueprint_id: str) -> AppBlueprint | None:
        row = self.db.get(AppBlueprintORM, blueprint_id)
        return None if row is None else self._to_domain(row)

    @staticmethod
    def _to_domain(row: AppBlueprintORM) -> AppBlueprint:
        return AppBlueprint(
            id=row.id,
            name=row.name,
            app_type=AppTemplateType(row.app_type),
            description=row.description,
            target_users=row.target_users or [],
            workflows=row.workflows or [],
            required_engines=row.required_engines or [],
            primary_views=row.primary_views or [],
            data_sources=row.data_sources or [],
            build_packet=generate_build_packet(AppTemplateType(row.app_type), row.name),
            notes=row.notes,
        )


class AppScaffoldPlanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(self, plan: ScaffoldPlan) -> ScaffoldPlan:
        row = self.db.get(AppScaffoldPlanORM, plan.blueprint_id)
        if row is None:
            row = AppScaffoldPlanORM(blueprint_id=plan.blueprint_id)
        row.summary = plan.summary
        row.steps = plan.steps
        row.recommended_frameworks = plan.recommended_frameworks
        row.generated_files = plan.generated_files
        row.tech_debt_items = plan.tech_debt_items
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ScaffoldPlan(
            blueprint_id=row.blueprint_id,
            summary=row.summary,
            steps=row.steps or [],
            recommended_frameworks=row.recommended_frameworks or [],
            generated_files=row.generated_files or [],
            tech_debt_items=row.tech_debt_items or [],
        )

    def get(self, blueprint_id: str) -> ScaffoldPlan | None:
        row = self.db.get(AppScaffoldPlanORM, blueprint_id)
        if row is None:
            return None
        return ScaffoldPlan(
            blueprint_id=row.blueprint_id,
            summary=row.summary,
            steps=row.steps or [],
            recommended_frameworks=row.recommended_frameworks or [],
            generated_files=row.generated_files or [],
            tech_debt_items=row.tech_debt_items or [],
        )
