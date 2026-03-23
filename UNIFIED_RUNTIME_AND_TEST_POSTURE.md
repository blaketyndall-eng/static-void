# Unified Runtime and Test Posture

## Preferred runtime commands

### Backend and intelligence surface
- Entry: `app_backend.py`
- Start command: `uvicorn app_backend:app --reload`

### Product-surface aggregation
- Entry: `app_product_surface.py`
- Start command: `uvicorn app_product_surface:app --reload`

## Preferred test posture
Run these as the primary confidence suite for current behavior:
- `pytest test_integrated_intelligence_app.py`
- `pytest test_integrated_foundation_app.py`
- `pytest test_invalid_inputs.py`
- `pytest test_recommendation_generation.py`
- `pytest test_recommendation_generation_failures.py`
- `pytest test_recommendation_ranking.py`

## Secondary validation tests
Keep these for narrower regression coverage and review history:
- `test_foundation_api_db.py`
- `test_foundation_events.py`
- `test_decision_workflow_api.py`
- `test_event_outputs.py`

## Rule
All new runtime documentation and future cleanup work should point to `app_backend.py` and `app_product_surface.py` first, not older checkpoint entrypoints.
