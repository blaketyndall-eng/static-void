# Router Runtime Status

## Current strongest implementation path
The strongest future-facing runtime surfaces on this branch are now the router-composed packaged apps:

### Backend
- `app_backend_router_packaged.py`
- Composes packaged backend routers for:
  - sources and opportunities
  - evaluations and outputs
  - recommendations

### Product surface
- `app_product_router_packaged.py`
- Composes packaged product routers for:
  - decision board
  - activity
  - evaluation views
  - recommendation views

## Why these are now preferred
- They use packaged storage and repositories.
- They align with the target router-based architecture.
- They reduce dependence on large monolithic runtime files.
- They are closer to the long-term maintainable shape of the codebase.

## Current role of earlier packaged runtimes
The earlier packaged runtimes remain useful as transition artifacts and validation checkpoints, but they are no longer the strongest long-term path:
- `app_backend_packaged.py`
- `app_product_surface_packaged.py`
- `app_backend_packaged_observed.py`
- `app_product_surface_packaged_observed.py`

## Next step
Use the router-composed packaged runtimes as the preferred migration target for canonical aliases once compatibility-shim conversion becomes available.
