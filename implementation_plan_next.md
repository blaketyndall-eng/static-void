# Next Implementation Plan

## Immediate priorities
- wire repository-backed services into the live API surface
- initialize the SQLite database locally with `init_db.py`
- add automated API tests for create/list/update flows
- introduce Alembic after the repository-backed flow is stable

## Why this order
- It keeps the domain contract stable before migration churn.
- It validates that the ORM layer maps cleanly to the existing in-memory model.
- It gives us a clean checkpoint before refactoring into the final package layout.

## Migration checkpoint
Once repository-backed create/list/update flows are working, add:
1. `alembic init`
2. baseline migration for sources, opportunities, evaluations
3. local seed data for smoke testing
