from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v12 import app
from packages.storage.orm_ai_governance import AIGovernanceSnapshotORM, AIGovernanceWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/ai_governance_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    AIGovernanceWorkspaceORM.metadata.create_all(bind=db_session.engine)
    AIGovernanceSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_ai_governance_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/ai-governance/workspaces',
        json={
            'name': 'Model Governance Workspace',
            'owner': 'blake',
            'description': 'Tracks evaluation and policy readiness for AI use.',
            'model_scope': ['llm', 'reranker'],
            'evaluation_goals': ['benchmarking', 'policy review'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'evaluation'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/ai-governance/workspaces/{workspace_id}/snapshot',
        json={
            'benchmark_tracks': ['quality', 'latency'],
            'policy_checks': ['approval checklist'],
            'monitoring_checks': ['weekly review'],
            'risks': ['policy drift'],
            'mitigations': ['quarterly audits'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'governance_score': 66,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['governance_score'] == 66

    status = client.post(
        f'/api/v1/ai-governance/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/ai-governance/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/ai-governance/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_governance_score'] >= 0
