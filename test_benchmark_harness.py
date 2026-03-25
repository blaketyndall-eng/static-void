from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v30 import app
from packages.storage.orm_benchmark_harness import BenchmarkHarnessSnapshotORM, BenchmarkHarnessWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/benchmark_harness_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    BenchmarkHarnessWorkspaceORM.metadata.create_all(bind=db_session.engine)
    BenchmarkHarnessSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_benchmark_harness_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/benchmark-harness/workspaces',
        json={
            'name': 'Benchmark Workspace',
            'owner': 'blake',
            'description': 'Tracks benchmark suites, replay datasets, and challenger logic.',
            'benchmark_domains': ['routing', 'recommendations'],
            'benchmark_goals': ['quality', 'regression detection'],
            'linked_apps': [],
            'linked_brain_modules': ['reasoning', 'research'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/benchmark-harness/workspaces/{workspace_id}/snapshot',
        json={
            'benchmark_suites': ['reasoning benchmark suite'],
            'replay_datasets': ['historical replay set'],
            'challenger_models': ['challenger-v1'],
            'rollback_rules': ['rollback on quality drop'],
            'risks': ['benchmark drift'],
            'opportunities': ['improve evaluation rigor'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'benchmark_quality_score': 80,
            'harness_readiness_score': 75,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['benchmark_quality_score'] == 80

    status = client.post(
        f'/api/v1/benchmark-harness/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/benchmark-harness/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/benchmark-harness/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_benchmark_quality_score'] >= 0
    assert summary_payload['average_harness_readiness_score'] >= 0
