# Assets & Interface — State

_Last updated: 2026-09-28_
_Current integration base: `release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`_
_Current department branch: `assets/v0.8-exploration-ui-stage2`_
_Current branch head: `7f5294efaab738b44af116514a65d22478851ad0`_
_Current review surface: PR #15 — ready for review_

## Mission

Make Agent City visually understandable and alive while never allowing presentation, animation, or generated assets to invent physical reality, hidden knowledge, equipment, quantity, capability, or spatial truth.

Core rendering law:

> **Simulation defines reality. Assets renders reality.**

## v0.8 Stage 2 — Assets Complete

Assets & Interface has completed its Stage 2 implementation.

Base:
`release-v0.8.0` / `017b417386f4f4e0f957dfb66285431223283739`

Final branch:
`assets/v0.8-exploration-ui-stage2` / `7f5294efaab738b44af116514a65d22478851ad0`

PR:
**#15 — Assets: v0.8 Stage 2 continuous local map and shared-action UI**

Status:
**REVIEW**

### Continuous local meter-space map

The Home world view now consumes Simulation's safe Stage 2 spatial state:

- `state.spatial_frame`
- location `x_m / y_m`
- citizen `position_x_m / position_y_m`
- citizen `local_movement`
- authoritative visitor `x_m / y_m`
- `state.spatial_observations[]`

Presentation behavior:

- normal view is a physically scaled meter-space regional map
- +x is east
- +y is north
- named locations remain recognizable physical anchors
- when a selected citizen/shared activity moves only tens of meters, the map automatically switches to a local meter focus so movement remains readable
- this local focus changes only viewport/scale, never physical coordinates
- if safe meter-space data is absent, the older map presentation remains a compatibility fallback

### Continuous movement truth

For Stage 2 local/shared movement, Assets renders only Simulation's authoritative segment:

- start x/y
- target x/y
- authoritative current x/y
- start/end timing
- progress
- path distance

CSS may visually smooth between authoritative refreshes.

Assets does **not**:

- invent waypoints
- choose an alternate route
- extrapolate beyond the authoritative segment
- expose hidden terrain used internally for movement cost

`prefers-reduced-motion` disables the smoothing transition.

Legacy named-route travel keeps its existing compatibility representation.

### Validated exploration observations

Map evidence comes only from:
`state.spatial_observations[]`

Each visible observation may use:

- stable observation ID
- observed x/y
- `radius_m`
- safe terrain
- safe detail level
- safe discovered material/geology only when actually exposed
- safe stable deposit/contact ID when present

Uncertainty is rendered as a radius ring rather than a falsely precise point.

Baseline observations explicitly do **not** reveal:

- material
- classified geology
- hidden deposit center
- hidden deposit axes/orientation
- richness
- undiscovered procedural resources

The Assets JavaScript contains no dependency on:
- `planet_seed`
- `generated_deposits`
- hidden body geometry/richness

### Shared visitor physical activity

Visit now consumes Communication's final:
`shared_action_proposals[]`

Identity separation is preserved:

1. Communication proposal ID = social/provenance projection
2. Simulation `shared_activities.id` = canonical shared physical event
3. Simulation `jobs.id` = actual physical movement job

Proposal presentation:

- `proposed` = intent, visually nonphysical
- accepted without a real job = intent, visually nonphysical
- `started` + `simulation_action_id` = active physical activity
- `completed` = Simulation-completed activity
- rejected / failed / cancelled / expired = no active movement

Visitor controls use Communication's final endpoints:

- `POST /api/shared-actions/{proposal_id}/accept`
- `POST /api/shared-actions/{proposal_id}/reject`

A proposal card explicitly states that proposal is not movement.

Accept/start visuals appear only after Communication returns the real Simulation job identity.

Canonical Simulation rejection is preferred for the visible "Declined" label even if a broader Communication sync state later buckets it as failed.

### Visitor physical marker

During a real shared activity, the visitor marker uses authoritative visitor-presence x/y supplied by Simulation.

Chat agreement alone never moves the visitor.

### Stage 1 UI preserved

