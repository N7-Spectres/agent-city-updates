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

- [Communication & Perception] v0.6.0: discovery/claim provenance, local information flow, anti-omniscience audits, visitor busy/talk status fix
- [Assets & Interface] v0.6.0: finish data-driven Home/Citizens/Locations using safe Simulation/Memory/Communication contracts

### WAITING

- [Assets & Interface] Simulation safe known-state contract is now ready; final UI semantics still depend on Communication's provenance/status shape and Memory's bounded consumer read model
- [Memory & Social] Simulation discovery/result IDs are now stable; any richer ingestion that depends on transferred claims still waits on Communication's final provenance shape
- [Coordinator / Integration] final v0.6 assembly waits for Communication + Assets completion

### READY

- [World & Simulation] v0.6 Research/Discovery core ready on `simulation/v0.6-research-discovery` @ `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`
- [World & Simulation] CI run `36419824468` passed Python compile, JS syntax, all v0.4/v0.5 regressions, and `tests/smoke_v060.py`
- [World & Simulation] stable discovery/knowledge/result/read-model contracts delivered to Communication, Memory, and Assets
- [Memory & Social] v0.6 per-citizen knowledge core on `memory/v0.6-location-knowledge` @ `89c0a3e2d49c4c9236342c10559f92b93b1b7601`; CI run `36419352645` passed
- [Communication & Perception] deeper claim-level `PROVENANCE_CONTRACT.md` remains available as design reference

### REVIEW

- [World & Simulation] hidden world truth, experiments, persistent discoveries, citizen-local knowledge, learned verification processes, safe public state, and migration are complete for v0.6
- [Memory & Social] v0.6 per-citizen knowledge core ready; final transferred-claim integration may consume Communication provenance after it stabilizes

### DONE

- [Coordinator] v0.5.0 assembled on `release-v0.5.0`, full smoke suite passed, versioned, and published from `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- [World & Simulation] v0.5 Making & Building physical core + energy reserve + coordinate groundwork
- [Assets & Interface] v0.5 bounded Visit/History + Making state UI
- [Communication & Perception] v0.5 source-linked talk integrity
- [Memory & Social] v0.5 project/source continuity audit, no schema change required
- [Coordinator] v0.4.0 assembled on `release-v0.4.0`, tested, versioned, and published
- [Coordinator] v0.4.1 blank-reply conversation hotfix tested and published
- [Memory & Social] Durable directional conversation memory + bounded social context
- [Assets & Interface] Control Room redesign + distance-aware map readability pass
- [Communication & Perception] Information-boundary rules / anti-omniscience architecture preserved; provenance contract documented
- [Communication & Perception] Same-location citizen talk system
- [World & Simulation] Visitor physical presence and travel
- [Assets & Interface] v0.3.0 live job progress and moving map markers
- [Memory & Social] Persistent visitor visits and bounded conversation context

## v0.6 Coordination Goal

Primary rule:

> **The UI may show what the civilization knows, not everything the Simulation secretly knows.**

Integration dependency:

1. Simulation defines hidden world truth + validated discovery/experiment records. **READY**
2. Communication defines how discoveries/claims move between citizens and fixes visit-status wording. **ACTIVE**
3. Memory retains/retrieves per-citizen knowledge without creating a global encyclopedia. **CORE READY; transfer provenance pending**
4. Assets renders Home/Citizens/Locations only from safe known-state interfaces. **ACTIVE**
5. Coordinator assembles all branches and runs regression + v0.6 smoke tests before publication.

## Simulation v0.6 Contract Locks

Coordinator integration must preserve:

1. `world_properties` remains hidden from ordinary `/api/state`
2. undiscovered deposits are absent from ordinary state
3. discovered deposits do not expose hidden reserve quantity
4. `discoveries.id` is the stable validated discovery anchor
5. direct discovery grants knowledge only to the discovering citizen
6. communicated claims do not become verified Simulation knowledge automatically
7. `experiment_results` persists `discovery | verified | inconclusive` outcomes
8. learned processes descend from validated discoveries and are not tech-tree nodes
9. missing knowledge renders as absence, not a UI hint that hidden content exists
10. no `update.json` publication by departments

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
