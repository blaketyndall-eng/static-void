# Canonical Alias Repoint Plan

## Goal
Prepare the final move from transitional aliases toward router-based packaged runtime aliases without breaking current usage.

## Current candidates
### Backend
- current stable alias: `app_backend.py`
- router-based candidate: `app_backend_router.py`
- target implementation: `app_backend_router_packaged.py`

### Product surface
- current stable alias: `app_product_surface.py`
- router-based candidate: `app_product_router.py`
- target implementation: `app_product_router_packaged.py`

## Repoint sequence
1. Keep current aliases stable while router-based candidates exist in parallel.
2. Align preferred tests and docs to the router-based candidates.
3. Once shim conversion is sufficiently complete, repoint the stable aliases to the router-based packaged runtimes.
4. Preserve temporary compatibility aliases for one transition window.

## Safety rule
Do not repoint the current stable aliases until:
- router-based packaged runtimes are the preferred tested path
- root shim conversion is far enough along to preserve imports
- deprecation targets are clearly classified as transition-only or historical

## Practical current state
This plan can advance now through alias candidates and docs, even though the final in-place alias replacement may still depend on the current file-update constraints.
