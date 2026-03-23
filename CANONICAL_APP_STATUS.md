# Canonical App Status

## Current strongest runtime surface
- `integrated_intelligence_app.py` is now the strongest and most complete application surface on this branch.
- `app_integrated.py` points to the earlier integrated foundation layer and should be replaced in a later cleanup pass.
- `app.py` still points to an older checkpoint because the direct update path was blocked by the connector during an earlier edit attempt.

## Why `integrated_intelligence_app.py` is preferred
It combines:
- source, opportunity, and evaluation CRUD
- linked evidence, artifact, and recommendation workflows
- append-only event logging
- rule-based recommendation generation
- score breakdown artifact creation
- recommendation explainability through a dedicated why endpoint

## Recommended cleanup direction
1. Repoint `app.py` to `integrated_intelligence_app.py`
2. Add a lightweight compatibility alias file once the repo connector allows direct update
3. Collapse older app variants after review and merge
4. Move runtime modules into final package layout when nested-path writes are possible
