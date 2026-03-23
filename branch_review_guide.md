# Branch Review Guide

## Preferred runtime surfaces
- `app_integrated.py` — explicit entrypoint to the integrated app
- `integrated_foundation_app.py` — most complete backend surface on the branch
- `RUNBOOK.md` — local setup, initialization, run, and test instructions
- `ARCHITECTURE_STATUS.md` — current architectural status and cleanup direction
- `PR_CHECKPOINT.md` — branch summary and merge recommendation

## Preferred tests
- `test_integrated_foundation_app.py`
- `test_invalid_inputs.py`
- `test_foundation_events.py`
- `test_foundation_api_db.py`
- `test_decision_workflow_api.py`

## Checkpoint files
These remain useful for review history and narrower isolated testing, but they are not the preferred long-term entrypoints:
- `main.py`
- `api_app.py`
- `foundation_api.py`
- `foundation_api_db.py`
- `foundation_api_db_events.py`
- `decision_outputs_api.py`
- `decision_workflow_api.py`

## Review focus
1. Confirm the integrated app covers the full CRUD and linked workflow path.
2. Confirm event logs exist for important mutations.
3. Confirm repositories map cleanly between ORM and domain records.
4. Confirm enum and status failures return predictable errors.
5. Confirm the branch is ready for cleanup into a single canonical runtime surface.
