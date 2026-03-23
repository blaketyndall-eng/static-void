# Observability Surface Map

## Canonical runtime surfaces

### `integrated_intelligence_app.py`
Scope:
- recommendation generation
- recommendation explainability
- linked workflow mutations
- event logging for decision logic

Telemetry files currently associated with this scope:
- `var/recommendation_telemetry.jsonl`
- `var/integrated_intelligence_events.jsonl`

### `integrated_product_surface_app.py`
Scope:
- decision board summary
- attention-needed
- evaluation summary and readiness
- recommendation cards
- recent activity feed

Telemetry files currently associated with this scope:
- `var/decision_board_telemetry.jsonl`
- `var/evaluation_surface_telemetry.jsonl`
- `var/activity_surface_telemetry.jsonl`

## Temporary observed API files
These currently prove telemetry behavior, but should be folded into the canonical runtime surfaces:
- `observed_recommendation_api.py`
- `observed_board_summary_api.py`
- `observed_attention_needed_api.py`
- `observed_evaluation_readiness_api.py`
- `observed_recommendation_cards_api.py`
- `observed_recent_activity_api.py`

## Consolidation direction
1. Reuse `telemetry_logger.py`, `telemetry_events.py`, and `telemetry_helpers.py` from both canonical surfaces.
2. Keep event logging and telemetry logging distinct until runtime consolidation is complete.
3. After consolidation, reduce the number of telemetry files where practical while keeping backend and product-surface concerns distinct enough for debugging.
