from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v32 import app
from packages.storage.orm_action_workflow_execution import ActionWorkflowExecutionSnapshotORM, ActionWorkflowExecutionWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/action_workflow_execution_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    ActionWorkflowExecutionWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ActionWorkflowExecutionSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_action_workflow_execution_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/action-workflow-execution/workspaces',
        json={
            'name': 'Action Workspace',
            'owner': 'blake',
            'description': 'Tracks execution workflows, approval checkpoints, and connector actions.',
            'execution_domains': ['company ops', 'go to market ops'],
            'workflow_goals': ['reliable execution', 'approval discipline'],
            'linked_apps': [],
            'linked_brain_modules': ['reasoning', 'output'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/action-workflow-execution/workspaces/{workspace_id}/snapshot',
        json={
            'workflow_templates': ['launch workflow v1'],
            'approval_checkpoints': ['final operator approval'],
            'connector_actions': ['notify channel', 'create task record'],
            'execution_logs': ['workflow run 001'],
            'failure_modes': ['approval bottleneck'],
            'opportunities': ['improve execution throughput'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'execution_reliability_score': 78,
            'approval_readiness_score': 73,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['execution_reliability_score'] == 78

    status = client.post(
        f'/api/v1/action-workflow-execution/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/action-workflow-execution/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/action-workflow-execution/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_execution_reliability_score'] >= 0
    assert summary_payload['average_approval_readiness_score'] >= 0
