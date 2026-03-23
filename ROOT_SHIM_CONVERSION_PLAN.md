# Root Shim Conversion Plan

## Goal
Convert moved shared root modules into lightweight compatibility shims after verifying packaged runtime usage is stable.

## First shim targets
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
Each file should re-export from its new package location only.

Example:
```python
from packages.domain.core import *
```

## Order
1. Convert model files first.
2. Convert storage files second.
3. Convert repository files third.
4. Convert contract files fourth.
5. Then update canonical aliases and docs to prefer packaged runtimes.

## Safety rule
Do not convert a root module into a shim until the packaged runtime surface that depends on it exists or is already proven.
