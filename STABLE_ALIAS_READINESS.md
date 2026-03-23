# Stable Alias Readiness

## Goal
Define when the current stable aliases can be safely repointed to the router-based packaged runtimes.

## Current stable aliases
- `app_backend.py`
- `app_product_surface.py`

## Current next-stage candidates
- `app_backend_next.py`
- `app_product_next.py`

## Readiness criteria

### 1. Runtime confidence
- router-based packaged runtimes exist and are the preferred implementation path
- `app_backend_router_packaged.py` is stable for backend workflows
- `app_product_router_packaged.py` is stable for product-surface views

### 2. Test confidence
- router runtime tests are present and treated as preferred runtime tests
- supporting stability tests remain in place for invalid inputs, failures, and ranking behavior

### 3. Compatibility confidence
- shim conversion is at least partially complete or clearly prepared
- root-level compatibility risks are understood and documented

### 4. Deprecation confidence
- older packaged runtime variants are classified as transitional
- older standalone runtime variants are classified as historical or compatibility-only

## Repoint trigger
Once the router-based packaged runtimes are the preferred tested path and shim conversion is executable, the stable aliases can be repointed with much lower risk.
