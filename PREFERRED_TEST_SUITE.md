# Preferred Test Suite

## Primary suite
Use this set as the main behavior-confidence suite for the branch:
- `test_integrated_intelligence_app.py`
- `test_integrated_foundation_app.py`
- `test_invalid_inputs.py`
- `test_recommendation_generation.py`
- `test_recommendation_generation_failures.py`
- `test_recommendation_ranking.py`

## Why this suite matters
This set covers:
- integrated workflow behavior
- product-facing recommendation logic
- invalid enum/status handling
- recommendation generation and failure paths
- recommendation ranking behavior

## Secondary suite
Use these for narrower regression checks and historical checkpoint validation:
- `test_foundation_api_db.py`
- `test_foundation_events.py`
- `test_decision_workflow_api.py`
- `test_event_outputs.py`

## Rule going forward
Prefer expanding the primary suite around the canonical backend and product-surface runtimes instead of adding new test suites around deprecated standalone app surfaces.
