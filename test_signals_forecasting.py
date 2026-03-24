from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v13 import app
from packages.storage.orm_signals_forecasting import SignalsForecastingSnapshotORM, SignalsForecastingWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/signals_forecasting_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    SignalsForecastingWorkspaceORM.metadata.create_all(bind=db_session.engine)
    SignalsForecastingSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_signals_forecasting_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/signals-forecasting/workspaces',
        json={
            'name': 'Market Signals Workspace',
            'owner': 'blake',
            'description': 'Tracks trend shifts and forecast signals.',
            'tracked_domains': ['ai software', 'buying signals'],
            'forecast_targets': ['category demand', 'evaluation volume'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'pattern'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/signals-forecasting/workspaces/{workspace_id}/snapshot',
        json={
            'trend_signals': ['ai governance demand rising'],
            'forecast_hypotheses': ['evaluation volume will increase'],
            'anomaly_alerts': ['unexpected spike in vendor activity'],
            'regime_shift_notes': ['buyers moving earlier into evaluation'],
            'opportunities': ['launch governance workflows'],
            'risks': ['signal noise'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'signal_quality_score': 68,
            'forecast_confidence_score': 64,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['signal_quality_score'] == 68

    status = client.post(
        f'/api/v1/signals-forecasting/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/signals-forecasting/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/signals-forecasting/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_signal_quality_score'] >= 0
    assert summary_payload['average_forecast_confidence_score'] >= 0
