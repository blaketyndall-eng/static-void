from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v18 import app
from packages.storage.orm_integrations_automation import IntegrationsAutomationSnapshotORM, IntegrationsAutomationWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/integrations_automation_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    IntegrationsAutomationWorkspaceORM.metadata.create_all(bind=db_session.engine)
    IntegrationsAutomationSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_integrations_automation_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/integrations-automation/workspaces',
        json={
            'name': 'Automation Operations Workspace',
            'owner': 'blake',
            'description': 'Tracks integration health and workflow reliability.',
            'integration_targets': ['crm', 'slack'],
            'automation_goals': ['sync health', 'workflow reliability'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'routing'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/integrations-automation/workspaces/{workspace_id}/snapshot',
        json={
            'integration_health_checks': ['crm sync check'],
            'automation_workflows': ['daily sync'],
            'webhook_endpoints': ['slack webhook'],
            'freshness_alerts': ['stale source alert'],
            'risks': ['sync drift'],
            'opportunities': ['expand workflow reuse'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'integration_health_score': 74,
            'automation_reliability_score': 70,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['integration_health_score'] == 74

    status = client.post(
        f'/api/v1/integrations-automation/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/integrations-automation/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/integrations-automation/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_integration_health_score'] >= 0
    assert summary_payload['average_automation_reliability_score'] >= 0
