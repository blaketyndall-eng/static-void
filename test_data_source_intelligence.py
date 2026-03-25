from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v19 import app
from packages.storage.orm_data_source_intelligence import DataSourceIntelligenceSnapshotORM, DataSourceIntelligenceWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/data_source_intelligence_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    DataSourceIntelligenceWorkspaceORM.metadata.create_all(bind=db_session.engine)
    DataSourceIntelligenceSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_data_source_intelligence_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/data-source-intelligence/workspaces',
        json={
            'name': 'Source Intelligence Workspace',
            'owner': 'blake',
            'description': 'Tracks source quality, freshness, and conflicts.',
            'source_domains': ['vendor data', 'market data'],
            'intelligence_goals': ['freshness', 'reliability'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'signals'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/data-source-intelligence/workspaces/{workspace_id}/snapshot',
        json={
            'source_health_checks': ['vendor feed check'],
            'freshness_monitors': ['daily freshness monitor'],
            'reliability_flags': ['feed mismatch'],
            'conflict_detections': ['pricing conflict'],
            'coverage_gaps': ['missing small vendors'],
            'opportunities': ['expand source coverage'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'source_quality_score': 75,
            'freshness_confidence_score': 71,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['source_quality_score'] == 75

    status = client.post(
        f'/api/v1/data-source-intelligence/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/data-source-intelligence/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/data-source-intelligence/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_source_quality_score'] >= 0
    assert summary_payload['average_freshness_confidence_score'] >= 0
