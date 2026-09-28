# World & Simulation — State

_Last updated: 2026-09-28_
_Current shipped release: v0.5.0_
_Active implementation branch: `simulation/v0.6-research-discovery`_
_Branch head: `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`_

## Mission

Own physical truth.

> **The AI may decide intent. The simulation decides reality.**

For v0.6 this also means:

> **World truth may exist before any citizen knows it.**

## Shipped Foundation Preserved

The v0.6 branch starts from immutable shipped v0.5.0 commit:

`d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`

It preserves:

- travel / survey / extract / deposit / charge / wait
- face-to-face talk with source-linked conversation integrity
- fabrication and equipment
- construction projects and structures
- cargo-capacity and extraction-tool effects
- return-energy reserve
- stable job/project IDs
- local coordinate groundwork

## v0.6 Research & Discovery — Implemented on Department Branch

### Hidden World Truth

New internal table:

- `world_properties`

It stores physical facts that may exist before discovery.

Examples currently include:

- material response properties
- location field properties

This table is deliberately **not included** in ordinary `/api/state`.

### Discovery Events

New persisted table:

- `discoveries`

Stable fields:

- `id`
- `discovery_kind` — currently `deposit` or `world_property`
- `subject_type`
- `subject_id`
- `property_id` when applicable
- `citizen_id`
- `location_id`
- `source_job_id`
- `discovered_minute`
- `summary`

A survey or experiment may produce a validated discovery. A discovery is an event/knowledge anchor, not a global mind-meld.

### Citizen Knowledge

New persisted table:

- `citizen_knowledge`

Stable fields:

- `citizen_id`
- `discovery_id`
- `learned_minute`
- `acquisition_kind`
- `source_type`
- `source_id`
- `verification_state`

Direct survey/experiment discoveries grant knowledge only to the discovering citizen.

No other citizen receives that knowledge automatically.

New helper module:

- `agent_city/knowledge.py`

Useful interfaces:

- `grant_citizen_knowledge(...)`
- `known_properties_for(citizen_id)`
- `known_deposits_for_citizen(citizen_id)`
- `knowledge_payload_for(citizen_id)`

Communication may later use `grant_citizen_knowledge` only after a real transfer event and only when the transferred fact can be tied to a validated discovery.

### Experiments

New legal action:

- `experiment`

Current generic physical methods:

- thermal-response assay
- electrical-response assay
- mechanical-response assay

These methods are not technologies and do not reveal which hidden property exists.

Experiment requirements:

- citizen at Seed Site
- real stored native material sample
- real sample consumption
- energy cost
- timed job

Experiment results persist in:

- `experiment_results`

Fields include:

- stable result `id`
- `job_id`
- `citizen_id`
- `location_id`
- `material`
- `method`
- `outcome`
- `discovery_id` when successful
- `summary`
- `completed_minute`

Current outcomes:

- `discovery`
- `verified`
- `inconclusive`

An inconclusive experiment is a real persisted result, not erased failure.

### Reproducible Learned Processes

A successful property discovery creates a citizen-scoped verification process in:

- `learned_processes`

Fields:

- `id`
- `citizen_id`
- `process_key`
- `name`
- `process_kind`
- `source_discovery_id`
- `learned_minute`

These are repeatable verification procedures derived from real discoveries, not a visible technology tree and not automatic fabrication unlocks.

### Survey / Location Knowledge

Field surveys can now be repeated.

A survey may:

- reveal a previously hidden deposit
- independently confirm a deposit another citizen found
- reveal a hidden location property
- produce no new finding

Repeated surveys remain legal rather than using hidden truth to decide whether the action is offered.

Locations now expose safe accumulated facts through:

- `state.locations[].known_facts`

Unknown facts are absent.

### Ordinary State Boundary

`snapshot()` is now explicitly civilization-facing safe state.

Important changes:

- `world_properties` is never returned
- undiscovered deposits are never returned
- discovered deposits no longer expose hidden reserve quantity
- `state.discoveries[]` contains only validated discovery events
- `state.citizen_knowledge[]` contains only knowledge that actually reached that citizen
- `state.experiment_results[]` contains persisted experiment history
- `state.learned_processes[]` contains learned repeatable procedures
- `state.locations[].known_facts` contains validated accumulated location facts

The UI may display absence as absence. It must not render placeholders that imply a hidden fact exists.

### Planner Boundary

Citizen planner context now receives:

- personally confirmed deposits
- personally validated material/world properties
- actual local observations/conversations
- legal experiment choices without hidden outcome hints

The planner is explicitly instructed not to infer a hidden property from experiment availability.

## Migration

Existing v0.5 saves migrate additively.

Pre-v0.6 discovered deposits are backfilled into:

- `discoveries`
- `citizen_knowledge`

No destructive reset is required.

## Validation

GitHub Actions run `36419824468` passed:

- Python compilation
- JavaScript syntax
- v0.4 regression smoke
- v0.5 Simulation smoke
- v0.5 Communication integrity smoke
- v0.5 UI integration smoke
- v0.6 Research/Discovery smoke

The release-only workflow trigger was restored afterward.

## Status

World & Simulation v0.6 core is ready for coordinator/cross-department review.

No `update.json` or release metadata was changed.


## v0.6 Session Close

World & Simulation work for this session is complete.

Authoritative handoff:
- branch: `simulation/v0.6-research-discovery`
- head: `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`
- base: shipped v0.5.0 commit `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- validation: GitHub Actions run `36419824468`

The final v0.6 Simulation contract has been delivered to:
- Communication & Perception
- Memory & Social
- Assets & Interface

No further Simulation implementation is pending in this work session. Resume only for coordinator merge conflicts, new inbox requests, or a later milestone.

No release metadata or `update.json` was changed.
