from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.system_events import SystemEventRepository
from packages.routers.backend_expansion_rollup import _collect
from packages.services.expansion_control import build_expansion_control_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/executive-dashboard', tags=['executive_dashboard'])
telemetry = TelemetryLogger(filepath='var/executive_dashboard_telemetry.jsonl')

CORE_ARMS = {
    'app_builder',
    'software_engineering',
    'marketing',
    'opportunity_hunter',
    'investment',
    'brain_links',
}
EXPANSION_ARMS = {
    'ai_governance',
    'signals_forecasting',
    'research_lab',
    'agent_studio',
    'decision_memory',
    'vertical_packs',
    'integrations_automation',
    'data_source_intelligence',
}


@router.get('/summary')
def get_executive_dashboard_summary(db: Session = Depends(get_db)) -> dict:
    events = [item.model_dump(mode='json') for item in SystemEventRepository(db).list()]
    core_activity = [item for item in events if item.get('source_arm') in CORE_ARMS]
    expansion_activity = [item for item in events if item.get('source_arm') in EXPANSION_ARMS]

    expansion_rollup = build_expansion_control_summary(_collect(db)).model_dump(mode='json')

    payload = {
        'executive_overview': {
            'core_activity_count': len(core_activity),
            'expansion_activity_count': len(expansion_activity),
            'expansion_workspace_count': expansion_rollup['total_workspace_count'],
            'expansion_active_count': expansion_rollup['total_active_count'],
        },
        'expansion_rollup': expansion_rollup,
        'core_recent_activity': core_activity[:20],
        'expansion_recent_activity': expansion_activity[:20],
        'top_risks': expansion_rollup['top_risks'][:10],
        'top_opportunities': expansion_rollup['top_opportunities'][:10],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_executive_dashboard_summary', returned_count=payload['executive_overview']['expansion_workspace_count'])
    return payload
