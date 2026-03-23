# Frontend-Facing API Map

## Decision Board
### `GET /api/v1/decision-board/summary`
Use for:
- top-level dashboard counts
- evaluation status distribution
- opportunity stage distribution
- latest recommendation widgets

### `GET /api/v1/decision-board/attention-needed`
Use for:
- tasks or alerts section
- evaluations missing recommendations
- evaluations without proposed recommendations

## Activity Feed
### `GET /api/v1/activity/recent`
Use for:
- recent activity panel
- audit/event feed in dashboard or evaluation pages

## Evaluation Views
### `GET /api/v1/evaluations/{evaluation_id}/summary`
Use for:
- evaluation overview page
- counts and latest recommendation snapshot
- evidence and artifact sidebars

### `GET /api/v1/evaluations/{evaluation_id}/readiness`
Use for:
- readiness badge or progress meter
- blockers and next-step suggestions

### `GET /api/v1/evaluations/{evaluation_id}/recommendation-cards`
Use for:
- recommendation card list
- why/rationale previews
- artifact count and evidence count badges

### `GET /api/v1/evaluations/{evaluation_id}/ranked-recommendation-summary`
Use for:
- ranked recommendation tables
- top recommendation hero card

### `GET /api/v1/evaluations/{evaluation_id}/outputs`
Use for:
- raw linked output panels
- evidence/artifact/recommendation inspection

## Recommendation Views
### `GET /api/v1/recommendations/{recommendation_id}/why`
Use for:
- explainability drawer
- rationale block
- linked score artifact and generation event context

## Recommendation Actions
### `POST /api/v1/evaluations/{evaluation_id}/generate-recommendation`
Use for:
- generate recommendation CTA
- recommendation draft flow
- score breakdown artifact generation

## Payload guidance
- Prefer summary endpoints for UI rendering.
- Prefer raw linked output endpoints for deeper drill-down and inspection surfaces.
- Avoid stitching multiple older standalone app surfaces in the frontend once the canonical runtime is selected.