Stage 2 retains:

- Home active-job progress bars
- elapsed / total / remaining / ETA
- Enter-to-send
- Shift+Enter newline
- IME-safe submission
- duplicate-submit guard
- six runtime citizen visual profiles
- v0.7 maintenance/history truth boundaries

## Citizen Art Status

The approved concept direction remains canonical presentation reference through:

`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

Assets checked the expected repository locations for runtime-ready citizen art.

No approved base-body/head-token files are currently present.

Therefore:

- visual-profile asset slots remain intentionally empty
- no chat-generated image was silently committed as canon
- no substitute citizen art was invented
- no concept-art backpack/tool/medical/cargo gear was treated as physical equipment

When real source art is added later, required exports remain:

- transparent equipment-free full-body base
- matching head token
- neutral / blink / happy / focused / curious visor frames as available
- consistent canvas/body anchors
- optional equipment as separate layers

## Local Asset Worker Scaffold

Added:
`agent_city/asset_worker.py`

This is a presentation-only asynchronous scaffold.

It uses a separate local database:
`data/asset_worker.db`

It does not import or mutate Agent City's Simulation database.

Implemented:

- `AssetSpec`
- persistent source type / ID / revision / spec version
- render tiers:
  - `individual`
  - `bundle`
  - `storage`
- persistent `asset_specs`
- persistent `asset_jobs`
- status lifecycle:
  - queued
  - working
  - ready
  - failed
- atomic worker claim using `BEGIN IMMEDIATE`
- attempt count
- output path / format
- content hash
- generator version
- error metadata
- idempotent reuse of the same queued/working/ready physical revision

No Blender dependency exists yet.
No 3D generation is required yet.
A missing rich asset never blocks or changes the physical object.

Full architecture:
`docs/departments/assets/V080_ASSET_WORKER_CONTRACT.md`

## Validation

Final static audit:

- 73 HTML IDs
- 69 JavaScript `getElementById` refs
- zero missing DOM refs
- zero duplicate IDs
- JavaScript parses successfully
- hidden seeded-truth identifiers absent from Assets JS
- branch 10 commits ahead / 0 behind unified Stage 1 base
- final branch contains only five changed files

Final changed files:

- `agent_city/asset_worker.py`
- `static/app.js`
- `static/index.html`
- `static/styles.css`
- `tests/smoke_v080_assets_stage2.py`

### Real branch CI

Temporary PR-only validation workflow run:

**GitHub Actions `36460454385` — PASS**

Passed:

- Node JavaScript syntax
- `tests/smoke_v080_assets.py`
- `tests/smoke_v080_assets_stage2.py`

The Stage 2 smoke also exercised the actual temporary SQLite AssetQueue lifecycle:
queue → claim → ready → idempotent reuse.

The temporary workflow was deleted after validation and is not part of the final branch.

## Upstream Final Contracts Consumed

### World & Simulation

- branch: `simulation/v0.8-exploration-stage2`
- head: `b81c9bb57884727e7a1c769d95ecb27928d1d489`
- CI: `36456647323` PASS

### Communication & Perception

- branch: `communication/v0.8-shared-actions-stage2`
- head: `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- CI: `36457633293` PASS

### Memory & Social

- branch: `memory/v0.8-exploration-stage2`
- head: `306a9ef4329ab81afa5912846333a1d9782ee9be`
- CI: `36455394456` PASS

## Status / Next Owner

Assets & Interface is **REVIEW**.

No remaining Assets-owned Stage 2 dependency exists.

Next owner:
**Coordinator / Stage 2 Integration**

Coordinator should integrate Simulation + Communication + Memory + Assets onto the unified v0.8 branch and run the complete regression matrix, including:

- all shipped v0.4-v0.7 smokes
- all v0.8 Stage 1 smokes
- `tests/smoke_v080_stage2.py`
- `tests/smoke_v080_communication_stage2.py`
- `tests/smoke_v080_memory_stage2.py`
- `tests/smoke_v080_assets_stage2.py`

No `update.json` or release publication changes were made by Assets.
