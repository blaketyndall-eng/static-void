from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.system_events import SystemEventRepository
from packages.routers.backend_expansion_rollup import _collect
from packages.services.expansion_control import build_expansion_control_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/os', tags=['os_summary'])
telemetry = TelemetryLogger(filepath='var/os_summary_telemetry.jsonl')

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


@router.get('/summary')
def get_os_summary(db: Session = Depends(get_db)) -> dict:
    events = [item.model_dump(mode='json') for item in SystemEventRepository(db).list()]
    arm_summaries = _collect(db)
    expansion = build_expansion_control_summary(arm_summaries).model_dump(mode='json')

    core_cards = {}
    for name, arms in CORE_ARM_GROUPS.items():
        group_events = [item for item in events if item.get('source_arm') in arms]
        core_cards[name] = {
            'activity_count': len(group_events),
            'recent_activity': group_events[:10],
        }

    expansion_events = [item for item in events if item.get('source_arm') in EXPANSION_ARMS]

    payload = {
        'home_overview': {
            'core_group_count': len(CORE_ARM_GROUPS),
            'expansion_arm_count': len(arm_summaries),
            'expansion_workspace_count': expansion['total_workspace_count'],
            'expansion_active_count': expansion['total_active_count'],
            'total_recent_activity_count': len(events),
        },
        'executive_cards': core_cards,
        'expansion_control': {
            'rollup': expansion,
            'recent_activity': expansion_events[:20],
            'top_risks': expansion['top_risks'][:10],
            'top_opportunities': expansion['top_opportunities'][:10],
        },
        'global_recent_activity': events[:30],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_os_summary', returned_count=payload['home_overview']['expansion_workspace_count'])
    return payload
