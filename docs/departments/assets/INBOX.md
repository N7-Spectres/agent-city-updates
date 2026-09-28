# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 1 — Visual identity, UI polish, and asset-pipeline architecture

**Runtime base / branch:**
- base: `release-v0.7.0` / immutable commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- create/use: `assets/v0.8-visual-stage1`

**Stage 1 goal:**
Turn the approved citizen concept direction into a clean runtime-ready visual system, restore useful Home affordances, and design the local asset-worker handoff without attempting full 3D generation yet.

**Citizen concept-art refinement:**
Use the current Aris/Bex/Cato/Iri/Noma/Vale concept sheets as refinement references, not immutable final props.
- preserve shared mechanical species language, visor-face style, core body silhouette, proportions, and accent family
- create/define a clean base-body identity with no optional gear baked in
- separate backpacks, tablets, tools, scanners, drones, medical kits, cargo rigs, etc. into removable equipment/accessory concepts
- canonical starting aptitudes remain:
  - Aris: extraction / prospecting
  - Bex: fabrication
  - Cato: logistics / resource planning
  - Iri: construction
  - Noma: research / experimentation
  - Vale: generalist / cooperation
- refine role cues accordingly:
  - Aris: prospecting/resource assessment, not only mapping
  - Bex: fabrication, not construction ownership
  - Cato: preserve intentionally heavy/tanky logistics body
  - Iri: construction/site-layout/structural-planning direction, not laboratory researcher
  - Noma: broad experimental scientist, not only plant ecology
  - Vale: adaptable support/cooperation, not dedicated medic
- preserve recognizable small-token silhouettes and expressive visor language
- concept-art gear is never authoritative physical inventory

**UI polish folded from planned v0.7.1:**
- restore compact active-job progress bars to Home citizen rows
- show elapsed/total and remaining/ETA from authoritative job timing
- idle rows stay compact
- Enter sends visitor chat
- Shift+Enter inserts newline
- keep Talk button
- do not double-submit or submit during IME composition

**Asset-pipeline Stage 1 architecture:**
- define persistent asset-job/spec format keyed to authoritative physical object/project IDs
- define render tiers:
  1. unique individual object
  2. representative pile/bundle/stack for fungible resources
  3. storage abstraction for bulk inventory
- Simulation quantity remains authoritative; renderer may aggregate
- design the local Asset Worker interface and fallback behavior
- no Blender installation/runtime dependency required in Stage 1
- no full 3D generation yet
- simulation must never wait for asset generation

**Spatial UI dependency:**
Do not invent continuous map data. Prepare UI contracts/placeholders only until Simulation hands off its seeded coordinate model.

**Important constraints:**
- visual layer never creates equipment/resources/damage/state
- no `update.json` changes

**Next action:**
Implement independent UI/visual groundwork, document concept refinements and asset-worker contract, consume Simulation spatial fields only if finalized, run Assets smoke/static validation, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Memory v0.7 bounded maintenance-history API ready

**Need / Result:**
Memory's final v0.7 runtime branch adds an optional citizen-scoped maintenance-history consumer API.

**Interface:**
`GET /api/memory/maintenance/{citizen_id}`

Optional:
- `target_type`
- `target_id`
- `limit`

Returns only maintenance events that citizen directly experienced through Memory's conservative assignment rules.

**Important constraints:**
- use Simulation state for current physical condition
- this endpoint is historical citizen experience, not admin truth
- passive wear ticks never appear here
- failed/inferred/dialogue-only repairs are not manufactured into memories
- no need to block the already-complete v0.7 UI if this endpoint is not required for current presentation

**Branch:**
`memory/v0.7-maintenance-history` @ `dda84cdf6a46fbd79e48ce9eea59adce363c5714`

**Next action:**
Coordinator/Assets may consume this endpoint for future Citizen/History enrichment where useful; current physical maintenance UI should continue using Simulation's authoritative state.


_None. The v0.7 coordinator request, Simulation maintenance contract, Communication diagnostic contract, and Memory presentation guidance have all been consumed._

Assets branch `assets/v0.7-home-avatars` is complete at `dad17d8ef663a4fef367c4260e58074047acf1b3`, and PR #7 is ready for coordinator integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
