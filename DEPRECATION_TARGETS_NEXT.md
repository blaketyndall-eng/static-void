# Deprecation Targets After Router Checkpoint

## Highest-priority deprecation targets
These files should move toward compatibility-only or historical status once canonical aliases can point at router-composed packaged runtimes.

### Earlier packaged runtime variants
- `app_backend_packaged.py`
- `app_product_surface_packaged.py`
- `app_backend_packaged_observed.py`
- `app_product_surface_packaged_observed.py`

### Earlier non-router packaged helpers used mainly as intermediate runtime steps
- `product_surface_services_packaged.py` should remain as a shared service helper, but not as a reason to preserve older packaged runtimes.

### Older standalone observed surfaces
- `observed_recommendation_api.py`
- `observed_board_summary_api.py`
- `observed_attention_needed_api.py`
- `observed_evaluation_readiness_api.py`
- `observed_recommendation_cards_api.py`
- `observed_recent_activity_api.py`

### Older standalone non-packaged runtime surfaces
- `integrated_intelligence_app.py`
- `integrated_product_surface_app.py`
- `product_surface_rewired.py`
- `integrated_foundation_app.py`
- `foundation_api.py`
- `foundation_api_db.py`
- `foundation_api_db_events.py`
- `decision_workflow_api.py`
- `decision_outputs_api.py`
- `recommendation_generation_api.py`
- `recommendation_ranking_api.py`

## Rule
Do not remove these yet. Reclassify them as transition or historical surfaces first, then remove only after:
1. canonical aliases point to router-composed packaged runtimes
2. preferred test posture is aligned to those runtimes
3. shim conversion is complete enough to preserve compatibility
