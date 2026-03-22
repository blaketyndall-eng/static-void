# Data Model & Schema

## Core entities

### Application
- id
- name
- type (internal, customer-facing, experimental)
- status
- owner
- environments
- release_stage
- description
- dependencies
- KPI set
- created_at
- updated_at

### Opportunity
- id
- title
- category
- source_refs
- score
- rationale
- status
- owner
- discovered_at
- updated_at

### Source
- id
- name
- category
- access_type
- price_type
- freshness
- trust_score
- approved_use_cases
- constraints
- notes

### Evaluation
- id
- subject
- evaluation_type
- participants
- criteria
- evidence_refs
- summary
- score
- recommendation
- created_at

### Experiment
- id
- hypothesis
- system_area
- metric_targets
- start_date
- end_date
- outcome
- learnings
- next_action

### Agent
- id
- role
- tools
- permissions
- version
- owner
- status
- failure_modes
- performance_notes

### Artifact
- id
- type
- linked_entity_ids
- provenance
- content_ref
- created_at

## Data principle
Every important output should connect back to:
- where it came from
- what it influenced
- how trustworthy it was
- what happened afterward