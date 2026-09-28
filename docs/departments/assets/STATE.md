# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.6.0_
_Current department branch: `assets/v0.7-home-avatars`_
_Current branch head: `dad17d8ef663a4fef367c4260e58074047acf1b3`_
_Current review surface: PR #7 — ready for review_

## Mission

Make Agent City visually understandable and alive while never allowing presentation to invent physical state, hidden knowledge, wear, damage, equipment, or outcomes.

## v0.7 Assets Scope — Complete

Base:
`release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

### Home

- citizen / world / Visit rails share one desktop height budget
- citizen list scrolls internally
- citizen name search/filter supports future population growth
- Visit/chat scrolls internally with input/actions anchored
- compact five-item Recent Activity surface
- "View all history" opens Records → History

Recent Activity rules:

- real stored conversation summaries only
- successful conversation begin/completion chronology is deduplicated
- failed talk attempts remain events only
- Communication `diagnostic` rows are excluded from normal Home activity
- validated maintenance events can appear once
- routine observe/wait churn is filtered

### Avatar first stage

- 2D/static asset manifest for full/token art
- full-body Citizens identity surface
- matching Home / directory / map tokens
- neutral mechanical fallback when final art is absent
- interface accent hue is presentation-only
- state animation derives only from validated jobs:
  - idle
  - traveling
  - charging
  - talking
  - working
- reduced-motion preference disables animation

### Citizen maintenance

Consumes Simulation's authoritative v0.7 fields:

- `battery_health`
- `battery_state`
- `usable_energy_capacity`
- `battery_replacement_due`
- `joint_wear`
- `chassis_service_state`
- `chassis_service_due`
- `last_service_minute`
- authoritative `cargo_capacity`

Citizens page shows battery/chassis service state without inventing visible damage.

### Equipment maintenance

Consumes:

- `condition`
- `condition_state`
- `operational`
- `service_due`
- `last_service_minute`
- `use_count`
- `effective_cargo_bonus`
- `effective_extraction_speed_multiplier`

Current capability uses **effective** fields, never pristine raw modifier fields.

### Structure maintenance

Consumes:

- `condition`
- `condition_state`
- `operational`
- `service_due`
- `efficiency_multiplier`
- `last_service_minute`
- `use_count`
- `provides_charging`

Critical/non-operational structures remain visible.

### Maintenance history

Records → Making now includes bounded `state.maintenance_events[]`:

- event / job IDs
- actor / target
- before → after value when present
- material use when present
- outcome / simulation time / summary

This is physical history. It is not automatically citizen memory.

### Home maintenance alerts

Alerts use Simulation-owned:

- battery replacement due
- chassis service due
- equipment/structure `service_due`
- equipment/structure `operational`
- provided condition states

Assets does not rederive thresholds.

Alerts are capped and sorted by provided severity to avoid maintenance spam.

## Communication / Memory boundaries preserved

- diagnostic talk rows are system/debug history, not citizen dialogue
- failed talk attempts never get conversation cards/transcripts
- claim-extraction diagnostics do not convert a successful stored exchange into a failed conversation
- maintenance physical state does not imply remembered maintenance history

## Verification

Branch-level verification:

- 71 HTML IDs
- 67 JavaScript `getElementById` refs
- zero missing referenced IDs
- zero duplicate IDs
- JavaScript parsed successfully
- all v0.7 Assets contract assertions pass
- branch is 8 commits ahead / 0 behind v0.6.0
- PR #7 is mergeable and marked ready for review

Changed files:

- `static/index.html`
- `static/app.js`
- `static/styles.css`
- `tests/smoke_v070_assets.py`

## Status

Assets & Interface is **REVIEW**.

Next owner: **Coordinator / Integration**.

Coordinator should integrate:

- Simulation `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`
- Communication `communication/v0.7-talk-reliability` @ `61eecc4c047dd3fd22b71612251769a8cb456737`
- Memory's final v0.7 maintenance branch when ready
- Assets `assets/v0.7-home-avatars` @ `dad17d8ef663a4fef367c4260e58074047acf1b3`

Then run the full v0.4-v0.7 regression suite including `tests/smoke_v070_assets.py`.

No `update.json`, release metadata, hidden-knowledge rules, or physical simulation rules were changed by Assets.
