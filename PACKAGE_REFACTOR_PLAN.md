# Package Refactor Plan

## Goal
Move the current root-level backend modules into a durable package structure once repo path constraints allow nested-path writes.

## Target structure
/apps
  /api
    main.py
    routers/
      sources.py
      opportunities.py
      evaluations.py
      outputs.py
      recommendations.py
      events.py
/packages
  /domain
    core.py
    decision_outputs.py
  /repositories
    sources.py
    opportunities.py
    evaluations.py
    decision_outputs.py
  /services
    recommendation_intelligence.py
    ranking.py
    event_logger.py
  /storage
    db_session.py
    orm_core.py
    orm_outputs.py
  /contracts
    api_core.py
    api_outputs.py

## Migration sequence
1. Move pure model files first.
2. Move repositories and DB session files.
3. Move service helpers like intelligence and ranking.
4. Move API contracts.
5. Rebuild the canonical integrated app in `/apps/api/main.py` using imports from packages.
6. Leave temporary root compatibility files that re-export the new package modules.

## Why this order
- It preserves the current working behavior.
- It reduces breakage risk while the branch is still evolving.
- It makes the final app structure easier to review and maintain.

## Current canonical candidates to preserve during refactor
- `integrated_intelligence_app.py`
- `recommendation_intelligence.py`
- `recommendation_ranking.py`
- `repository_decision_outputs.py`
- `repository_evaluations.py`
- `repository_opportunities.py`
- `repository_sources.py`
