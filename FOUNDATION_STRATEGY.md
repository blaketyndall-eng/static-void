# Foundation Strategy

## What is implemented now
- a minimal FastAPI application surface
- in-memory services for sources, opportunities, and evaluations
- request contracts for create flows
- SQLAlchemy session and ORM scaffolding for the first persistence pass

## Why this path
1. Prove the domain model and API contract before adding migration overhead.
2. Keep the first implementation inspectable and easy to refactor.
3. Establish a clean bridge from in-memory services to SQLAlchemy repositories.
4. Preserve the long-term plan for a bigger multi-module application structure.

## Next build sequence
1. Replace in-memory services with repository-backed services.
2. Add Alembic and create the first baseline migration.
3. Move root-level files into the final package layout when repo path constraints are cleared.
4. Add event logging and artifact storage.
5. Add tests for create/list/status workflows.
