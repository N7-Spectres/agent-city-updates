# Assets & Interface — Backlog

## Review / Validation — v0.8 Stage 1

- review PR #11 / `assets/v0.8-visual-stage1`
- run `tests/smoke_v080_assets.py` during coordinator/release assembly
- verify active-job progress against real travel/survey/extract/charge/fabricate/construct/experiment/maintenance jobs
- verify idle citizen rows remain compact
- verify Enter submits once
- verify Shift+Enter inserts newline
- verify IME composition cannot submit
- verify Talk button remains functional
- verify citizen visual profiles preserve the six approved roles/silhouettes
- verify no optional equipment appears from visual profile metadata alone
- verify v0.7 Home/avatar/maintenance behavior remains intact

## Completed — v0.8 Stage 1 Assets

- restored Home active-job progress
- elapsed / total / remaining / ETA display
- Enter-to-send visitor chat
- Shift+Enter multiline
- IME-safe keyboard behavior
- duplicate-submit guard
- six runtime citizen visual profiles
- approved silhouette fallback exercise
- expression asset slots
- empty modular equipment-layer slots
- citizen visual-system architecture
- local Asset Worker contract
- render aggregation tiers
- asynchronous fallback/provenance rules
- v0.8 Assets Stage 1 smoke test

## Waiting — Simulation Spatial Contract

Assets direct request is in:
`docs/departments/simulation/INBOX.md`

Do not start continuous-world UI placement until Simulation hands off:

- coordinate frame / units
- safe citizen x/y
- landmark anchors
- stable generated subject IDs
- safe observed subject coordinates
- safe extent / uncertainty
- discovery/observation event IDs
- repeat-encounter identity semantics

This is a dependency for later continuous-world UI, not a blocker for Stage 1 review.

## Stage 2 / Later

- consume Simulation seeded spatial read model
- replace presentation-only map positioning with physical coordinates where appropriate
- real head token assets for all six citizens
- blink / happy / focused / curious visor frames
- full-body base-body web assets
- bust assets
- lazy-loading asset manifest
- authoritative equipment overlays after equipped/attachment semantics exist
- persistent asset queue implementation after coordinator approves Stage 1 contract
- deterministic procedural geometry worker
- optional Blender/headless integration later
- richer world/structure/object rendering
- LOD / instancing / aggregation implementation

## Current Blockers

_None for Stage 1 review._

Continuous-world rendering is intentionally deferred until Simulation's spatial contract is ready.
