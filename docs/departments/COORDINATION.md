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

- [Coordinator / Integration] final v0.7 assembly waits for the two final passes above, then integrates Simulation + Communication + Memory + Assets and runs the full regression suite

### READY

- [Memory & Social] v0.7 runtime pass is unblocked but not yet implemented; next session creates `memory/v0.7-maintenance-history` from `release-v0.6.0`, ingests `maintenance_events.id`, adds bounded retrieval + smoke validation

- [World & Simulation] v0.7 Maintenance & Consequences core ready on `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`; runtime CI `36429729279` passed all v0.4-v0.7 smoke suites
- [World & Simulation] authoritative condition/effective-capability fields delivered to Assets
- [World & Simulation] stable `maintenance_events.id` physical anchors delivered to Memory
- [Communication & Perception] v0.7 talk reliability ready on `communication/v0.7-talk-reliability` @ `61eecc4c047dd3fd22b71612251769a8cb456737`; CI `36428495003` passed
- [Memory & Social] v0.6 per-citizen knowledge core remains available on `memory/v0.6-location-knowledge`
- [Assets & Interface] independent v0.7 Home scaling/search/Recent Activity/avatar framework is already prepared

### REVIEW

- [Assets & Interface] v0.7 complete on `assets/v0.7-home-avatars` @ `dad17d8ef663a4fef367c4260e58074047acf1b3`; PR #7 ready for integration with Home scaling/search/Recent Activity/avatar framework + authoritative maintenance UI + Assets smoke

- [Memory & Social] v0.7 maintenance policy/source contract reviewed; runtime branch still pending and must not be treated as integration-ready

- [World & Simulation] v0.7 gradual equipment/structure wear, battery health, chassis wear, service/repair/replacement jobs, condition-scaled capability, passive structure aging, additive migration, and stable maintenance events complete
- [Communication & Perception] v0.7 raw-exchange-first persistence, bounded retry, non-fatal claim enrichment, diagnostics, and failure classification complete

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
