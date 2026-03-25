from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v25 import app
from packages.storage.orm_ai_governance import AIGovernanceSnapshotORM, AIGovernanceWorkspaceORM
from packages.storage.orm_data_source_intelligence import DataSourceIntelligenceSnapshotORM, DataSourceIntelligenceWorkspaceORM
from packages.storage.orm_decision_memory import DecisionMemorySnapshotORM, DecisionMemoryWorkspaceORM
from packages.storage.orm_integrations_automation import IntegrationsAutomationSnapshotORM, IntegrationsAutomationWorkspaceORM
from packages.storage.orm_agent_studio import AgentStudioSnapshotORM, AgentStudioWorkspaceORM
from packages.storage.orm_research_lab import ResearchLabSnapshotORM, ResearchLabWorkspaceORM
from packages.storage.orm_signals_forecasting import SignalsForecastingSnapshotORM, SignalsForecastingWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM
from packages.storage.orm_verticalization import VerticalPacksSnapshotORM, VerticalPacksWorkspaceORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [
        Path('var/os_summary_telemetry.jsonl'),
        Path('var/system_events_telemetry.jsonl'),
    ]:
        if path.exists():
            path.unlink()
    AIGovernanceWorkspaceORM.metadata.create_all(bind=db_session.engine)
    AIGovernanceSnapshotORM.metadata.create_all(bind=db_session.engine)
    SignalsForecastingWorkspaceORM.metadata.create_all(bind=db_session.engine)
    SignalsForecastingSnapshotORM.metadata.create_all(bind=db_session.engine)
    ResearchLabWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ResearchLabSnapshotORM.metadata.create_all(bind=db_session.engine)
    AgentStudioWorkspaceORM.metadata.create_all(bind=db_session.engine)
    AgentStudioSnapshotORM.metadata.create_all(bind=db_session.engine)
    DecisionMemoryWorkspaceORM.metadata.create_all(bind=db_session.engine)
    DecisionMemorySnapshotORM.metadata.create_all(bind=db_session.engine)
    VerticalPacksWorkspaceORM.metadata.create_all(bind=db_session.engine)
    VerticalPacksSnapshotORM.metadata.create_all(bind=db_session.engine)
    IntegrationsAutomationWorkspaceORM.metadata.create_all(bind=db_session.engine)
    IntegrationsAutomationSnapshotORM.metadata.create_all(bind=db_session.engine)
    DataSourceIntelligenceWorkspaceORM.metadata.create_all(bind=db_session.engine)
    DataSourceIntelligenceSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def seed_workspaces(client: TestClient) -> None:
    client.post('/api/v1/ai-governance/workspaces', json={'name': 'AI Gov', 'owner': 'blake'})
    client.post('/api/v1/signals-forecasting/workspaces', json={'name': 'Signals', 'owner': 'blake'})
    client.post('/api/v1/research-lab/workspaces', json={'name': 'Research Lab', 'owner': 'blake'})
    client.post('/api/v1/agent-studio/workspaces', json={'name': 'Agent Studio', 'owner': 'blake'})
    client.post('/api/v1/decision-memory/workspaces', json={'name': 'Decision Memory', 'owner': 'blake'})
    client.post('/api/v1/vertical-packs/workspaces', json={'name': 'Vertical Packs', 'owner': 'blake'})
    client.post('/api/v1/integrations-automation/workspaces', json={'name': 'Integrations', 'owner': 'blake'})
    client.post('/api/v1/data-source-intelligence/workspaces', json={'name': 'Sources', 'owner': 'blake'})


def test_os_summary() -> None:
    reset_state()
    client = TestClient(app)
    seed_workspaces(client)

    summary = client.get('/api/v1/os/summary')
    assert summary.status_code == 200
    payload = summary.json()
    assert 'home_overview' in payload
    assert 'executive_cards' in payload
    assert 'expansion_control' in payload
    assert payload['home_overview']['expansion_workspace_count'] >= 8
    assert len(payload['expansion_control']['rollup']['arm_summaries']) >= 8
