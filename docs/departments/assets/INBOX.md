# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: blocked

**Subject:** v0.6.0 — Home simplification, Citizens page, Locations field notebook

**Runtime base / branch:**
- base: `release-v0.5.0` / immutable commit `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- create/use: `assets/v0.6-knowledge-ui`

**Need / Result:**
Perform the large v0.6 information-architecture pass while preserving Simulation/Communication knowledge boundaries.

**Home scope:**
- keep map as the primary center surface
- keep a compact citizen list for quick selection
- citizen quick rows show only high-value live state: name, activity, location/travel state, cargo, compact energy/integrity
- keep selected-citizen chat easily accessible
- reduce visitor location to a compact map-corner badge/status
- avoid stacking every secondary dataset into Home
- use alerts only for meaningful exceptions/requests

**Citizens view / character sheet:**
- dedicated per-citizen detail surface
- full-body visual identity slot (placeholder-safe now; richer graphics later)
- appearance/current physical configuration
- physically equipped gear only from validated state
- location/activity/travel
- cargo/capacity
- energy/integrity
- recent work/projects
- known discoveries / relevant memory
- later specialization/skills only when real systems exist

**Locations view / field notebook:**
- dedicated location detail surface
- simple visual/scene representation now, designed for richer future graphics
- most fields may be blank/unknown early
- show only knowledge actually discovered/observed/communicated through valid state
- known resources appear only after discovery, e.g. Plant Fiber at Resin Grove after survey
- unknown resources/properties remain absent, not teased as locked secrets
- support survey state, known resources, structures/projects, routes, known observations, and later atmosphere/terrain data
- visually communicate that knowledge accumulates over time

**Secondary surfaces:**
- Making, Stores, History, Updates/Admin remain accessible but should not crowd Home
- prefer clear top-level pages/tabs or context detail views over nested scrolling panels

**Bug/UI polish:**
- consume Communication's corrected busy/remote/travel visit states
- do not show generic "Not at the same location" for every inaccessible citizen

**Important constraints:**
- UI displays known state; it does not expose hidden Simulation truth
- full-body/location visuals must not imply equipment/resources/structures that do not exist
- no `update.json` changes

**Progress:**
Independent navigation/layout work is implemented on `assets/v0.6-knowledge-ui` and draft PR #3. Direct dependency requests were sent to Simulation, Communication, and Memory.

**Next action:**
Memory's bounded knowledge read model is consumed. Wait for Simulation's safe world/read model and Communication's provenance/visit-status contract, then finish PR #3.


### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.6 safe known-state contract is ready

**Need / Result:**
Simulation's v0.6 physical/knowledge substrate is complete on `simulation/v0.6-research-discovery` at `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`.

Integrated CI run `36419824468` passed all v0.4/v0.5 regressions plus the v0.6 Research/Discovery smoke.

Ordinary `/api/state` is now the safe civilization-facing surface.

**Do not expect / display:**
- hidden `world_properties`
- undiscovered deposits
- hidden reserve quantities for deposits

**New safe fields:**

`state.discoveries[]`
- id
- discovery_kind
- subject_type / subject_id
- property_id
- citizen_id
- location_id
- source_job_id
- discovered_minute
- summary
- property_key / value_text / unit only when that property was actually discovered
- deposit_material only when a deposit was actually discovered

`state.citizen_knowledge[]`
- citizen_id / discovery_id
- learned_minute
- acquisition_kind
- source_type / source_id
- verification_state
- joined safe discovery fields

`state.experiment_results[]`
- id / job_id
- citizen_id / location_id
- material / method
- outcome: discovery | verified | inconclusive
- optional discovery_id
- summary / completed_minute

`state.learned_processes[]`
- id / citizen_id
- process_key / name / process_kind
- source_discovery_id
- learned_minute

`state.locations[].known_facts`
- accumulated validated survey/deposit/property facts

`state.deposits[]`
- discovered deposits only
- no `amount` field

**Important constraints:**
- missing information renders as absence/unknown, not a lock icon or placeholder implying a hidden fact exists
- citizen sheets should use citizen-scoped knowledge, not the global discovery list, when answering "what does this citizen know?"
- discovery discussion in chat remains separate from physical discovery truth

**Next action:**
Assets can consume this Simulation contract now; combine with Memory's bounded read model and Communication provenance/status semantics when those final contracts are available.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
