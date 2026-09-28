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

_None._

### REVIEW

_None._

### DONE

- [Coordinator] v0.7.0 assembled on `release-v0.7.0`, full v0.4-v0.7 smoke suite passed in Actions run `36436548845`, versioned, and published from immutable runtime commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- [World & Simulation] v0.7 maintenance/consequences core integrated
- [Communication & Perception] v0.7 talk reliability/diagnostics integrated
- [Memory & Social] v0.7 bounded maintenance history integrated
- [Assets & Interface] v0.7 Home scaling/search/Recent Activity/avatar/maintenance UI integrated
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

## v0.7 Coordination Goal

v0.7.0 is **Maintenance, Consequences & Home Polish**.

Primary goals:

1. mechanical life gains gradual physical wear/repair consequences without repetitive chore spam
2. Home scales cleanly for longer conversations and future population growth
3. lightweight 2D/static avatar identity begins without a 3D dependency
4. autonomous talk failures become substantially more reliable without fabricated dialogue

## Simulation v0.7 Contract Locks

Coordinator integration must preserve:

1. `battery_health` is long-term capacity and remains distinct from current `energy`
2. real use gradually wears relevant equipment and citizen chassis/battery state
3. structure aging advances only with simulation time, never while the app is closed
4. equipment capability uses Simulation's authoritative effective modifiers
5. equipment/structures at condition <= 20 are visible but non-operational
6. service/repair consumes real materials and simulation time
7. remote service does not consume Seed Site materials until remote logistics exists
8. future chargers remain capability-based via `provides_charging`, not hard-coded by starter name
9. `maintenance_events.id` is the stable meaningful maintenance event anchor
10. routine microscopic wear does not generate one durable memory-grade event per tick/job
11. all v0.6 knowledge/provenance boundaries remain intact
12. no department publishes `update.json`

## Assets v0.7 Consumption Contract

Assets should consume directly:

**Citizen**
- battery_health / battery_state
- usable_energy_capacity
- battery_replacement_due
- joint_wear
- chassis_service_state / chassis_service_due

**Equipment**
- condition / condition_state / operational / service_due
- effective_cargo_bonus
- effective_extraction_speed_multiplier
- last_service_minute / use_count

**Structures**
- condition / condition_state / operational / service_due
- efficiency_multiplier
- last_service_minute / use_count

Do not rederive thresholds or current capability from pristine raw modifier fields.

## Memory v0.7 Event Contract

Meaningful completed maintenance uses:

- `maintenance_events.id`
- `job_id`
- citizen actor
- target type/id
- before/after value
- consumed materials
- outcome
- sim minute
- summary

Memory should avoid turning every tiny wear decrement into durable narrative memory.

## Communication v0.7 Contract Locks

Coordinator integration must preserve:

1. raw exchange generation/persistence happens before claim/provenance enrichment
2. claim extraction failure does not invalidate an existing durable conversation
3. there is still no fabricated fallback dialogue
4. raw dialogue may retry once, but success still requires real model-generated content
5. `talk_diagnostics` is debug metadata, not citizen knowledge or physical truth
6. a talk physically succeeds only when its `source_job_id` has a durable `citizen_conversations` row
7. failed talk chronology remains distinct from conversation transcript/history
8. diagnostic History rows use `category = "diagnostic"` and should not be rendered as citizen speech

## Required Integration Tests

At minimum preserve and run:

- `tests/smoke_v040.py`
- all v0.5 smoke suites
- all v0.6 Simulation/Communication/Memory/UI smoke suites
- `tests/smoke_v070.py`
- `tests/smoke_v070_communication.py`
- Memory v0.7 maintenance smoke if a runtime branch is added
- Assets v0.7 UI/integration smoke after its final pass

Assembled release validation: `36436548845` passed the complete required v0.4-v0.7 chain.

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


## Memory v0.7 Integration Locks

Coordinator integration must preserve:

1. `maintenance_events.id` as the canonical physical maintenance source.
2. Actor receives direct maintenance memory; a different citizen target also receives serviced-subject memory.
3. Equipment owners, bystanders, and the settlement do not automatically receive maintenance memory.
4. Passive wear and condition deltas do not create durable Memory events.
5. `simulation_maintenance_event` records stay out of generic v0.6 knowledge-fact retrieval.
6. Maintenance model context remains bounded.
7. `GET /api/memory/maintenance/{citizen_id}` is citizen-scoped history, not physical admin truth.
8. Memory synchronization safely no-ops before Simulation's maintenance table exists, preserving merge compatibility.
9. Preserve `tests/smoke_v070_memory.py` in the assembled v0.7 suite.
