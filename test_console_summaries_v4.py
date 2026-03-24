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
from packages.storage.orm_brain_links import BrainLinkRecordORM
from packages.storage.orm_opportunity_hunter import OpportunityCandidateORM, OpportunityMarketSignalORM, OpportunityScanORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [
        Path('var/app_builder_telemetry.jsonl'),
        Path('var/software_engineering_telemetry.jsonl'),
        Path('var/system_events_telemetry.jsonl'),
        Path('var/master_console_telemetry.jsonl'),
        Path('var/brain_links_telemetry.jsonl'),
        Path('var/opportunity_hunter_telemetry.jsonl'),
    ]:
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
    BrainLinkRecordORM.metadata.create_all(bind=db_session.engine)
    OpportunityScanORM.metadata.create_all(bind=db_session.engine)
    OpportunityCandidateORM.metadata.create_all(bind=db_session.engine)
    OpportunityMarketSignalORM.metadata.create_all(bind=db_session.engine)


def seed_blueprint_and_engineering(client: TestClient) -> tuple[str, str]:
    blueprint = client.post(
        '/api/v2/app-builder/blueprints-bridge',
        json={
            'name': 'Signal Builder',
            'app_type': 'operator_console',
            'description': 'Builds signal workflows and console views.',
            'target_users': ['operators'],
            'workflows': ['research', 'delivery'],
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
            'name': 'Signal Builder',
            'project_type': 'application',
            'owner': 'blake',
            'description': 'Engineering support for signal builder.',
            'languages': ['python'],
            'frameworks': ['dashboard'],
            'goals': ['research', 'delivery'],
            'linked_apps': [],
            'linked_brain_modules': ['memory'],
        },
    )
    assert project.status_code == 200
    project_id = project.json()['id']

    research = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/research',
        json={
            'architecture_notes': ['bounded modules'],
            'tool_recommendations': ['uv', 'Vitest'],
            'performance_findings': ['response times stable'],
            'risk_notes': ['watch dependency sprawl'],
            'source_notes': [{'source': 'internal', 'note': 'seed'}],
            'modernization_score': 80,
        },
    )
    assert research.status_code == 200

    execution = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/execution',
        json={
            'milestones': ['foundation'],
            'active_work': ['summary integration'],
            'blockers': [],
            'reliability_score': 75,
            'delivery_score': 78,
        },
    )
    assert execution.status_code == 200

    experiments = client.post(
        f'/api/v2/software-engineering/projects/{project_id}/experiments',
        json={
            'experiments': ['faster test loop'],
            'hypotheses': ['Vitest improves iteration speed'],
            'findings': ['positive local feedback'],
            'adoption_candidates': ['Vitest'],
            'experimentation_score': 70,
        },
    )
    assert experiments.status_code == 200

    linked = client.post(
        f'/api/v2/app-builder/blueprints/{blueprint_id}/engineering-link',
        json={
            'engineering_project_id': project_id,
            'match_score': 93,
            'linkage_reason': 'manual confirmation for aligned blueprint and project',
            'is_manual_override': True,
        },
    )
    assert linked.status_code == 200
    return blueprint_id, project_id


def test_app_builder_summary_v3_master_v4_global_v3_and_app_production_v2() -> None:
    reset_state()
    client = TestClient(app)
    blueprint_id, _project_id = seed_blueprint_and_engineering(client)

    brain_link = client.post(
        '/api/v1/brain-links',
        json={
            'source_arm': 'app_builder',
            'source_id': blueprint_id,
            'target_type': 'app_to_module',
            'target_id': 'memory',
            'notes': 'Blueprint linked to memory module',
        },
    )
    assert brain_link.status_code == 200

    opp_scan = client.post(
        '/api/v2/opportunities/scans',
        json={
            'name': 'Engineering Opportunity Sweep',
            'focus': 'Find engineering-adjacent app opportunities.',
            'source_arms': ['app_builder', 'software_engineering'],
            'source_queries': ['developer tooling'],
            'notes': 'seed',
        },
    )
    assert opp_scan.status_code == 200

    app_builder_summary = client.get('/api/v2/app-builder/summary-v3')
    assert app_builder_summary.status_code == 200
    app_builder_payload = app_builder_summary.json()
    assert app_builder_payload['linked_engineering_count'] >= 1
    assert app_builder_payload['manual_override_count'] >= 1
    assert len(app_builder_payload['recent_activity']) >= 1

    production_summary = client.get('/api/v2/software-engineering/app-production/summary-v2')
    assert production_summary.status_code == 200
    production_payload = production_summary.json()
    assert production_payload['portfolio']['advisory_count'] >= 1
    assert len(production_payload['linkage_notes']) >= 1

    master_summary = client.get('/api/v1/master-console/summary-v4')
    assert master_summary.status_code == 200
    master_payload = master_summary.json()
    assert master_payload['software_engineering']['project_count'] >= 1
    assert master_payload['software_engineering']['production_portfolio']['advisory_count'] >= 1

    global_summary = client.get('/api/v1/global/summary-v3')
    assert global_summary.status_code == 200
    global_payload = global_summary.json()
    assert global_payload['software_engineering']['project_count'] >= 1
    assert global_payload['software_engineering']['production_portfolio']['advisory_count'] >= 1
