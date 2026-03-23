# Observability Implementation Next

## What was implemented
- `OBSERVABILITY_PLAN.md`
- `telemetry_logger.py`
- `telemetry_events.py`
- `telemetry_helpers.py`

## What should be implemented next
1. Emit telemetry from the product-surface summary endpoints.
2. Emit telemetry from recommendation generation and why endpoints.
3. Keep event logging and telemetry logging separate until the runtime surfaces are consolidated.
4. Fold telemetry into the canonical backend and aggregation surfaces after cleanup.

## Current blocker
A direct attempt to create a larger observed product-surface app file was interrupted by connector payload friction. This is implementation work to resume in the next cleanup/refactor pass, not a product strategy blocker.
