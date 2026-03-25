from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v15 import app
from packages.storage.orm_agent_studio import AgentStudioSnapshotORM, AgentStudioWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/agent_studio_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    AgentStudioWorkspaceORM.metadata.create_all(bind=db_session.engine)
    AgentStudioSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_agent_studio_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/agent-studio/workspaces',
        json={
            'name': 'Routing Studio Workspace',
            'owner': 'blake',
            'description': 'Tracks routing policy quality and operator confidence.',
            'agent_roles': ['router', 'judge'],
            'routing_goals': ['quality', 'cost control'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'routing'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/agent-studio/workspaces/{workspace_id}/snapshot',
        json={
            'routing_policies': ['budget-first policy'],
            'hitl_checkpoints': ['approval gate'],
            'replay_tracks': ['routing replay v1'],
            'budget_controls': ['max tool budget'],
            'risks': ['misroute risk'],
            'opportunities': ['improve routing confidence'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'routing_quality_score': 70,
            'operator_confidence_score': 66,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['routing_quality_score'] == 70

    status = client.post(
        f'/api/v1/agent-studio/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/agent-studio/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/agent-studio/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_routing_quality_score'] >= 0
    assert summary_payload['average_operator_confidence_score'] >= 0
