# Merge Cleanup Checklist

## Canonical surface decisions
- [ ] Make `integrated_intelligence_app.py` the single preferred runtime surface
- [ ] Repoint `app.py` to the canonical app when direct update is possible
- [ ] Keep `app_integrated.py` and `integrated_intelligence_app_ranked.py` only as temporary compatibility aliases
- [ ] Mark checkpoint app variants as deprecated after merge

## Dependency cleanup
- [ ] Fold `requirements_foundation.txt` dependencies into the primary install path
- [ ] Confirm local install works from one documented setup path
- [ ] Document exact test command and runtime command in one place

## Runtime cleanup
- [ ] Collapse overlapping app variants after review
- [ ] Keep one event log path for the canonical app
- [ ] Confirm database bootstrap and seed scripts still match the canonical app flow

## Testing cleanup
- [ ] Run and confirm the preferred test suite
- [ ] Keep failure-path tests for enums and missing records
- [ ] Keep integrated intelligence tests as the main behavioral confidence suite

## Package refactor checkpoint
- [ ] Move root modules into final package layout when nested-path writes are available
- [ ] Split routers, services, repositories, and models into stable package modules
- [ ] Preserve compatibility aliases during the refactor window
