# Surface Decision Note

## Current app layers on the branch

### 1. Backend workflow and intelligence surface
- Preferred file: `integrated_intelligence_app.py`
- Purpose: core CRUD, linked workflow behavior, recommendation generation, explainability, and event logging.
- Use this as the main backend runtime candidate.

### 2. Product-facing aggregation surface
- Preferred file: `integrated_product_surface_app.py`
- Purpose: Decision Board and evaluation UI summary payloads.
- Use this as the current aggregation/UI-facing surface.

### 3. Compatibility and checkpoint surfaces
- Files such as `foundation_api.py`, `foundation_api_db.py`, `foundation_api_db_events.py`, `decision_workflow_api.py`, and others remain useful for narrower validation and review history.
- These are not preferred long-term runtime surfaces.

## Recommended direction
1. Keep `integrated_intelligence_app.py` as the canonical behavior-rich backend app.
2. Keep `integrated_product_surface_app.py` as a temporary aggregation layer for UI-facing payloads.
3. After review, fold product-surface summary endpoints into the canonical backend app or expose them through routers mounted off the same runtime.
4. Preserve aliases only as short-term compatibility shims.

## Why this split currently makes sense
- It lets the branch keep shipping useful product payloads without blocking on package refactor work.
- It keeps behavioral logic and UI aggregation distinct while the system is still evolving.
- It reduces the risk of another round of parallel ad hoc app files.
