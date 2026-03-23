# Observed Surface Consolidation

## Goal
Fold telemetry-enabled behavior into the preferred runtime surfaces instead of maintaining a growing set of standalone observed API files.

## Preferred target surfaces
- `integrated_intelligence_app.py` for behavior-rich backend and recommendation logic
- `integrated_product_surface_app.py` for UI-facing summary and aggregation payloads

## Observed endpoint mapping

### Fold into `integrated_intelligence_app.py`
- observed recommendation generation
- observed recommendation why payload

### Fold into `integrated_product_surface_app.py`
- observed decision board summary
- observed attention-needed
- observed evaluation readiness
- observed recommendation cards
- observed recent activity

## Temporary standalone observed files to keep only until consolidation lands
- `observed_recommendation_api.py`
- `observed_board_summary_api.py`
- `observed_attention_needed_api.py`
- `observed_evaluation_readiness_api.py`
- `observed_recommendation_cards_api.py`
- `observed_recent_activity_api.py`

## Rule
Do not create additional standalone observed surfaces. New telemetry work should target the preferred runtime surfaces directly.
