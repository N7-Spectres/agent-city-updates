# Communication & Perception — Backlog

## v0.8 Stage 2 — Visitor-Linked Physical Actions

Stage 1 grounding is complete.

Real shared visitor/citizen activity remains intentionally deferred until Simulation defines the physical action lifecycle.

Communication needs Stage 2 Simulation interfaces for:

- visitor identity + citizen identity participant binding
- authoritative co-location/proximity validation
- requested local objective/direction/point
- meter-scale path/movement legality
- duration
- energy requirements
- tool/equipment requirements
- shared action start/status/failure/completion
- stable Simulation action ID
- stable completion/physical event ID when distinct
- validated observation ID(s) produced by the action
- authoritative participant positions during/after the action

Communication will attach:

- source visit ID
- source exchange ID
- visitor request text
- citizen response/intention

but will not create physical state.

See branch document:

`docs/departments/communication/SHARED_ACTION_CONTRACT.md`

## Stage 2 Spatial Communication

When Simulation adds continuous movement:

- preserve exact source/time for last-known positions
- distinguish current co-location from stale remembered coordinates
- use validated position/action state, not visitor prose
- retain `radius_m` / tool semantics for observations
- do not infer hidden resource geometry from repeated point observations

## Visitor Claim Provenance — Future Depth

Stage 1 grounds visitor claims in prompt semantics and preserves raw visitor conversation.

If later required, add structured visitor-claim provenance only with transcript-grounded extraction comparable to citizen claims.

Do not create a broad visitor-claim extractor merely to make Stage 1 work.

## Emergent Place Naming

Future place naming should remain social information distinct from physical coordinate identity.

Communication may eventually carry:

- proposed place names
- aliases
- who coined/adopted them
- naming discussion

but Simulation owns the physical feature/site identity and Memory owns retained naming history.

## Existing Deferred Communication Depth

- claim contradiction/reliability reconciliation
- third-party overhearing
- physical notice boards/logs/records
- invented long-distance communication after real research/material/fabrication prerequisites
- diagnostic aggregation/backfill for degraded claim extraction

## Ongoing Audit Rules

As Living World systems expand:

- audit all new prompt/context sources for raw hidden Simulation truth
- audit remote live state leakage
- audit concept-art/visual metadata so presentation never becomes capability
- preserve v0.7 raw-exchange-first talk reliability
- keep personality expressive while factual nouns stay evidence-grounded
