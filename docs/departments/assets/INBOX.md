# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.7.0 final Assets pass required before integration

Handoff review found PR #7's independent Home/avatar work is ready, but the v0.7 maintenance presentation contract arrived after the prior wrap and is not yet consumed.

**Finish before coordinator integration:**
- render citizen battery health/state, usable capacity, battery replacement due, joint/chassis service state
- render equipment condition/operational/service state and authoritative effective modifiers
- render structure condition/operational/service/efficiency state
- add bounded meaningful `maintenance_events` presentation to Records
- add Home alerts only for meaningful authoritative degradation/service-due states
- keep diagnostic talk rows out of normal conversation presentation/Recent Activity
- rerun/update `tests/smoke_v070_assets.py` and static verification
- update STATE/OUTBOX/COORDINATION with final branch head and green validation

Do not rederive Simulation thresholds in JS. No `update.json` changes.

**Next action:** Continue the existing `assets/v0.7-home-avatars` branch and hand the completed PR #7 back to the coordinator.


### 2026-09-28 — From: Memory & Social — Status: note

**Subject:** Memory v0.7 maintenance history presentation guidance

**Need / Result:**
Memory's v0.7 audit is complete, but no maintenance-history API is being invented before Simulation's event schema exists.

For UI planning:
- current condition/wear comes from Simulation physical state
- Memory history should later show only meaningful validated failures/repairs/replacements/service
- do not render every wear tick as Recent Activity
- do not imply a citizen remembers a repair merely because admin state shows it happened

**Next action:**
Continue condition presentation from Simulation. Memory will hand off a bounded maintenance-history read model only if the final physical event contract makes one useful.

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.7.0 — Home scaling, Recent Activity, and avatar first stage

**Runtime base / branch:**
- base: `release-v0.6.0` / immutable commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- create/use: `assets/v0.7-home-avatars`

**Home layout scope:**
- extend citizen rail to roughly map height on desktop
- keep citizen list internally scrollable
- reserve/add a citizen name search/filter suitable for future population growth
- extend Visit/chat rail to roughly map height on desktop
- keep chat internally scrollable with anchored input/actions
- add compact Home Recent Activity showing about 5 latest meaningful events/conversations
- provide a clear "View all history" action to Records → History
- conversation summaries only from real stored exchanges; failed talk attempts remain events only
- maintain responsive behavior on smaller screens

**Avatar first stage:**
- no Mixamo/3D requirement
- add lightweight 2D/static identity support for each citizen
- Citizens page: full-body visual identity area
- Home/map: smaller matching token/crop where practical
- simple CSS/JS state animation is allowed: idle pulse/bob, travel movement, charging glow, talking/working indicator
- animation must derive from validated state
- equipment should alter visuals only when authoritative physical equipment supports it
- if final unique art is not yet available, build the asset slots/fallback visuals cleanly so identity art can be dropped in later without redesign

**Maintenance UI:**
- once Simulation hands off condition fields, show meaningful equipment/structure/battery-health condition on Citizens/Records without overwhelming Home
- alerts should highlight meaningful degradation, not every tiny percentage change

**Important constraints:**
- presentation cannot create physical state
- do not invent worn gear/damage that Simulation does not expose
- no `update.json` changes

**Progress:**
Independent layout/avatar/Recent Activity scope is implemented on `assets/v0.7-home-avatars` and draft PR #7. Assets smoke coverage exists at `tests/smoke_v070_assets.py`.

Simulation has now delivered the maintenance contract on `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`. Communication also delivered v0.7 diagnostic guidance; Memory delivered maintenance-history guidance.

**Next action:**
Next Assets session should consume the ready maintenance fields into Citizens/Records and add only meaningful Home alerts, update the smoke test as needed, then hand the completed PR #7 to coordinator integration.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.7 talk reliability History/debug contract

**Need / Result:**
Communication's v0.7 reliability slice is ready on `communication/v0.7-talk-reliability` @ `61eecc4c047dd3fd22b71612251769a8cb456737`.

Normal successful conversation UI does not change:
- real exchange remains in `citizen_conversations`
- canonical conversation/source-job IDs remain intact

Hard failed talks still produce the existing concise chronology event:
- conversation attempt ended without a recorded exchange

When Communication has a precise internal cause, Simulation may also add a separate History row:
- `category = "diagnostic"`
- message form: `Talk job #<id> failed before durable exchange: <code>.`

**UI guidance:**
- never render a diagnostic row as citizen dialogue
- diagnostic rows may be omitted from Home Recent Activity, or shown only as muted/system/debug information
- failed talk attempts remain events only and must not get conversation cards/transcripts
- a degraded claim-extraction diagnostic does not mean the conversation failed; if a real `citizen_conversations` row exists, the raw exchange succeeded

**Important reliability semantic:**
Raw conversation persistence now happens before best-effort claim extraction. Claim enrichment failure must not be presented as a failed physical conversation.

**Validation:**
CI `36428495003` passed all v0.4/v0.5/v0.6 regressions plus v0.7 Communication smoke.

**Next action:**
No required frontend change unless PR #7 wants to surface diagnostic-category History. Preserve the distinction between conversation records, failed talk events, and optional diagnostics.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.7 final maintenance/condition fields for Assets

**Need / Result:**
Simulation's v0.7 maintenance core is ready on `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`.

Runtime code passed the complete v0.4-v0.7 smoke chain in CI run `36429729279`; the only later branch commit restored the release-only workflow.

Use these authoritative fields.

**Citizens — `state.citizens[]`:**
- `battery_health`
- `battery_state`
- `usable_energy_capacity`
- `battery_replacement_due`
- `joint_wear`
- `chassis_service_state`
- `chassis_service_due`
- `last_service_minute`
- existing `cargo_capacity` remains authoritative from `/api/state`

**Equipment — `state.equipment[]`:**
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `last_service_minute`
- `use_count`
- `effective_cargo_bonus`
- `effective_extraction_speed_multiplier`

The old raw `cargo_bonus` and `extraction_speed_multiplier` are pristine design values. Display the **effective** fields for current capability.

**Structures — `state.structures[]`:**
- `condition`
- `condition_state`
- `operational`
- `service_due`
- `efficiency_multiplier`
- `last_service_minute`
- `use_count`
- `provides_charging`

**Maintenance history — `state.maintenance_events[]`:**
- `id`, `job_id`, `citizen_id`
- `event_type`
- `target_type`, `target_id`
- `before_value`, `after_value`
- `materials_json`
- `outcome`
- `sim_minute`
- `summary`

**Important constraints:**
- do not rederive thresholds or condition math in JavaScript
- condition state is physical state, not hidden knowledge
- critical tools/structures remain visible but `operational = false`
- routine tiny wear should not dominate Recent Activity; completed maintenance events and meaningful threshold messages are the interesting layer

**Next action:**
Assets can now finish its v0.7 maintenance presentation without waiting on Simulation.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
