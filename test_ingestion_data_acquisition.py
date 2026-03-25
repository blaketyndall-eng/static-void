from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v26 import app
from packages.storage.orm_ingestion_data_acquisition import IngestionDataAcquisitionSnapshotORM, IngestionDataAcquisitionWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/ingestion_data_acquisition_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    IngestionDataAcquisitionWorkspaceORM.metadata.create_all(bind=db_session.engine)
    IngestionDataAcquisitionSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_ingestion_data_acquisition_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/ingestion-data-acquisition/workspaces',
        json={
            'name': 'Ingestion Workspace',
            'owner': 'blake',
            'description': 'Tracks connectors, sync jobs, and normalization readiness.',
            'source_targets': ['vendor feeds', 'market feeds'],
            'ingestion_goals': ['freshness', 'normalization'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'signals'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/ingestion-data-acquisition/workspaces/{workspace_id}/snapshot',
        json={
            'connectors': ['vendor api connector'],
            'sync_jobs': ['daily vendor sync'],
            'normalization_pipelines': ['vendor normalization'],
            'freshness_windows': ['24h'],
            'failures': ['late sync once'],
            'opportunities': ['expand source ingestion'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'ingestion_health_score': 76,
            'normalization_readiness_score': 72,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['ingestion_health_score'] == 76

    status = client.post(
        f'/api/v1/ingestion-data-acquisition/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/ingestion-data-acquisition/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/ingestion-data-acquisition/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_ingestion_health_score'] >= 0
    assert summary_payload['average_normalization_readiness_score'] >= 0
