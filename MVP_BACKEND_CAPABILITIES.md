# MVP Backend Capabilities

## Current core capabilities
- create and list sources
- create opportunities and update opportunity stage
- create evaluations and update evaluation status
- attach evidence links to evaluations
- create evidence records, artifacts, and recommendations linked to evaluations
- retrieve all linked outputs for an evaluation
- generate rule-based recommendation drafts from evaluation context
- persist score breakdown artifacts for generated recommendations
- explain why a recommendation exists through a dedicated endpoint
- rank multiple recommendations for the same evaluation
- emit append-only event logs for major mutations and generated outputs

## Product implications
This branch now supports the minimum backend behavior required for an evidence-first decision product:
1. collect inputs
2. structure an evaluation
3. attach supporting evidence
4. produce recommendation outputs
5. explain recommendation logic
6. compare and rank competing recommendations
7. preserve a durable audit trail

## What this is ready to support next
- decision board UI wiring
- shortlist generation surfaces
- recommendation review workflows
- evidence-first briefing artifacts
- lightweight collaboration and approval states
