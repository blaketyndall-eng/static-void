from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v8 import app
from packages.storage.orm_app_builder import AppBlueprintORM, AppScaffoldPlanORM
from packages.storage.orm_blueprint_engineering_link import BlueprintEngineeringLinkORM
from packages.storage.orm_software_engineering import (
    EngineeringExecutionRecordORM,
    EngineeringExperimentRecordORM,
    EngineeringProjectORM,
    EngineeringResearchRecordORM,
)
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


def test_blueprint_engineering_link_and_summary_v2() -> None:
    reset_state()
    client = TestClient(app)

    blueprint = client.post(
        '/api/v2/app-builder/blueprints-bridge',
        json={
            'name': 'Decision Ops Builder',
            'app_type': 'operator_console',
            'description': 'Builds decision operations and app workflows.',
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
            'name': 'Decision Ops Builder',
            'project_type': 'application',
            'owner': 'blake',
            'description': 'Engineering support for decision ops builder.',
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
            'architecture_notes': ['service boundaries defined'],
            'tool_recommendations': ['uv', 'Playwright'],
            'performance_findings': ['startup is acceptable'],
            'risk_notes': ['monitor dependency sprawl'],
            'source_notes': [{'source': 'internal', 'note': 'seed'}],
            'modernization_score': 78,
        },
    )
    assert research.status_code == 200

    execution = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/execution',
        json={
            'milestones': ['foundation'],
            'active_work': ['summary routes'],
            'blockers': [],
            'reliability_score': 74,
            'delivery_score': 76,
        },
    )
    assert execution.status_code == 200

    experiments = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/experiments',
        json={
            'experiments': ['faster build pipeline'],
            'hypotheses': ['uv reduces setup time'],
            'findings': ['positive local speedup'],
            'adoption_candidates': ['uv'],
            'experimentation_score': 72,
        },
    )
    assert experiments.status_code == 200

    linked = client.post(
        f'/api/v2/app-builder/blueprints/{blueprint_id}/engineering-link',
        json={
            'engineering_project_id': project_id,
            'match_score': 91,
            'linkage_reason': 'manual confirmation for same product line',
            'is_manual_override': True,
        },
    )
    assert linked.status_code == 200
    assert linked.json()['engineering_project_id'] == project_id

    fetched = client.get(f'/api/v2/app-builder/blueprints/{blueprint_id}/engineering-link')
    assert fetched.status_code == 200
    assert fetched.json()['link']['match_score'] == 91

    summary = client.get('/api/v2/app-builder/summary')
    assert summary.status_code == 200
    payload = summary.json()
    assert payload['total_blueprints'] >= 1
    assert payload['linked_engineering_count'] >= 1
    assert payload['production_portfolio']['advisory_count'] >= 1
    assert len(payload['items']) >= 1
