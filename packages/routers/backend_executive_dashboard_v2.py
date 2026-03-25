from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.system_events import SystemEventRepository
from packages.routers.backend_expansion_rollup import _collect
from packages.services.expansion_control import build_expansion_control_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/executive-dashboard', tags=['executive_dashboard_v2'])
telemetry = TelemetryLogger(filepath='var/executive_dashboard_telemetry.jsonl')

CORE_ARM_GROUPS = {
    'product_build': {'app_builder', 'software_engineering'},
    'growth_ops': {'marketing', 'opportunity_hunter'},
    'capital_ops': {'investment'},
    'system_links': {'brain_links'},
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


@router.get('/summary-v2')
def get_executive_dashboard_summary_v2(db: Session = Depends(get_db)) -> dict:
    events = [item.model_dump(mode='json') for item in SystemEventRepository(db).list()]
    expansion = build_expansion_control_summary(_collect(db)).model_dump(mode='json')

    core_cards = {}
    for name, arms in CORE_ARM_GROUPS.items():
        group_events = [item for item in events if item.get('source_arm') in arms]
        core_cards[name] = {
            'activity_count': len(group_events),
            'recent_activity': group_events[:10],
        }

    expansion_events = [item for item in events if item.get('source_arm') in EXPANSION_ARMS]
    payload = {
        'executive_overview': {
            'core_group_count': len(CORE_ARM_GROUPS),
            'expansion_workspace_count': expansion['total_workspace_count'],
            'expansion_active_count': expansion['total_active_count'],
            'expansion_arm_count': len(expansion['arm_summaries']),
        },
        'core_cards': core_cards,
        'expansion_card': {
            'workspace_count': expansion['total_workspace_count'],
            'active_count': expansion['total_active_count'],
            'top_risks': expansion['top_risks'][:10],
            'top_opportunities': expansion['top_opportunities'][:10],
            'recent_activity': expansion_events[:15],
            'arm_summaries': expansion['arm_summaries'],
        },
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_executive_dashboard_summary_v2', returned_count=payload['executive_overview']['expansion_workspace_count'])
    return payload
