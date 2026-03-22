# System Architecture

## High-level architecture

### 1. Experience layer
- internal console UI
- customer-facing Shortlist UI
- admin surfaces
- API / webhook interfaces

### 2. Orchestration layer
- workflow engine
- agent router
- task queue
- policy / permissions layer
- scheduling and triggers

### 3. Intelligence layer
- source ingestion
- retrieval/search
- scoring and ranking
- evidence synthesis
- prediction and recommendation services

### 4. Data layer
- relational operational database
- vector/retrieval store
- event log / telemetry store
- document/object storage
- cache

### 5. Integrations layer
- market/news/data APIs
- internal tools
- analytics
- deployment infra
- messaging/notification systems

## Key design choices
- event-driven where useful
- modular agent interfaces
- explicit source provenance
- auditability for recommendations
- human-review path for high-impact outputs
- shared primitives across internal console and external apps

## Recommended backbone entities
- applications
- opportunities
- sources
- evaluations
- experiments
- agents
- artifacts
- recommendations
- incidents / events

## Strategic outcome
A shared architecture that can support both:
- the internal operating system
- the customer-facing Shortlist product
without forcing them to become the same thing.