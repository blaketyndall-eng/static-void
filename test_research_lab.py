from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v14 import app
from packages.storage.orm_research_lab import ResearchLabSnapshotORM, ResearchLabWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/research_lab_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    ResearchLabWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ResearchLabSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_research_lab_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/research-lab/workspaces',
        json={
            'name': 'Experiment Lab Workspace',
            'owner': 'blake',
            'description': 'Tracks champion challenger tests and benchmark outcomes.',
            'experiment_domains': ['routing', 'prompting'],
            'benchmark_targets': ['latency', 'decision quality'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'evaluation'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/research-lab/workspaces/{workspace_id}/snapshot',
        json={
            'active_experiments': ['champion vs challenger prompts'],
            'benchmark_tracks': ['latency'],
            'winning_variants': ['prompt_v2'],
            'challenger_variants': ['prompt_v3'],
            'risks': ['benchmark drift'],
            'opportunities': ['promote winning variant'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'experiment_quality_score': 71,
            'benchmark_confidence_score': 67,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['experiment_quality_score'] == 71

    status = client.post(
        f'/api/v1/research-lab/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/research-lab/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/research-lab/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_experiment_quality_score'] >= 0
    assert summary_payload['average_benchmark_confidence_score'] >= 0
