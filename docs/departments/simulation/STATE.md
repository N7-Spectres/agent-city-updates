# World & Simulation — State

_Last updated: 2026-09-28_
_Current shipped release: v0.6.0_
_Active implementation branch: `simulation/v0.7-maintenance`_
_Branch head: `54f5d838f674d0b278a51382f3a880cc0738b417`_

## Mission

Own physical truth.

> **The AI may decide intent. The simulation decides reality.**

## Shipped Foundation Preserved

The v0.7 branch starts from immutable shipped v0.6.0 commit:

`6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

All v0.5/v0.6 physical-production, energy-return, hidden-truth, discovery, provenance-layer compatibility, and knowledge-boundary rules remain intact.

## v0.7 Maintenance & Consequences — Implemented

### Citizen Mechanical State

Citizens now persist:

- `battery_health` — long-term pack health, distinct from current `energy`
- existing `joint_wear` now accumulates from real work
- `last_service_minute`

Safe snapshot adds:

- `battery_state`
- `usable_energy_capacity`
- `battery_replacement_due`
- `chassis_service_state`
- `chassis_service_due`

Battery health physically caps usable charge. A citizen with 70% battery health cannot recharge above 70% until the pack is replaced.

Real completed work applies small battery-health and joint-wear increments. Wear is gradual and threshold history is sparse.

### Equipment Wear

Equipment now persists:

- `condition`
- `last_service_minute`
- `use_count`

Real use degrades relevant equipment:

- extraction work wears extraction equipment
- loaded travel wears cargo equipment

Condition affects capability continuously:

- cargo bonus scales with condition
- extraction speed bonus scales with condition
- condition <= 20 makes equipment non-operational

A critical tool remains visible in state so it can be repaired.

Snapshot exposes:

- `condition_state`
- `operational`
- `service_due`
- `effective_cargo_bonus`
- `effective_extraction_speed_multiplier`

UI/other departments should use the effective fields, not recompute condition math from the raw base modifiers.

### Structure Wear

Structures now persist:

- `condition`
- `last_service_minute`
- `use_count`

Wear comes from:

- gradual simulated-time aging while the world clock runs
- actual structure use

Examples:

- workbench wear from fabrication/experiments
- charger wear from charging
- storage wear from cargo deposit

Time stops while Agent City is closed, so passive wear also stops.

Snapshot exposes:

- `condition_state`
- `operational`
- `service_due`
- `efficiency_multiplier`

Badly degraded structures have physical consequences:

- condition <= 20 => non-operational
- degraded workbench => longer fabrication/experiment jobs
- degraded charger => longer charging jobs
- non-operational storage => cargo deposit cannot complete

Charging capability remains generic through `provides_charging = 1`; citizen-built future chargers are supported without relying on the literal starter name.

### Maintenance Actions

New autonomous legal actions:

- `service_chassis`
- `replace_battery`
- `service_equipment`
- `service_structure`

Actions appear only after meaningful thresholds:

- equipment/structure service due below 90 condition
- battery replacement due below 85 health
- chassis service due at joint wear >= 12

Routine maintenance therefore remains occasional rather than constant.

Service consumes real materials before start, takes real simulation time, and restores validated physical state.

Examples of service inputs include:

- Lubricant
- Fasteners
- Mechanical components
- Processed structural material
- Battery cells

More severe degradation requires more replacement material.

Current structure/equipment service uses Seed Site stored materials. Remote maintenance waits for physical remote material logistics rather than teleporting settlement stock.

### Stable Maintenance Events

New durable table:

- `maintenance_events`

Fields:

- `id` — stable maintenance event ID
- `job_id` — physical action/job anchor
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

Jobs additionally expose:

- `maintenance_event_id`

Successful service/repair/replacement creates one maintenance event.

Routine per-use wear does **not** create a separate Memory-grade event every time. Condition state itself is authoritative, and History only notes meaningful degradation threshold crossings.

### Event Types

Current maintenance event types:

- `chassis_service`
- `battery_replacement`
- `equipment_service`
- `structure_service`

### Migration

v0.6 saves migrate additively.

New citizen/equipment/structure/job fields and `maintenance_events` are added without reset.

The maintenance wear clock initializes from the current simulation minute, preventing old saves from receiving retroactive wear for time that was never simulated under v0.7.

### Planner Context

Autonomous citizens now receive their own:

- current charge
- battery health
- integrity
- joint wear

Maintenance choices appear in the same legal-action list as other physical work. The LLM chooses intent; Simulation validates material/time/condition rules.

## Validation

Final runtime hardening was validated in GitHub Actions run:

`36429729279`

Passed:

- Python compilation
- JavaScript syntax
- v0.4 regression smoke
- all v0.5 smoke suites
- all v0.6 Simulation/Communication/Memory/UI smoke suites
- v0.7 maintenance smoke

The only subsequent branch commit restored the normal release-only workflow; runtime code is unchanged.

## Status

World & Simulation v0.7 maintenance core is ready for coordinator/cross-department review.

No `update.json` or release metadata was changed.
