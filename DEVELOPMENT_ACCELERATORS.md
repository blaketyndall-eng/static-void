# Development Accelerators

## Goal
Make the current architecture easier to extend, test, and eventually stabilize around the router-based packaged path.

## What helps development most right now

### 1. Shared test helpers
- Use `test_support.py` to reset the database and telemetry state consistently.
- This reduces repeated setup logic across tests and makes future test additions faster.

### 2. Keep building only on the strongest path
The current strongest path is:
- `app_backend_router_full.py`
- `app_product_router_full.py`
- transition aliases that point at those runtimes

Avoid extending older standalone runtime surfaces unless needed for compatibility debugging.

### 3. Prefer packaged services and routers over large app files
- Put reusable logic into packaged services and repositories.
- Keep routers thin.
- Treat app composition files as assembly points, not logic homes.

### 4. Expand tests where they buy confidence fastest
Best areas to keep extending:
- router-based detail/read views
- router-based invalid-input handling
- router-based observability
- transition alias behavior

### 5. Prepare for eventual shim conversion
Even before in-place file replacement is available, keep exact shim targets and conversion order documented so the eventual cleanup becomes mechanical.

## Most useful next improvements
- unify more tests onto `test_support.py`
- continue adding missing router-based endpoints only on the full router path
- expand observability assertions on the router-full runtimes
- document the final preferred engineering/runtime path even more clearly
