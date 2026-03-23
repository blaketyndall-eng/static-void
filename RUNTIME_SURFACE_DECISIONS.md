# Runtime Surface Decisions

## Keep

### Canonical backend and intelligence surface
- `integrated_intelligence_app.py`
- Purpose: core CRUD, linked workflows, recommendation generation, explainability, event logging.

### Temporary product-facing aggregation surface
- `integrated_product_surface_app.py`
- Purpose: Decision Board and evaluation UI summary payloads while aggregation remains separate.

### Temporary entrypoint aliases
- `app_integrated.py`
- `integrated_intelligence_app_ranked.py`
- Purpose: compatibility shims until the top-level entrypoint can be cleanly repointed.

## Deprecate after merge
- `main.py`
- `api_app.py`
- `foundation_api.py`
- `foundation_api_db.py`
- `foundation_api_db_events.py`
- `decision_outputs_api.py`
- `decision_workflow_api.py`
- `recommendation_generation_api.py`
- `recommendation_ranking_api.py`
- `decision_board_summary_api.py`
- `evaluation_detail_summary_api.py`
- `recommendation_cards_api.py`
- `ranked_recommendation_summary_api.py`
- `recent_activity_api.py`
- `attention_needed_api.py`
- `evaluation_readiness_api.py`

## Rule going forward
Do not add any new standalone app surfaces. New behavior should land in the canonical backend surface or the temporary product aggregation surface until the package refactor is complete.
