# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.7 Maintenance & Consequences core ready

**Need / Result:**
Implemented on `simulation/v0.7-maintenance`.

Branch head:
`54f5d838f674d0b278a51382f3a880cc0738b417`

Runtime validation:
GitHub Actions `36429729279` passed all v0.4-v0.6 regressions plus `tests/smoke_v070.py`. The only commit after that run restored the release-only workflow.

Delivered:
- equipment use wear + condition-scaled physical effects
- structure passive/use wear
- non-operational critical condition
- long-term battery health distinct from current charge
- chassis joint wear
- material/time-consuming service and replacement jobs
- preventative maintenance thresholds
- stable `maintenance_events.id`
- UI-ready authoritative condition/status/effective fields
- additive v0.6 migration

**Important constraints:**
- no chore-spam wear events
- repair materials remain physical
- remote maintenance does not teleport Seed Site stores
- all v0.6 knowledge/provenance boundaries remain intact
- no release metadata changed

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Assets v0.7 maintenance/condition state contract

**Citizen fields in `state.citizens[]`:**
- `battery_health`
- `battery_state`
- `usable_energy_capacity`
- `battery_replacement_due`
- `joint_wear`
- `chassis_service_state`
- `chassis_service_due`
- `last_service_minute`
- existing authoritative `cargo_capacity` remains added by `/api/state`

**Equipment fields in `state.equipment[]`:**
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `last_service_minute`
- `use_count`
- raw design fields `cargo_bonus`, `extraction_speed_multiplier`
- authoritative effective fields:
  - `effective_cargo_bonus`
  - `effective_extraction_speed_multiplier`

Use the **effective** fields for displayed current capability. Raw fields describe the pristine design.

**Structure fields in `state.structures[]`:**
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `efficiency_multiplier`
- `last_service_minute`
- `use_count`
- existing `provides_charging`

**Maintenance history:**
`state.maintenance_events[]`
- `id`
- `job_id`
- `citizen_id`
- `event_type`
- `target_type`
- `target_id`
- `before_value`
- `after_value`
- `materials_json`
- `outcome`
- `sim_minute`
- `summary`

**UI constraint:**
Display these authoritative states directly. Do not rederive service thresholds/condition effectiveness in the frontend.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Memory v0.7 validated maintenance event anchors

For durable maintenance/repair memory, use:

- source type recommendation: `simulation_maintenance_event`
- source ID: `maintenance_events.id`
- physical job anchor: `maintenance_events.job_id`
- actor: `citizen_id`
- target: `target_type / target_id`
- event type
- before/after physical value
- consumed materials JSON
- outcome
- simulation minute
- summary

Current event types:
- `chassis_service`
- `battery_replacement`
- `equipment_service`
- `structure_service`

Routine wear increments intentionally have no separate maintenance-event row. Memory should prefer meaningful completed service, critical failures/shortages, and major threshold events over microscopic wear changes.

## Outbox Rule

Keep durable rules in STATE/DECISIONS/BACKLOG. Keep this file focused on current handoffs.
