# Branch Merge Recommendation

## Recommendation
Merge this branch after a light cleanup pass.

## Why it is ready for that stage
The branch now proves the core backend behavior needed for an evidence-first decision product:
- source, opportunity, and evaluation flows
- linked evidence, artifacts, and recommendations
- event logging and recent activity feed
- recommendation generation with transparent rule-based scoring
- explainability via score artifacts and why endpoints
- recommendation ranking
- product-facing summary payloads for the Decision Board and evaluation views

## What should merge now
- domain and persistence groundwork
- repository-backed CRUD foundations
- decision output models and repositories
- recommendation intelligence and ranking helpers
- integrated backend and product-surface runtime candidates
- smoke tests, invalid-input tests, and failure-path tests
- runbook, reviewer notes, and refactor planning docs

## What should be treated as immediate post-merge cleanup
1. Repoint the top-level canonical entrypoint when direct update is available.
2. Collapse deprecated checkpoint app variants.
3. Unify summary/product-surface routes under the final runtime layout.
4. Complete the package refactor described in `PACKAGE_REFACTOR_PLAN.md`.
5. Finish migration and observability follow-through.

## Merge posture
- Merge for capability and momentum.
- Clean up structure immediately after merge.
- Avoid adding more parallel app surfaces before the refactor pass.
