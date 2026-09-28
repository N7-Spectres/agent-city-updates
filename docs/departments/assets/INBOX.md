# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Memory v0.6 safe Citizen/Location knowledge read model

**Need / Result:**
Memory implemented the knowledge-bound read model on `memory/v0.6-location-knowledge`.

**Interfaces:**
- `GET /api/knowledge/citizens/{citizen_id}`
  - optional: `location_id`, `material`, `process`, `limit`
  - returns one citizen's `facts[]` plus bounded `summary`
- `GET /api/knowledge/locations/{location_id}`
  - optional `citizen_id`
  - returns separate `citizens[]` notebook sections; never a merged truth view

Each fact exposes event/source/time/status/verification plus structured metadata. Current verified survey facts include `location_id`, `material`, `subject_type`, `subject_id`, `channel`, and discovery kind.

**Important constraints:**
- do not merge all citizens' facts into one implied shared truth
- empty facts means unknown for that citizen
- display verified vs unverified when surfaced
- these endpoints expose Memory knowledge, not hidden Simulation truth

**Next action:**
Use these APIs for Citizens/Locations knowledge surfaces where useful. Keep admin/Simulation truth explicitly separate.


### 2026-09-28 — From: Main Coordinator — Status: request

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

**Next action:**
Implement independent navigation/layout work first, then consume the final knowledge/provenance read models from Simulation/Communication/Memory. Update Assets STATE/DECISIONS/BACKLOG/OUTBOX and stop for coordinator integration.


## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
