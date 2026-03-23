# Architecture Status

## Current recommended backend surface
- `integrated_foundation_app.py` is the most complete application surface on this branch.
- `app.py` should be updated in a cleanup pass to point at the integrated app.
- Earlier app variants remain useful as checkpoints, but they are no longer the preferred runtime surface.

## What is now implemented
- source CRUD foundation
- opportunity CRUD foundation and stage transitions
- evaluation CRUD foundation and status transitions
- linked evidence, artifact, and recommendation records
- append-only JSONL event logging
- repository-backed persistence layer with SQLAlchemy ORM models
- local DB bootstrap, seed path, and smoke tests

## Strategic implication
This branch now proves the minimum backend shape needed for a real decision intelligence product core:
1. ingest and organize signals
2. structure an evaluation
3. attach evidence and artifacts
4. generate recommendations
5. preserve an audit trail

## Recommended next cleanup
1. make the integrated app the single canonical entrypoint
2. collapse deprecated parallel entrypoints after review
3. fold dependencies into one install path
4. migrate root files into the final package layout when repo path constraints allow
