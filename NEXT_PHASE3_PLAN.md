# Next Phase 3 Plan

## Phase objective
Stabilize the refactor by converting root shared modules into shims, consolidating telemetry into canonical packaged runtimes, and preparing the eventual router split.

## Phase 3 priorities

### 1. Root compatibility shim conversion
- Convert moved shared modules into thin re-export shims.
- Keep shim removal deferred until runtime and test posture are stable.

### 2. Canonical alias cleanup
- Prefer `app_backend.py` and `app_product_surface.py` as stable user-facing entrypoints.
- Plan eventual repointing to packaged runtimes after shim conversion is in place.

### 3. Observability consolidation
- Fold telemetry-enabled behavior into packaged backend and packaged product-surface runtimes.
- Reduce reliance on standalone observed API files.

### 4. Router preparation
- Group endpoints by future router clusters:
  - backend: sources, opportunities, evaluations, outputs, recommendations, events
  - product: decision_board, activity, evaluation_views, recommendation_views

### 5. Controlled deprecation
- Mark older standalone runtime and observed files as historical or compatibility-only.
- Avoid adding any new standalone surfaces.

## Success criteria
- moved shared root modules are shimmed
- packaged runtimes are the effective implementation base
- telemetry strategy is folded into those runtimes
- router split can begin without ambiguity around canonical surfaces
