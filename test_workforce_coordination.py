from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v34 import app
from packages.storage.orm_system_events import SystemEventRecordORM
from packages.storage.orm_workforce_coordination import WorkforceCoordinationSnapshotORM, WorkforceCoordinationWorkspaceORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/workforce_coordination_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    WorkforceCoordinationWorkspaceORM.metadata.create_all(bind=db_session.engine)
    WorkforceCoordinationSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_workforce_coordination_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/workforce-coordination/workspaces',
        json={
            'name': 'Workforce Coordination Workspace',
            'owner': 'blake',
            'description': 'Tracks worker roles, routing, queue pressure, and escalation rules.',
            'role_groups': ['research squad', 'operator squad'],
            'coordination_goals': ['improve queue discipline', 'reduce escalations'],
            'linked_apps': [],
            'linked_modules': ['company_operator', 'action_execution'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/workforce-coordination/workspaces/{workspace_id}/snapshot',
        json={
            'access_rules': ['operators can approve launches'],
            'spend_limits': ['max monthly tool spend threshold'],
            'routing_rules': ['research items route to research squad'],
            'work_queues': ['launch queue', 'ops queue'],
            'review_points': ['human review before external send'],
            'linked_tools': ['slack', 'notion'],
            'escalation_rules': ['escalate stale queue after 24h'],
            'opportunities': ['improve routing confidence'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'reliability_score': 77,
            'readiness_score': 72,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['reliability_score'] == 77

    status = client.post(
        f'/api/v1/workforce-coordination/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/workforce-coordination/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/workforce-coordination/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_reliability_score'] >= 0
    assert summary_payload['average_readiness_score'] >= 0
