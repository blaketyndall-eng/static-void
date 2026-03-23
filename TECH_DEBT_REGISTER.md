# Tech Debt Register

## Current accepted tech debt

### 1. Parallel app surfaces
- Multiple app entrypoints still exist because the repo connector blocked some direct file updates.
- Preferred direction: make `integrated_intelligence_app.py` canonical and keep aliases only temporarily.

### 2. Root-level module sprawl
- Runtime, repositories, contracts, and models remain at the repo root.
- Preferred direction: migrate into the package layout documented in `PACKAGE_REFACTOR_PLAN.md`.

### 3. Split intelligence/ranking surfaces
- Recommendation generation and ranking currently exist in separate helper and API files.
- Preferred direction: fold ranking and recommendation generation into the canonical integrated runtime surface.

### 4. Lightweight event logging
- Event logging is JSONL-based and useful for auditability, but not yet instrumented with proper tracing/metrics.
- Preferred direction: add OpenTelemetry and consolidate event paths.

### 5. Partial migration scaffolding
- Alembic scaffolding exists, but the branch is not yet running a full baseline migration workflow.
- Preferred direction: finish migration config after runtime consolidation.

### 6. No UI aggregation layer yet
- The backend is strong, but the Decision Board-style aggregate payloads are still thin.
- Preferred direction: add dashboard and evaluation aggregation endpoints for product-facing UI surfaces.

## Prioritization
1. Canonical runtime consolidation
2. Package refactor
3. Observability
4. UI aggregation layer
5. Migration completion
6. Semantic retrieval and orchestration
