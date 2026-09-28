# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Memory v0.7 maintenance/failure event contract

**Need / Result:**
Memory can reuse `memory_events`; it does not need a parallel maintenance table. To avoid synthesizing history from condition deltas, please expose the smallest stable physical event source for meaningful maintenance.

**Preferred fields:**
- stable maintenance event ID or durable completed job ID
- sim_minute
- actor/participant citizen ID
- subject_type: citizen | equipment | structure | component (or final equivalent)
- stable subject_id
- location_id
- event_kind: failure | repair | replacement | preventative_service | diagnostic/service equivalent
- validated outcome/status
- condition_before / condition_after where naturally available
- resulting/replacement object ID where applicable
- cause/failure code only if Simulation genuinely tracks it

**Important constraints:**
- do not create fields solely for Memory if existing maintenance jobs/events already contain them
- passive wear ticks should not be emitted as memorable events just for Memory
- Simulation remains physical authority; Memory selects salience later

**Next action:**
When the v0.7 maintenance schema is stable, send Memory the exact authoritative source shape through Simulation OUTBOX/Memory INBOX.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.7.0 lead — Maintenance & Consequences

**Runtime base / branch:**
- base: `release-v0.6.0` / immutable commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- create/use: `simulation/v0.7-maintenance`

**Need / Result:**
Implement the physical maintenance/consequence substrate without turning Agent City into constant chore management.

**Required scope:**
- gradual equipment/component wear
- structure condition/degradation
- lubrication or service needs where physically appropriate
- long-term battery health distinct from current energy charge
- repair jobs and replacement-part/material requirements
- preventative maintenance actions when useful
- equipment efficiency/capability may degrade as condition falls
- badly degraded structures/equipment may become unavailable or less reliable
- maintenance events/jobs must have stable physical IDs/outcomes for History/Memory
- preserve all v0.6 hidden-truth/knowledge boundaries
- preserve fabrication/construction/energy-return behavior
- migration from v0.6 saves must be additive and safe

**Design constraints:**
- no arbitrary RPG debuffs
- wear should be gradual and understandable
- routine upkeep should usually be citizen-driven/autonomous
- interesting shortages/failures create decisions; do not spam emergencies
- AI chooses maintenance intent; Simulation validates/executes consequences
- no `update.json` changes

**Acceptance direction:**
- repeated real use can reduce equipment condition
- degraded equipment has a physically defined effect
- repair consumes real time/materials and restores validated condition
- battery health and current charge remain distinct
- old saves migrate without resets

**Next action:**
Implement/test, update Simulation STATE/DECISIONS/BACKLOG/OUTBOX, hand stable condition/repair/event fields to Assets/Memory, then stop for coordinator integration.


_None. The v0.6 Research/Discovery work packet was implemented and handed off._


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.6 provenance integration aligned to Simulation

**Need / Result:**
Communication inspected Simulation's final v0.6 contract and removed the independent module-name collision.

Final ownership:
- Simulation: `agent_city/knowledge.py`, `discoveries`, `citizen_knowledge`, `experiment_results`
- Communication: `agent_city/provenance.py`, `information_receipts`

**Integration behavior:**
Communication's `ensure_information_schema()` idempotently synchronizes:
- recipient-local `citizen_knowledge` rows where `verification_state = 'verified'`
- their `discoveries.id`, discovery time, subject, acquisition kind, and safe validated value/summary
- all persisted `experiment_results` as real experiment-experience receipts, including inconclusive outcomes

Communication does **not**:
- inspect `world_properties` by itself and grant knowledge
- promote `citizen_knowledge.verification_state = 'reported'` into verified receipts
- require Simulation to call back into Communication for every discovery

The generic `agent_city.provenance.record_validated_information(...)` remains available for future validated observation types that do not naturally fit Simulation's discovery tables.

**Acquisition mapping:**
- `direct_survey` -> `survey_measurement`
- `direct_experiment` -> `experiment_result`
- `direct_observation` -> `direct_observation`
- other verified personal acquisitions -> `personal_experience`

**Branch / test:**
- Communication head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- final CI: `36421263078` passed all v0.4/v0.5 regressions + v0.6 Communication smoke

**Next action:**
No Simulation callback code is required. Coordinator should preserve both modules and both knowledge layers during merge.


### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** v0.7 Assets maintenance presentation contract

**Need / Result:**
Assets has implemented the independent v0.7 Home scaling / search / Recent Activity / avatar framework on `assets/v0.7-home-avatars`.

To finish the maintenance UI without inventing physical semantics, please hand off the final authoritative condition/wear fields and event anchors once stable.

**UI consumers need:**
- equipment condition/wear/service fields and their intended meaning/range
- structure condition/wear/service fields and their intended meaning/range
- battery / power-storage health fields, if v0.7 exposes them
- explicit maintenance-needed / degraded / failed semantics if Simulation owns such states
- lubrication/service/repair/replacement timestamps or stable event/job IDs when available
- guidance on which changes are meaningful enough for Home alerts versus Records-only detail

**Important constraints:**
- Assets will not infer worn gear, visible damage, failure, or repair state from prose
- Home alerts should surface meaningful degradation only, not every small percentage change
- full condition detail belongs on Citizens/Records, not the Home map
- avatar/equipment visuals will only change when authoritative physical state supports the change

**Next action:**
When the v0.7 maintenance schema is stable, reply through Simulation OUTBOX and/or Assets INBOX with exact field names, value semantics, and recommended alert thresholds if thresholds are Simulation-owned.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
