# Agent City — Department Coordination Board

_Last updated: 2026-09-28_

This file is the shared project task board.

## Status Key

- **ACTIVE** — currently being worked
- **WAITING** — blocked on another department or coordinator integration
- **READY** — dependency or deliverable is ready for pickup
- **REVIEW** — department branch/work is complete enough for coordinator review
- **DONE** — finished and incorporated

## Current Board

### ACTIVE

_None._

### WAITING

_None._

### READY

- [World & Simulation] v0.6 Research/Discovery core ready on `simulation/v0.6-research-discovery` @ `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`; CI `36419824468` passed
- [Communication & Perception] v0.6 provenance/availability ready on `communication/v0.6-knowledge-provenance` @ `6a483fcc4d143606f3e401218002e06ae43076d1`; CI `36421263078` passed
- [Memory & Social] v0.6 per-citizen bounded knowledge core ready on `memory/v0.6-location-knowledge` @ `89c0a3e2d49c4c9236342c10559f92b93b1b7601`; CI `36419352645` passed
- [Assets & Interface] all upstream data/status contracts needed for the remaining UI pass are now available

### REVIEW

_None. v0.6.0 integration is complete._

### DONE

- [Coordinator] v0.6.0 assembled on `release-v0.6.0`, full smoke suite passed, versioned, and published from `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- [World & Simulation] v0.6 hidden truth, experiments, discoveries, per-citizen validated knowledge, safe state
- [Communication & Perception] v0.6 provenance receipts, grounded claims, anti-omniscience context, structured Visit availability
- [Memory & Social] v0.6 bounded per-citizen/location knowledge read model
- [Assets & Interface] v0.6 Home/Citizens/Locations/Records UI and safe knowledge presentation
- [Coordinator] v0.5.0 assembled on `release-v0.5.0`, full smoke suite passed, versioned, and published from `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- [World & Simulation] v0.5 Making & Building physical core + energy reserve + coordinate groundwork
- [Assets & Interface] v0.5 bounded Visit/History + Making state UI
- [Communication & Perception] v0.5 source-linked talk integrity
- [Memory & Social] v0.5 project/source continuity audit
- [Coordinator] v0.4.0 assembled/tested/published
- [Coordinator] v0.4.1 conversation hotfix tested/published
- [Memory & Social] durable directional conversation memory + bounded social context
- [Assets & Interface] Control Room redesign + distance-aware map readability
- [Communication & Perception] anti-omniscience architecture + provenance contract
- [Communication & Perception] same-location citizen talk
- [World & Simulation] visitor physical presence/travel
- [Assets & Interface] v0.3.0 live job progress/moving map markers
- [Memory & Social] persistent visitor visits/bounded conversation context

## v0.6 Coordination Goal

Primary rule:

> **The UI may show what the civilization knows, not everything the Simulation secretly knows.**

Integration dependency:

1. Simulation defines hidden world truth and validated discovery/experiment records. **READY**
2. Communication records how information actually reached specific citizens and separates verified observation from unverified claim. **READY**
3. Memory retains/retrieves bounded per-citizen knowledge without creating a global encyclopedia. **READY**
4. Assets renders Home/Citizens/Locations only from safe known-state interfaces. **ACTIVE**
5. Coordinator assembles all branches and runs regression + v0.6 smoke tests before publication.

## v0.6 Layered Knowledge Contract

Coordinator integration must preserve all layers rather than selecting one:

### Simulation

`agent_city/knowledge.py` owns:
- `world_properties` hidden truth
- `discoveries`
- `citizen_knowledge`
- `experiment_results`
- validated discovery possession/current verification state

### Communication

`agent_city/provenance.py` owns:
- `information_receipts`
- transfer/source/time/age history
- unverified face-to-face claims
- synchronization of only recipient-local **verified** Simulation knowledge
- experiment-result experience receipts
- structured Visit availability

### Memory

Owns:
- durable bounded retrieval/summaries
- consumer-facing per-citizen and per-location knowledge views
- no physical truth creation

### Assets

Consumes:
- Simulation safe public state for physical configuration/current validated world facts
- Memory bounded knowledge APIs for citizen/location notebooks
- Communication `status/availability` for Visit messaging

## Simulation v0.6 Contract Locks

1. `world_properties` remains hidden from ordinary `/api/state`
2. undiscovered deposits are absent from ordinary state
3. discovered deposits do not expose hidden reserve quantity
4. `discoveries.id` is the stable validated discovery anchor
5. direct discovery grants validated knowledge only to the discovering citizen
6. communicated claims do not automatically become verified Simulation knowledge
7. `experiment_results` persists `discovery | verified | inconclusive` outcomes
8. learned processes descend from validated discoveries and are not tech-tree nodes
9. missing knowledge renders as absence, not a hint that hidden content exists
10. no department publishes `update.json`

## Communication v0.6 Contract Locks

1. Simulation `agent_city/knowledge.py` and Communication `agent_city/provenance.py` are separate modules and both must survive merge
2. only verified recipient-local `citizen_knowledge` is mirrored into verified Communication receipts
3. `reported` knowledge is not silently upgraded to verified
4. face-to-face claims are tied to canonical stored conversation IDs and begin unverified
5. persisted claim text must occur verbatim in the attributed speaker's durable transcript
6. retelling does not verify a claim
7. remote visitor access must not leak local busy/talk details
8. merged planner/dialogue context should retain both Simulation-validated property knowledge and Communication provenance/claims

## Required Integration Tests

At minimum preserve and run:

- `tests/smoke_v040.py`
- `tests/smoke_v050.py`
- `tests/smoke_v050_communication.py`
- Simulation `tests/smoke_v060.py`
- Communication `tests/smoke_v060_communication.py`
- Memory v0.6 smoke
- Assets v0.6 UI/integration smoke when its branch is complete

## Handoff Protocol

When Department A needs Department B:

1. Department A writes a concise request to Department B's `INBOX.md`.
2. Department A records itself as **WAITING** here if the dependency blocks progress.
3. Department B reads its INBOX at the beginning of its next work session.
4. Department B completes the work or records why it cannot.
5. Department B writes the result to its own `OUTBOX.md` and, when useful, directly to Department A's `INBOX.md`.
6. The main coordinator reviews the handoff and updates this board.

## Coordinator Rule

Departments own systems, not reality.

Cross-department integration must preserve:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

A green department branch is not sufficient if merging it would silently remove another department's invariant.


## Memory v0.6 Final Handoff

Memory's final upstream contracts are resolved.

Coordinator should integrate:
- Simulation `agent_city/knowledge.py`
- Communication `agent_city/provenance.py`
- Memory `agent_city/memory.py` bounded knowledge extensions
- Memory Citizen/Location knowledge APIs
- Memory `tests/smoke_v060_memory.py`

Do not substitute any one layer for another during conflict resolution.


## v0.6 Integration Result

Published runtime:
`6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

Preserved layers:
1. Simulation hidden truth + validated discovery/experiment state
2. Communication immutable provenance + unverified transferred claims
3. Memory bounded per-citizen/location knowledge retrieval
4. Assets consumes safe known-state interfaces rather than hidden truth

Final CI passed:
- Python compile
- JavaScript syntax
- v0.4 regression smoke
- all v0.5 smoke suites
- v0.6 Simulation smoke
- v0.6 Communication provenance smoke
- v0.6 Memory knowledge smoke
- v0.6 assembled UI/integration smoke
