# Post-Merge Cleanup Plan

## Objective
Merge this branch for capability, then immediately clean the runtime surface and prepare the package refactor.

## Phase 1 — Immediate cleanup
1. Repoint the top-level canonical entrypoint to the integrated intelligence runtime.
2. Keep `integrated_product_surface_app.py` as the only temporary aggregation surface.
3. Mark deprecated app surfaces as review-history only.
4. Fold install, run, and test instructions into one path.

## Phase 2 — Runtime simplification
1. Remove redundant standalone summary APIs once their logic is represented in the product aggregation surface.
2. Remove redundant standalone generation/ranking APIs once their logic is represented in the integrated intelligence surface.
3. Keep temporary compatibility aliases only until the package refactor lands.

## Phase 3 — Refactor preparation
1. Move domain, repository, storage, and contract modules first.
2. Rebuild app surfaces as routers over imported package modules.
3. Preserve root compatibility shims during the refactor window.

## Success criteria
- one preferred backend runtime
- one temporary product aggregation runtime
- no new standalone app files
- stable tests preserved during cleanup
