from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v9 import app
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from packages.storage.orm_blueprint_engineering_link import BlueprintEngineeringLinkORM
from packages.storage.orm_software_engineering import EngineeringExecutionRecordORM, EngineeringExperimentRecordORM, EngineeringProjectORM, EngineeringResearchRecordORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/app_builder_telemetry.jsonl'), Path('var/software_engineering_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    AppBlueprintORM.metadata.create_all(bind=db_session.engine)
    AppScaffoldPlanORM.metadata.create_all(bind=db_session.engine)
    BlueprintEngineeringLinkORM.metadata.create_all(bind=db_session.engine)
    EngineeringProjectORM.metadata.create_all(bind=db_session.engine)
    EngineeringResearchRecordORM.metadata.create_all(bind=db_session.engine)
    EngineeringExecutionRecordORM.metadata.create_all(bind=db_session.engine)
    EngineeringExperimentRecordORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def seed_linked_blueprint(client: TestClient) -> tuple[str, str]:
    blueprint = client.post(
        '/api/v2/app-builder/blueprints-bridge',
        json={
            'name': 'Execution Console',
            'app_type': 'operator_console',
            'description': 'Coordinates execution, delivery, and operational reporting.',
            'target_users': ['operators'],
            'workflows': ['delivery', 'research'],
            'required_engines': ['analytics'],
            'primary_views': ['dashboard'],
            'data_sources': ['python'],
            'notes': 'seed',
        },
    )
    assert blueprint.status_code == 200
    blueprint_id = blueprint.json()['id']

    project = client.post(
        '/api/v2/software-engineering/projects',
        json={
            'name': 'Execution Console Runtime',
            'project_type': 'application',
            'owner': 'blake',
            'description': 'Supports execution console runtime and delivery systems.',
            'languages': ['python'],
            'frameworks': ['dashboard'],
            'goals': ['delivery', 'research'],
            'linked_apps': [],
            'linked_brain_modules': ['memory'],
        },
    )
    assert project.status_code == 200
    project_id = project.json()['id']

    research = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/research',
        json={
            'architecture_notes': ['clean module split'],
            'tool_recommendations': ['uv', 'Playwright'],
            'performance_findings': ['good baseline'],
            'risk_notes': ['watch coupling'],
            'source_notes': [{'source': 'internal', 'note': 'seed'}],
            'modernization_score': 77,
        },
    )
    assert research.status_code == 200

    execution = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/execution',
        json={
            'milestones': ['runtime'],
            'active_work': ['operator integration'],
            'blockers': [],
            'reliability_score': 73,
            'delivery_score': 75,
        },
    )
    assert execution.status_code == 200

    experiments = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/experiments',
        json={
            'experiments': ['test-speed improvement'],
            'hypotheses': ['faster tooling improves iteration'],
            'findings': ['promising'],
            'adoption_candidates': ['uv'],
            'experimentation_score': 69,
        },
    )
    assert experiments.status_code == 200

    linked = client.post(
        f'/api/v2/app-builder/blueprints/{blueprint_id}/engineering-link',
        json={
            'engineering_project_id': project_id,
            'match_score': 88,
            'linkage_reason': 'manual override for production support alignment',
            'is_manual_override': True,
        },
    )
    assert linked.status_code == 200
    return blueprint_id, project_id


def test_app_production_v3_prefers_persisted_linkage_and_shows_activity() -> None:
    reset_state()
    client = TestClient(app)
    blueprint_id, project_id = seed_linked_blueprint(client)

    summary = client.get('/api/v2/software-engineering/app-production/summary-v3')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['portfolio']['advisory_count'] >= 1
    assert summary_payload['persisted_link_count'] >= 1
    assert len(summary_payload['recent_activity']) >= 1

    detail = client.get(f'/api/v2/software-engineering/app-production/blueprint/{blueprint_id}/v3')
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload['linkage_source'] == 'persisted'
    assert detail_payload['linked_project']['id'] == project_id
    assert detail_payload['match_score'] == 88
    assert len(detail_payload['operator_actions']) >= 1
    assert len(detail_payload['recent_activity']) >= 1
