# World & Simulation — State

_Last updated: 2026-09-28_
_Current shipped release: v0.5.0_
_Active implementation branch: `simulation/v0.5-making-building`_
_Branch head: `773299189d22d214b3376c72b396015a4a7a762e`_

## Mission

Own physical truth.

The LLM may choose intent, but every physical action must be legal, validated, timed, and persisted by the simulation.

## Core Rule

> **The AI may decide intent. The simulation decides reality.**

## v0.5 Making & Building — Implemented on Department Branch

The Simulation branch now contains a tested physical core for v0.5.0. It is not yet the shipped release until the coordinator integrates it.

### Fabrication

Implemented real fabrication jobs with:

- validated settlement material requirements
- real job duration and energy cost
- material consumption before the job proceeds
- persisted `equipment` records only after successful job completion
- stable equipment IDs
- explicit physical modifiers instead of abstract level bonuses

Current starting workbench processes are intentionally small, not a technology tree:

- Field Cargo Pack
  - raises physical carrying capacity
  - requires real fabricated equipment
- Powered Extraction Tool
  - reduces extraction job duration through an explicit speed multiplier

A citizen is not repeatedly offered another copy of the same still-functional personal equipment template.

### Construction / Projects

Implemented persisted multi-step projects:

`planned -> reserved -> underway -> complete`

Physical tables:

- `projects`
- `project_materials`

A construction project has:

- stable project ID
- blueprint/type
- name
- validated location
- local x/y coordinates
- creating citizen
- lifecycle timestamps
- active construction job ID
- resulting structure ID after completion

Reservation deducts validated settlement materials and records the reserved amounts. Construction creates a real `structures` row only when the timed construction job completes.

Current v0.5 construction is intentionally settlement-local at Seed Site. Remote construction waits for explicit physical project-material transport rather than teleporting reserved stock.

### Structures / Coordinate Groundwork

Structures now support:

- stable ID
- kind
- `location_id`
- local `x_km` / `y_km`
- condition
- `provides_charging`
- source `project_id`

Starter landmarks also receive simple local coordinates. This is groundwork for later continuous/spherical geography; v0.5 does not implement free-roam globe movement.

### Energy-Safe Field Work

Implemented return-energy reserve validation.

Before outbound travel or remote survey/extraction, Simulation checks whether the citizen can still reach a known operational charger with a modest safety margin.

Rules:

- unsafe outbound travel is not offered
- unsafe remote survey/extraction is not offered
- start-time validation repeats the safety check
- returning to a charger remains legal when physically reachable
- future structures with `provides_charging = 1` automatically become valid recharge destinations in the route-distance calculation
- charging itself is available at any location containing an operational charging structure

Returning cargo remains a citizen choice. It is not hard-coded as an automatic action.

### Stable Physical Event References

Completed jobs remain durable authoritative physical-event records.

Relevant fields:

- `jobs.id` — stable physical event/job ID
- `citizen_id`
- `action`
- `target`
- `start_minute`
- `end_minute`
- `status`
- `outcome`
- `project_id` when applicable

New outcomes use values such as `success`, `failed`, or `no_yield`. Pre-v0.5 completed jobs are migrated to `legacy_complete` instead of being assigned invented richer semantics.

### Conversation Integrity Preserved

Communication's v0.5 physical-talk invariant is integrated into this branch.

- `citizen_conversations.source_job_id` links a stored exchange to its physical talk job
- a talk job completes successfully only if that durable exchange exists
- missing exchange => talk job `failed`
- Simulation never fabricates a synthetic conversation to make the job succeed
- both citizens are released from the physical talk job either way

## Current Time Model

Target chronology:

**1 real hour = 4 simulated hours**

Time stops while the app is closed. Pause freezes simulation time.

## Existing Physical Actions Preserved

- travel
- survey
- extract
- deposit cargo
- charge
- wait / observe
- face-to-face citizen talk

The v0.5 branch adds:

- fabricate
- plan project
- reserve project materials
- construct

## Existing World State Preserved

Citizens still track:

- location
- energy
- integrity
- active job
- carried materials

World still tracks:

- locations
- routes
- deposits
- survey state
- structures
- settlement stores

New v0.5 snapshot collections exposed through existing `/api/state`:

- `equipment`
- `projects`
- `project_materials`

Structures and locations expose the added physical fields directly in their existing collections.

## Validation

GitHub Actions run `36372991331` passed on the integrated branch:

- Python compilation
- JavaScript syntax check
- existing v0.4 regression smoke
- v0.5 Making & Building smoke
- v0.5 Communication talk-integrity smoke

The normal release-only workflow trigger was restored afterward.

## Integration Status

Ready for coordinator integration. No `update.json` or release metadata was published or changed.


## Work Session Handoff

This Simulation work session is complete.

Handoff source of truth:
- branch: `simulation/v0.5-making-building`
- head: `773299189d22d214b3376c72b396015a4a7a762e`
- integrated validation: GitHub Actions run `36372991331`
- coordinator state: Simulation is ready for review/integration
- next active dependency: Assets & Interface consumes the authoritative Making & Building state and finishes the v0.5 visual layer

No release metadata or `update.json` was changed.


## Shipped v0.5.0 Integration

Coordinator integrated this physical core with the completed Assets v0.5 UI on `release-v0.5.0`.

Immutable published runtime commit:
`d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`

The assembled release passed:
- Python compilation
- JavaScript syntax
- v0.4 regression smoke
- v0.5 Simulation smoke
- v0.5 Communication integrity smoke
- v0.5 assembled UI integration smoke
