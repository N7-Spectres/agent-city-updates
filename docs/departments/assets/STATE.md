# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.6.0_
_Current department branch: `assets/v0.7-home-avatars`_
_Current branch head: `e0daf26a4249584d1560c7aea06b29cd1b5818fb`_
_Current review surface: draft PR #7_

## Mission

Make Agent City visually understandable and alive while never allowing presentation to invent physical state, hidden knowledge, wear, damage, equipment, or outcomes.

## v0.7 Independent Assets Work — Implemented

Branch base:
`release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

### Home scaling

Desktop Home now uses one shared height budget for:

- citizen rail
- center world panel
- Visit/chat rail

Citizen rail:
- internal scrolling
- citizen name search/filter
- future-population-ready layout

Visit rail:
- full-height desktop panel
- internal chat scrolling
- anchored visitor input/actions

Smaller screens keep the existing stacked/responsive behavior.

### Recent Activity

Home now includes a compact five-item Recent Activity surface beside the focused-location card.

It combines:

- meaningful chronology events
- concise summaries from real stored `citizen_conversations`

Rules:

- successful conversation begin/completion chronology is filtered when the stored exchange summary exists
- failed talk attempts remain ordinary events
- routine observe/wait churn is filtered from the Home summary
- "View all history" opens Records → History

No conversation summary is synthesized from a failed or missing exchange.

### Avatar first stage

Added lightweight 2D/static identity infrastructure without Mixamo or 3D.

Supported surfaces:

- Citizens page full-body identity area
- Home citizen quick rows
- Citizens directory
- map citizen markers

The avatar manifest supports future full/token art without redesign.

Current fallback:

- neutral mechanical silhouette / token
- initials
- per-citizen interface accent hue

The accent hue is UI identity, not physical paint or appearance.

State animation derives only from validated active jobs:

- idle
- traveling
- charging
- talking
- working

Reduced-motion user preference disables animation.

No equipment, wear, or damage is drawn unless an authoritative physical state supports it.

## Verification

Static verification on `assets/v0.7-home-avatars`:

- 69 HTML IDs
- 65 JavaScript `getElementById` references
- zero missing referenced IDs
- zero duplicate IDs
- JavaScript parsed successfully
- branch is 4 commits ahead / 0 behind shipped v0.6.0
- changed files:
  - `static/index.html`
  - `static/app.js`
  - `static/styles.css`
  - `tests/smoke_v070_assets.py`
- v0.7 Assets smoke-test contract markers are present

## Maintenance Contract — Ready, Not Yet Consumed

World & Simulation delivered the final v0.7 maintenance presentation contract during this session's wrap-up.

Authoritative source:
- branch: `simulation/v0.7-maintenance`
- head: `54f5d838f674d0b278a51382f3a880cc0738b417`
- CI: `36429729279`

Ready fields:

### Citizens
- `battery_health`
- `battery_state`
- `usable_energy_capacity`
- `battery_replacement_due`
- `joint_wear`
- `chassis_service_state`
- `chassis_service_due`
- `last_service_minute`
- existing authoritative `cargo_capacity`

### Equipment
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `last_service_minute`
- `use_count`
- `effective_cargo_bonus`
- `effective_extraction_speed_multiplier`

Raw `cargo_bonus` / `extraction_speed_multiplier` are pristine design values and must not be shown as current capability.

### Structures
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `efficiency_multiplier`
- `last_service_minute`
- `use_count`
- `provides_charging`

### Maintenance history
`state.maintenance_events[]`:
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

The contract arrived after the user requested session wrap-up, so these fields are intentionally recorded but not yet implemented in PR #7.

Memory guidance is already recorded:

- show current condition from Simulation
- do not render every wear tick as Recent Activity
- later maintenance history should include meaningful validated service/failure/repair/replacement only
- admin physical state does not imply a citizen remembers the event

## Current Status

This Assets work session is closed by user request.

Draft PR #7 contains the complete independent Home/avatar/Recent Activity slice plus `tests/smoke_v070_assets.py`.

Assets is **not externally blocked** anymore. The remaining work for the next Assets session is to consume Simulation's now-ready maintenance fields into Citizens / Records and add only meaningful Home degradation alerts.

Exact next steps:
1. read Assets INBOX and COORDINATION
2. inspect `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`
3. render citizen battery/chassis maintenance state
4. render equipment current condition and **effective** capabilities
5. render structure condition / operational / efficiency state
6. add bounded `maintenance_events` presentation to Records
7. add Home alerts only for authoritative meaningful degradation/service-due states
8. exclude `diagnostic` History rows from Recent Activity or render them only as system/debug information
9. rerun `tests/smoke_v070_assets.py` and static verification
10. hand complete PR #7 to coordinator integration

No `update.json`, release metadata, hidden knowledge rules, or physical simulation rules were changed by Assets.
