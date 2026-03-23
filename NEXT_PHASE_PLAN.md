# Next Phase Plan

## Phase objective
Move from packaged shared modules to stable runtime usage of those packages, while reducing root-level duplication and preserving working behavior.

## Phase 2 priorities

### 1. Root compatibility shims
- Leave short root files that re-export packaged module locations.
- Use shims only for modules already moved into `packages/`.

### 2. Canonical runtime import migration
- Update `integrated_intelligence_app.py` imports to use package modules first.
- Update `product_surface_rewired.py` and related product-surface logic to use package modules first.
- Keep runtime aliases stable: `app_backend.py`, `app_product_surface.py`.

### 3. Observability consolidation
- Fold telemetry-enabled behavior into the canonical backend and product-surface runtimes.
- Deprecate standalone observed API files after the canonical surfaces absorb their behavior.

### 4. Router preparation
- Identify route clusters for future split:
  - backend: sources, opportunities, evaluations, outputs, recommendations, events
  - product: decision_board, activity, evaluation_views, recommendation_views

### 5. Cleanup discipline
- No new standalone app surfaces.
- No broad refactor mixed with feature expansion.
- Prefer import migration and consolidation over new endpoint growth.

## Success criteria for the next phase
- canonical app surfaces import mostly from package modules
- root compatibility shims exist for moved modules
- standalone observed files are clearly on the path to deprecation
- the branch is ready for router-based runtime refactor
