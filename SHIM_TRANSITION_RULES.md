# Shim Transition Rules

## Purpose
Guide Phase 2 import migration while keeping runtime behavior stable.

## Rule 1
For every shared module already moved into `packages/`, keep the root module temporarily as a compatibility shim until canonical runtimes import from the packaged location.

## Rule 2
Do not remove root compatibility shims until:
- canonical runtimes import from package modules
- the preferred test suite passes
- runtime docs no longer point to older root implementations

## Rule 3
Keep runtime alias files stable during import migration:
- `app_backend.py`
- `app_product_surface.py`

## Rule 4
Do not create new root implementations for logic that now belongs in packages.

## Rule 5
Observed standalone files should not gain new behavior. Their role is temporary until telemetry is folded into canonical surfaces.
