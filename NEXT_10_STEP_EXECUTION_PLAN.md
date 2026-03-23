# Next 10-Step Execution Plan

## Objective
Move from a powerful branch with multiple runtime surfaces into a merge-ready, refactor-ready codebase with one canonical backend surface and one canonical product-surface aggregation layer.

## Step 1 — Freeze runtime growth
- Do not add new standalone app surfaces.
- Keep only one backend/intelligence candidate and one product-surface candidate moving forward.

## Step 2 — Declare canonical entrypoints
- Backend/intelligence: `integrated_intelligence_app.py`
- Product-surface aggregation: `product_surface_rewired.py`
- Compatibility aliases can remain until direct entrypoint updates are possible.

## Step 3 — Mark deprecated surfaces
- Treat older foundation/checkpoint apps as review-history only.
- Keep them temporarily, but stop routing new work into them.

## Step 4 — Consolidate product-surface logic
- Use `product_surface_services.py` and `product_surface_models.py` as the shared product aggregation spine.
- Route future summary work through those shared builders.

## Step 5 — Consolidate observability direction
- Fold observed endpoint behavior into the canonical backend and product-surface candidates.
- Stop creating standalone observed API files.

## Step 6 — Unify install/run/test posture
- One documented runtime path
- One documented preferred test suite
- Keep compatibility notes separate from primary setup docs

## Step 7 — Start package refactor wave 1
- Move domain models
- Move repositories
- Move DB/session files
- Move contracts
- Preserve root compatibility shims

## Step 8 — Prepare router split
- Backend routers: sources, opportunities, evaluations, outputs, recommendations, events
- Product routers: decision_board, activity, evaluation_views, recommendation_views

## Step 9 — Complete migration/observability follow-through
- baseline migration workflow
- telemetry folded into canonical surfaces
- OpenTelemetry deferred until surface consolidation reduces churn

## Step 10 — Merge and clean structure immediately after
- Merge for capability
- Refactor for durability
- Avoid post-merge feature sprawl until runtime and package structure are stable

## Immediate executable moves
1. Add explicit canonical alias files for backend and product surfaces.
2. Update review docs to point at those aliases.
3. Treat everything else as temporary compatibility or historical checkpoints.
