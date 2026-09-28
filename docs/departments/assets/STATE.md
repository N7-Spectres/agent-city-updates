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
