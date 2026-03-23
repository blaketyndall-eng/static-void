# Canonical Entrypoints

## Preferred backend/intelligence runtime
- `app_backend.py`
- Alias target: `integrated_intelligence_app.py`

## Preferred product-surface runtime
- `app_product_surface.py`
- Alias target: `product_surface_rewired.py`

## Why these aliases exist
- They provide stable names while direct top-level entrypoint updates remain constrained.
- They create a cleaner bridge to the eventual package-based runtime layout.
- They reduce ambiguity for reviewers, local runners, and future deployment wiring.

## Rule
Use these aliases as the preferred entrypoints for new runtime documentation and future consolidation work.
