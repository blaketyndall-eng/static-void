# Router Test Alignment Plan

## Goal
Shift the preferred test posture toward router-based packaged runtimes before stable aliases are repointed.

## Backend runtime target
- `app_backend_router_packaged.py`
- alias candidate: `app_backend_router.py`

## Product runtime target
- `app_product_router_packaged.py`
- alias candidate: `app_product_router.py`

## Test alignment priorities

### 1. Backend behavior confidence
- evaluation creation
- evidence record creation
- recommendation creation
- recommendation generation
- recommendation why payload
- opportunity stage updates
- source creation

### 2. Product-surface confidence
- decision board summary
- attention-needed payload
- recent activity feed
- evaluation summary
- evaluation readiness
- recommendation cards
- ranked recommendation summary

### 3. Observability confidence
- telemetry emission from router-based packaged runtimes
- event logging still present for backend mutations

## Transition rule
Do not retire earlier packaged runtime variants until the preferred confidence suite is centered on router-based packaged runtimes.

## Practical next step
Add router-based runtime tests or adapt the existing preferred suite to point at:
- `app_backend_router_packaged.py`
- `app_product_router_packaged.py`
