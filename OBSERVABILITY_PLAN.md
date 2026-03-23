# Observability Plan

## Goal
Add lightweight observability around the canonical backend and product-facing surfaces before introducing more intelligence complexity.

## First telemetry targets

### Backend operational events
- `api.request.started`
- `api.request.completed`
- `api.request.failed`
- `db.query.executed`
- `db.query.failed`

### Decision workflow events
- `evaluation.created`
- `evaluation.status_updated`
- `evaluation.evidence_record_created`
- `evaluation.artifact_created`
- `recommendation.created`
- `recommendation.generated`
- `recommendation.ranked`

### Product-surface summary events
- `decision_board.summary_viewed`
- `decision_board.attention_needed_viewed`
- `activity.recent_viewed`
- `evaluation.summary_viewed`
- `evaluation.readiness_viewed`
- `recommendation.cards_viewed`
- `recommendation.why_viewed`

## First metrics
- request latency by endpoint
- request failure count by endpoint
- recommendation generation count
- recommendation generation failure count
- evaluations with no recommendation
- average readiness score
- recommendation count per evaluation
- recent activity item count returned

## Trace-worthy flows
1. create evaluation
2. create evidence record
3. generate recommendation
4. fetch recommendation why payload
5. fetch decision board summary

## Implementation order
1. Add lightweight instrumentation helpers.
2. Emit structured JSONL telemetry alongside existing event logs.
3. Instrument canonical backend surface first.
4. Instrument product-surface aggregation second.
5. Replace or augment with OpenTelemetry after runtime consolidation.

## Tech debt boundary
Full OpenTelemetry rollout remains deferred until runtime consolidation and package refactor reduce instrumentation churn.
