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


### WAITING

- [Coordinator / Stage 1 Review] review Simulation + Communication + Memory + Assets Stage 1 contracts before authorizing Stage 2 Living World integration

### READY

- [Memory & Social] Stage 1 safe spatial-observation consumer contract ready: observation ID = evidence, deposit ID = stable subject, radius = precision; hidden seed/geometry excluded

- [Communication & Perception] v0.8 Stage 1 grounding ready on `communication/v0.8-grounding-stage1` @ `a95e7af23eddaeb018bd6b2b6f19681a227e92af`; CI `36450386273` passed the full v0.4-v0.7 regression chain + Communication Stage 1 smoke

- [World & Simulation] v0.8 Stage 1 seeded spatial foundation ready on `simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`; runtime CI `36449582788` passed complete v0.4-v0.7 regression chain + Stage 1 smoke
- [Memory & Social] Simulation's stable spatial observation/deposit/coordinate-precision contract is now available; Stage 1 audit may finalize without hidden-world access
- [Communication & Perception] Simulation coordinate/observation contract and future shared-action boundary are now available
- [Assets & Interface] Simulation safe spatial read model is now available; Assets Stage 1 branch is already ready for review
- [Assets & Interface] v0.8 Stage 1 complete on `assets/v0.8-visual-stage1` @ `af2e058780103755360d143ca964855145e2254a`; PR #11 ready

### REVIEW

- [Communication & Perception] grounded visitor RP, evidence-status language, authoritative capability surface, safe spatial context, remote-store privacy fix, and future shared-action boundary complete

- [World & Simulation] persistent planet seed, meter-scale tangent-plane coordinates, deterministic hidden terrain/geology, stable spatial deposit bodies, additive legacy migration, validated spatial observations, and safe read contract complete
- [Assets & Interface] citizen visual profiles, restored job progress, Enter-to-send, Asset Worker/render-tier contracts, and v0.8 Assets smoke complete
- [Memory & Social] Stage 1 spatial-memory audit ready; Simulation subject/observation contract is now supplied

### DONE

- [Coordinator] v0.7.0 assembled on `release-v0.7.0`, full v0.4-v0.7 smoke suite passed in Actions run `36436548845`, versioned, and published from immutable runtime commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- [World & Simulation] v0.7 maintenance/consequences core integrated
- [Communication & Perception] v0.7 talk reliability/diagnostics integrated
- [Memory & Social] v0.7 bounded maintenance history integrated
- [Assets & Interface] v0.7 Home scaling/search/Recent Activity/avatar/maintenance UI integrated
- [Coordinator] v0.6.0 assembled and published
- [Coordinator] v0.5.0 assembled and published

## v0.8 Stage 1 Coordination Goal

Stage 1 establishes contracts and substrate before the larger Living World integration.

Order of authority:

1. Simulation defines seeded coordinate/world truth and stable physical subjects. **REVIEW**
2. Communication grounds what citizens/visitors may claim and defines conversational/shared-action boundaries. **REVIEW**
3. Memory retains only observations/claims that reached a citizen through valid sources. **CONTRACT READY**
4. Assets renders only validated state and prepares asynchronous visual-generation infrastructure. **REVIEW**
5. Coordinator reviews Stage 1 interfaces before Stage 2.

The planned v0.7.1 progress/chat/RP polish is folded into v0.8.0.

Stage 1 is intentionally not the full v0.8 release.

## Simulation v0.8 Stage 1 Contract Locks

Coordinator and downstream departments must preserve:

1. `meta.planet_seed` is persistent hidden physical truth and never ordinary UI/LLM/Memory state
2. local frame `seed_site_local` uses meters, +x east, +y north, origin Seed Site
3. current local frame is a tangent plane compatible with later global lat/lon, not lat/lon itself
4. existing named locations/routes/deposits retain identity and are additively spatially anchored
5. hidden spatial queries are deterministic from seed + coordinate/chunk
6. nearby points vary coherently; scans are not independent random rolls
7. generated deposit bodies have stable IDs and physical extent
8. procedural deposit IDs are independent of discoverer/time
9. raw `generated_deposits`, hidden geometry, hidden richness, and raw query payloads remain hidden
10. `spatial_observations.id` is the stable validated spatial observation anchor
11. observation source-job ownership/range/travel legality remains Simulation-controlled
12. coordinate decimals do not imply sensor precision; `radius_m` + source action/tool define epistemic precision
13. existing route travel remains discrete in Stage 1: origin coordinate while traveling, destination coordinate on arrival
14. Stage 1 adds no scanner, free-roam move action, globe renderer, new communication technology, or arbitrary citizen technology
15. no department publishes `update.json`

## Safe Spatial Consumption Contract

### Assets

May consume:
- `state.spatial_frame`
- locations `x_m/y_m`
- citizens `position_x_m/position_y_m`
- structures/projects `x_m/y_m`
- visitor presence `x_m/y_m`
- `state.spatial_observations[]`

Must not infer continuous travel paths yet.

### Memory

May source:
- `simulation_spatial_observation`
- source ID = `spatial_observations.id`
- optional stable deposit subject `dep_*` or `gdep_*`

Must preserve `radius_m` and provenance and must never ingest hidden generated-body tables/seed.

### Communication

Visitor/citizen claims about unvalidated spatial facts remain claims.

Future shared physical activity must be a Simulation-owned action. Chat agreement alone does not move participants or produce observations.

## Required Stage 1 Integration Tests

At minimum preserve and run:

- all shipped v0.4-v0.7 regression suites
- `tests/smoke_v080_stage1.py`
- Communication Stage 1 smoke when complete
- Memory Stage 1 smoke if runtime ingestion is added
- Assets Stage 1 smoke

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

## Communication v0.8 Stage 1 Contract Locks

Coordinator integration must preserve:

1. visitor-described physical details remain attributed reports until validated
2. dialogue distinguishes known fact, current observation, reported claim, hypothesis/proposal, and validated capability/action
3. concept art/visual assets never create physical equipment or capability
4. capability language derives from operational runtime equipment/structures, learned processes, and legal Simulation actions
5. legal action availability means attemptability, not guaranteed result
6. remote citizens do not receive exact live Seed Site storage quantities
7. Communication consumes safe meter positions and validated `spatial_observations`, never raw hidden spatial queries
8. coordinate decimal precision does not imply sensor/epistemic precision
9. Stage 1 chat agreement never changes coordinates, creates jobs, or creates observations
10. real visitor-linked shared activity remains Simulation-owned Stage 2 work
11. preserve v0.7 raw-exchange-first talk reliability and all v0.6 provenance/anti-omniscience rules
12. preserve `tests/smoke_v080_communication.py` in Stage 1 integration testing

Stage 2 dependency is recorded in World & Simulation INBOX and does not block Stage 1 review.


## Memory v0.8 Stage 1 Integration Locks

1. Memory reads `spatial_observations`, never `planet_seed` or hidden `generated_deposits` geometry/richness.
2. `spatial_observations.id` is evidence identity; `deposit_id` is stable physical subject identity.
3. Same-body repeat encounters keep the same subject and are not automatically separate durable memories.
4. First encounters, new methods, materially improved precision, and explicit milestones may be retained.
5. Routine meter movement / passive scans without new information are suppressed.
6. Stored coordinate precision must never exceed observation `radius_m`.
7. Spatial memories remain per-citizen and do not create a global map memory.
8. `simulation_spatial_observation` stays separate from generic knowledge-fact retrieval.
9. Preserve `tests/smoke_v080_memory.py` during Stage 1 coordinator integration.
