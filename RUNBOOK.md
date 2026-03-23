# Local Runbook

## Install
1. Create a Python 3.11 virtual environment.
2. Install base project dependencies from `pyproject.toml`.
3. Install foundation extras from `requirements_foundation.txt`.

## Initialize
1. Run `python init_db.py` to create local tables.
2. Run `python seed_data.py` to load example records.

## Start API
- Run `uvicorn app:app --reload`

## Test
- Run `pytest test_foundation_api_db.py test_foundation_events.py`

## Current canonical entrypoint
- `app.py` delegates to `foundation_api_db_events.py`

## Current focus
- repository-backed CRUD
- append-only event logging
- migration scaffolding
- smoke tests for create/list/update flows
