# Runtime Cleanup Checkpoint

## Canonical runtime
- `app_sys.py` is now the canonical unified runtime entrypoint for the console on the `implement/foundation-scaffold` branch.
- Versioned runtime files remain in the repo as historical build checkpoints.

## Current operating layers included in the canonical runtime
- Decision intelligence engines: ingestion, reasoning, output, bias, benchmark, feedback
- Execution layers: action workflow execution, company operator, workforce coordination
- Existing console surfaces: control room, executive dashboard, OS summary, global summary, master console variants

## Cleanup guidance
1. Prefer `app_sys.py` for new local runs and integration wiring.
2. Treat `app_sys_v26.py` through `app_sys_v34.py` as checkpoint snapshots unless a specific test imports one of them.
3. In a later cleanup pass, migrate tests and imports toward `app_sys.py` so older runtime files can be deprecated more aggressively.
4. Normalize remaining naming drift, especially files using `_v2` suffixes where the newer schema is now canonical.

## Next valuable checkpoint
- Finish Venture Builder end to end.
- After Venture Builder, perform a route and runtime consolidation checkpoint to reduce duplicate summary surfaces and deprecate older runtime files more safely.
