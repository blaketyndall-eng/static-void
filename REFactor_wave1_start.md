# Wave 1 Refactor Start

## Goal
Begin the package refactor with the safest, least-coupled modules while preserving root compatibility during the transition.

## First files to move when nested-path writes are possible
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

## Root compatibility rule
When these modules move, leave short root compatibility files that re-export the new package locations until the runtime surfaces are fully updated.

## Why these files first
- They are more reusable than runtime app surfaces.
- They reduce duplicated import paths later.
- They create the cleanest foundation for router-based consolidation.

## What should not move first
- Do not move every app surface at once.
- Do not mix runtime consolidation and package refactor in one giant step.
- Keep the canonical alias entrypoints stable during this wave.
