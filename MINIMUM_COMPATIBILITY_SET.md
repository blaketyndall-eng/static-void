# Minimum Compatibility Set

## Keep after merge
These files should remain as the minimum compatibility layer while the refactor is underway.

### Canonical entrypoints
- `app_backend.py`
- `app_product_surface.py`

### Temporary runtime aliases
- `app_integrated.py`
- `integrated_intelligence_app_ranked.py`

### Root module shims once wave 1 moves occur
- `domain_models.py`
- `decision_outputs_models.py`
- `product_surface_models.py`
- `db_session.py`
- `db_models_sqlalchemy.py`
- `decision_outputs_db_models.py`
- `repository_sources.py`
- `repository_opportunities.py`
- `repository_evaluations.py`
- `repository_decision_outputs.py`
- `api_contracts.py`
- `decision_outputs_contracts.py`

## Defer removal until
- runtime docs no longer reference older app surfaces
- primary suite passes on package imports
- canonical runtime surfaces are stable in the refactored layout

## Why this matters
This keeps the merge durable while minimizing the number of files that need to survive purely for backward compatibility.
