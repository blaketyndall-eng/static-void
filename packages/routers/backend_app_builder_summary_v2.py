from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.app_builder import AppBlueprintRepository, AppScaffoldPlanRepository
from packages.repositories.blueprint_engineering_link import BlueprintEngineeringLinkRepository
from packages.repositories.software_engineering import EngineeringExecutionRepository, EngineeringExperimentRepository, EngineeringProjectRepository, EngineeringResearchRepository
from packages.services.se_app_linking import find_best_linked_project, score_blueprint_project_match
from packages.services.software_engineering_app_production import build_app_production_advisory, build_app_production_portfolio_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v2/app-builder', tags=['app_builder_summary_v2'])
telemetry = TelemetryLogger(filepath='var/app_builder_telemetry.jsonl')


@router.get('/summary')
def get_app_builder_summary_v2(db: Session = Depends(get_db)) -> dict:
    blueprint_repo = AppBlueprintRepository(db)
    plan_repo = AppScaffoldPlanRepository(db)
    link_repo = BlueprintEngineeringLinkRepository(db)
    project_repo = EngineeringProjectRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)

    blueprints = blueprint_repo.list()
    projects = project_repo.list()
    advisories = []
    items = []
    linked_count = 0
    plan_count = 0

    for blueprint in blueprints:
        plan = plan_repo.get(blueprint.id)
        if plan is not None:
            plan_count += 1
        persisted_link = link_repo.get_for_blueprint(blueprint.id)
        linked_project = None
        match_score = None
        linkage_reason = None
        if persisted_link is not None:
            linked_project = project_repo.get(persisted_link.engineering_project_id)
            match_score = persisted_link.match_score
            linkage_reason = persisted_link.linkage_reason
            linked_count += 1
        else:
            linked_project = find_best_linked_project(blueprint, projects)
            if linked_project is not None:
                match_score = score_blueprint_project_match(blueprint, linked_project)
                linkage_reason = 'auto-matched from blueprint and engineering project signals'

        advisory = build_app_production_advisory(
            blueprint,
            linked_project,
            None if linked_project is None else research_repo.get(linked_project.id),
            None if linked_project is None else execution_repo.get(linked_project.id),
            None if linked_project is None else experiment_repo.get(linked_project.id),
        )
        advisories.append(advisory)
        items.append({
            'blueprint': blueprint.model_dump(mode='json'),
            'has_scaffold_plan': plan is not None,
            'linked_project': None if linked_project is None else linked_project.model_dump(mode='json'),
            'match_score': match_score,
            'linkage_reason': linkage_reason,
            'advisory': advisory.model_dump(mode='json'),
        })

    portfolio = build_app_production_portfolio_summary(advisories)
    weak_blueprints = [item for item in items if item['advisory']['readiness_score'] < 65]
    ready_blueprints = [item for item in items if item['advisory']['readiness_score'] >= 75]

    payload = {
        'total_blueprints': len(blueprints),
        'scaffold_plan_count': plan_count,
        'linked_engineering_count': linked_count,
        'ready_blueprint_count': len(ready_blueprints),
        'weak_blueprint_count': len(weak_blueprints),
        'production_portfolio': portfolio.model_dump(mode='json'),
        'items': items[:15],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_app_builder_summary_v2', returned_count=len(blueprints), linked_count=linked_count)
    return payload
