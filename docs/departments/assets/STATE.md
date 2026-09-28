# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.7.0_
_Current department branch: `assets/v0.8-visual-stage1`_
_Current branch head: `af2e058780103755360d143ca964855145e2254a`_
_Current review surface: PR #11 — ready for review_

## Mission

Make Agent City visually understandable and alive while never allowing presentation or generated assets to invent physical reality, hidden knowledge, equipment, quantity, capability, or spatial truth.

## v0.8 Stage 1 — Independent Assets Scope Complete

Base:
`release-v0.7.0` / `d81a85bf03b69b969532016f59bbbed2233949ee`

Stage 1 intentionally establishes visual/UI/asset-generation foundations before continuous-world rendering.

### Home active-job progress

Compact progress is restored to active Home citizen rows.

Displayed only when a real active job exists:

- elapsed simulation minutes
- total simulation minutes
- remaining simulation minutes
- ETA
- progress bar

Source of truth:

- `job.start_minute`
- `job.end_minute`
- `state.sim_minute`

Idle rows remain compact.

### Visitor chat keyboard behavior

- Enter submits
- Shift+Enter inserts newline
- Talk button still uses the same form-submit path
- IME composition never triggers a send
- explicit `chatSubmitting` guard prevents double submission

### Runtime citizen visual profiles

All six founding citizens now have explicit presentation profiles.

- Aris — extraction / prospecting — lean
- Bex — fabrication — compact
- Cato — logistics / resource planning — heavy
- Iri — construction — slim
- Noma — research / experimentation — soft
- Vale — generalist / cooperation — balanced

Each profile provides:

- approved UI accent identity
- silhouette family
- canonical aptitude note
- full / bust / token asset slots
- head expression slots:
  - neutral
  - blink
  - happy
  - focused
  - curious
- empty equipment-layer slots:
  - rear
  - body
  - waist
  - held
  - foreground

Optional gear is not baked into base identity.

The existing v0.7 renderer remains compatible through a flat `CITIZEN_AVATAR_ASSETS` view.

### Fallback silhouette exercise

Until real full-body art is added, the fallback body now exercises the approved silhouette architecture:

- Cato heavier
- Iri slimmer/taller-feeling
- Bex more compact
- Aris leaner
- Noma softer
- Vale balanced

These are presentation proportions only and are not authoritative physical dimensions.

## Durable v0.8 Asset Architecture

### Citizen visual system

