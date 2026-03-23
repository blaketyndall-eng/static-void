# Compatibility Shim Map

## Purpose
Preserve stable imports and runtime aliases during the first package-refactor wave.

## Runtime aliases to preserve
- `app_backend.py` -> canonical backend/intelligence surface
- `app_product_surface.py` -> canonical product-surface aggregation
- `app_integrated.py` -> temporary compatibility alias for older integrated runtime references
- `integrated_intelligence_app_ranked.py` -> temporary compatibility alias for ranked runtime references

## Root module shims to preserve after wave 1 moves

### Domain and response models
- `domain_models.py`
- `decision_outputs_models.py`
- `product_surface_models.py`

### Storage and ORM
- `db_session.py`
- `db_models_sqlalchemy.py`
- `decision_outputs_db_models.py`

### Repositories
- `repository_sources.py`
- `repository_opportunities.py`
- `repository_evaluations.py`
- `repository_decision_outputs.py`

### Contracts
- `api_contracts.py`
- `decision_outputs_contracts.py`

## Shim pattern
Each root shim should do one thing only: re-export the new package location.

Example pattern:
```python
from packages.domain.core import *
```

## Removal rule
Do not remove shims until:
1. canonical runtime surfaces import from package locations
2. primary test suite passes against the package imports
3. deprecated app surfaces are no longer referenced in runtime docs
