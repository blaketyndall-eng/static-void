# Router Runtime Preferred Test Posture

## Preferred runtime candidates
### Backend
- `app_backend_router_packaged.py`
- transition alias candidate: `app_backend_next.py`

### Product surface
- `app_product_router_packaged.py`
- transition alias candidate: `app_product_next.py`

## Preferred confidence suite moving forward
### Backend router runtime
- `test_backend_router_packaged.py`

### Product router runtime
- `test_product_router_packaged.py`

### Supporting stability tests to retain
- `test_invalid_inputs.py`
- `test_recommendation_generation_failures.py`
- `test_recommendation_ranking.py`

## Why this matters
This shifts confidence toward the router-composed packaged runtimes before stable aliases are repointed. It reduces the risk of alias changes landing before the preferred path is properly exercised.

## Transition rule
Do not treat older packaged or non-packaged runtime variants as the preferred tested path once this posture is adopted.
