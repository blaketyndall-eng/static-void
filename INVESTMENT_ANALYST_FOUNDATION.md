# Investment Analyst Foundation

## Goal
Extend the current decision-intelligence architecture into a multi-category investment analyst system that supports swing trades, options, crypto, and prediction markets.

## Shared investment foundation added
### Domain
- `packages/domain/investment.py`
- Shared thesis object plus category-specific profile extensions.

### Contracts
- `packages/contracts/investment.py`
- Request schemas for thesis creation, status updates, evidence attachment, and category-specific profile creation.

## Core architectural principle
Use one shared investment thesis core and separate category-specific strategy layers.

### Shared core responsibilities
- thesis state
- conviction
- entry / target / invalidation
- catalysts
- risk flags
- recommendation state
- evidence links
- review cadence

### Category-specific extensions
- swing trade profile
- options profile
- crypto profile
- prediction market profile

## Recommended next implementation steps
1. add packaged repositories for investment theses and profile extensions
2. add packaged storage/ORM support for theses and profiles
3. add backend routers for investment thesis creation and retrieval
4. add agent or engine scaffolds for category-specific evaluation logic
5. add product-facing views for active theses, watchlists, and catalyst summaries

## Why this fits the current repo
The current repo already supports:
- evidence and artifact tracking
- recommendations and rankings
- explainability
- router-based packaged runtimes
- observability and test scaffolding

That makes it a strong base for investment analyst workflows as long as the domain model becomes asset-aware.
