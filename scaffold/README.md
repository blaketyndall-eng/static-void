# Foundation Scaffold

This directory is a practical starting point for implementation.

## What is here
- `api/main.py` — FastAPI entrypoint with health, readiness, and route registration
- `api/config.py` — environment-backed settings
- `domain/common.py` — shared base models and enums
- `domain/events.py` — append-only event schema
- `domain/sources.py` — source registry schema
- `domain/opportunities.py` — opportunity radar schema
- `domain/evaluations.py` — evaluation workflow schema

## Suggested next moves
1. Move this scaffold into the final package structure once repo path constraints are cleared.
2. Add persistence with SQLAlchemy and Alembic.
3. Add service and repository layers for events, sources, and opportunities.
4. Add background jobs for source sync and opportunity scoring.