`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

Covers:

- shared mechanical species language
- six refined citizen body directions
- identity vs equipment separation
- head tokens
- blink / happy / focused / curious visor expressions
- full-body Citizens-page art
- modular equipment overlays
- later 3D translation rules
- performance/lazy-loading strategy

Core rule:

> **Identity stays. Equipment changes. Expressions live. Simulation remains truth.**

### Local Asset Worker

`docs/departments/assets/V080_ASSET_WORKER_CONTRACT.md`

Defines:

- persistent visual spec identity keyed to authoritative source IDs
- asset job queue lifecycle
- provenance
- asynchronous worker boundary
- fallback behavior
- output/cache strategy
- no Simulation blocking
- no mandatory Blender dependency in Stage 1

Render tiers:

1. unique individual object
2. representative bundle / pile / stack
3. storage abstraction

Core rules:

> **Simulation defines the object. Assets renders the object.**

> **Rendering may aggregate. It may not alter quantity.**

## Spatial Dependency — Deferred Correctly

Continuous-world UI is **not** implemented in this branch.

World & Simulation has not yet published the final seeded spatial read model.

Assets sent a direct request to:
`docs/departments/simulation/INBOX.md`

Needed later:

- safe citizen x/y
- known landmark anchors
- stable discovered subject IDs
- safe observed coordinates
- extent/uncertainty
- reference frame / units
- observation event/source identity
- repeat-encounter subject identity

Assets must not derive continuous coordinates from the current presentation-only map layout.

## Verification

Static branch audit:

- 71 HTML IDs
- 67 JavaScript `getElementById` refs
- zero missing refs
- zero duplicate IDs
- JavaScript parsed successfully
- all Stage 1 contract checks pass
- branch is 6 commits ahead / 0 behind v0.7.0
- PR #11 is mergeable and ready for review

Added:

- `tests/smoke_v080_assets.py`

The current GitHub workflow runs only on `release-v*` pushes, so coordinator integration should run the new smoke with the full assembled suite.

## Status

Assets & Interface Stage 1 is **REVIEW**.

Independent Stage 1 scope is complete.

Continuous-world rendering remains a later dependency on Simulation's seeded spatial contract and should not block review of this foundation.

No `update.json`, release metadata, Simulation rules, hidden seed/world state, or physical coordinate truth were changed by Assets.


## Work Session Closure — v0.8 Stage 1

This Assets & Interface work session is closed.

Final Stage 1 state:
- status: **REVIEW**
- branch: `assets/v0.8-visual-stage1`
- head: `af2e058780103755360d143ca964855145e2254a`
- PR: #11, ready for review
- independent Stage 1 scope: complete

During closeout, World & Simulation delivered the safe seeded spatial read contract:

- branch: `simulation/v0.8-seeded-world-stage1`
- head: `7473b6612ea23cf8d22b31176149da188476690e`

Safe fields now available for a later authorized integration pass:

- `state.spatial_frame`
  - frame: `seed_site_local`
  - units: meters
  - +x east
  - +y north
  - local tangent plane
- locations: `x_m / y_m`
- citizens: `position_x_m / position_y_m`
- structures: `x_m / y_m`
- projects: `x_m / y_m`
- visitor presence: `x_m / y_m`
- `state.spatial_observations[]`

Spatial observations provide safe validated evidence including:
- stable observation ID
- observer/job/time
- observed x/y
- `radius_m` precision
- observed terrain/geology
- optional stable discovered deposit ID/material

Never consume/render:
- raw planet seed
- hidden generated deposits
- hidden body center/axes/orientation/richness
- undiscovered procedural resources
- raw hidden spatial query payloads

Important Stage 1 movement limit:

> Existing route travel remains discrete. While traveling, use the authoritative origin coordinate; switch to destination coordinate only on validated arrival. Do not interpolate a physical continuous path from x/y yet.

This contract is recorded for the next coordinator-authorized stage and was intentionally not wired after the user's stop instruction.

Next owner:
**Coordinator / Stage 1 Review**.

Resume Assets only for:
- Stage 1 review feedback
- coordinator-authorized Stage 2 spatial UI integration
- a new inbox request


## v0.8 Stage 2 — Current Pickup State

Stage 2 is now coordinator-authorized.

Unified Stage 1 integration base:
- branch: `release-v0.8.0`
- commit: `017b417386f4f4e0f957dfb66285431223283739`
- combined CI: `36453177128` — PASS

Requested Assets Stage 2 branch:
`assets/v0.8-exploration-ui-stage2`

Important session truth:
- this chat did **not** create the Stage 2 branch
- this chat did **not** implement Stage 2 UI code
- the new Simulation/Communication contracts were discovered during wrap-up
- next Assets session should begin from the unified Stage 1 base above

### Final Simulation Stage 2 contract

Simulation is complete on:
- `simulation/v0.8-exploration-stage2`
- head `b81c9bb57884727e7a1c769d95ecb27928d1d489`
- CI `36456647323` — PASS

Safe citizen movement:
`state.citizens[].local_movement`
- job_id
- action
- frame_id
- start_x_m / start_y_m
- target_x_m / target_y_m
- path_distance_m
- terrain_multiplier
- start_minute / end_minute
- authoritative current x_m / y_m
- progress
- elapsed / total / remaining minutes

Citizen `position_x_m / position_y_m` is server-derived current position during active movement.

Safe shared physical activity:
`state.shared_activities[]`
- canonical id
- visitor / citizen
- objective / type
- start / target coordinates
- status
- proposed / accepted / started / completed minutes
- source visit / exchange IDs
- tool equipment ID
- citizen job ID
- observation ID
- outcome / failure reason
- movement payload while active

Lifecycle:
- proposed
- accepted
- active
- complete
- rejected
- failed

Simulation endpoints:
- `POST /api/shared-activities/propose`
- `POST /api/shared-activities/{id}/accept`
- `POST /api/shared-activities/{id}/reject`
- `POST /api/shared-activities/{id}/start`
- `GET /api/shared-activities/{id}`

### Communication proposal projection

Assets should consume Communication's Visit/UI projection:
`shared_action_proposals[]`

Important IDs:
- `id` = Communication proposal/provenance ID
- `simulation_activity_id` = canonical Simulation `shared_activities.id`
- `simulation_action_id` = real citizen job ID only after physical start

UI truth:
- proposed/accepted are nonphysical intent states
- active/started requires a real Simulation job
- rejected produces no movement/path marker
- completed exploration result requires Simulation completion + observation ID

### Stage 2 map truth

Assets may now render continuous local movement using only Simulation's authoritative segment/timing/current-position data.

Allowed visual smoothing:
- start coordinate
- target coordinate
- authoritative timing/progress
- server-derived current x/y

Do not:
- invent paths
- expose hidden seeded terrain/deposits
- infer material/geology from baseline observations
- render rejected proposals as movement
- show discovery markers without real observation IDs

Baseline evidence should represent `radius_m` uncertainty rather than false point precision.

### Citizen art / asset-worker Stage 2

Still required:
- continue approved six-citizen base-body/token system
- wire approved art only if actual source files are available
- never invent replacement art merely to fill slots
- optional gear remains separate from base body
- expression frames only when real approved art exists
- turn Stage 1 asset-worker contract into a minimal local queue/spec scaffold if it remains presentation-only
- no Blender dependency yet
- every physical object retains a fallback visual

## Session Closure — Stage 2 Not Yet Implemented

This work session is closed before Stage 2 implementation.

Assets remains an **ACTIVE** Stage 2 department task on the coordination board because the work packet is ready and unblocked, but no Stage 2 code was produced in this chat.

Next session should:
1. read Assets INBOX + COORDINATION
2. create `assets/v0.8-exploration-ui-stage2` from `release-v0.8.0@017b417...`
3. inspect final Communication handoff/head
4. implement local-map + shared-proposal + progress UI
5. add Stage 2 Assets smoke coverage
6. update handoff docs and stop for coordinator integration
