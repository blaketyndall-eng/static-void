# Preferred Engineering Path Status

## Current preferred implementation path
The preferred engineering path on this branch is now the full router-composed packaged runtime layer.

### Backend
- implementation: `app_backend_router_full.py`
- transition alias: `app_backend_full_next.py`

### Product surface
- implementation: `app_product_router_full.py`
- transition alias: `app_product_full_runtime.py`

## Why this path is preferred
- packaged foundations are already in place
- router-based composition is implemented
- core behavior tests exist
- observability tests exist
- alias bridge tests exist
- development helpers now support this path directly

## Development helpers that support this path
- `test_support.py`
- `test_factories.py`
- `test_assertions.py`

## Files that should receive new feature work first
- packaged routers
- packaged services
- router-composed packaged runtimes
- tests built around the router-full path

## Files that should not be the default place for new work
- older standalone runtime surfaces
- earlier packaged runtime variants that predate router composition
- observed standalone surfaces unless needed for compatibility debugging

## Practical rule
When in doubt, build and test on the router-full packaged path first. Treat older surfaces as transitional unless a compatibility need requires touching them.
