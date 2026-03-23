# Router Runtime Observability Posture

## Preferred observable runtime path
The preferred observable runtime path on this branch is now the router-based packaged runtime layer.

### Backend
- runtime: `app_backend_router_packaged.py`
- transition alias: `app_backend_next.py`
- observability confidence: `test_backend_router_telemetry.py`

### Product surface
- runtime: `app_product_router_packaged.py`
- transition alias: `app_product_next.py`
- observability confidence: `test_product_router_observability.py`

## Why this matters
This establishes that the router-based packaged runtimes are not only the strongest structural path, but also the strongest observable path for future cleanup and alias repointing.

## Rule
Do not expand observability work on older standalone runtime surfaces unless needed for compatibility debugging. Prefer adding observability only to the router-based packaged path.
