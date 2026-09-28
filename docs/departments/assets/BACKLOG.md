# Assets & Interface — Backlog

## Review / Integration — v0.8 Stage 2

Assets implementation is complete.

Review surface:

- branch `assets/v0.8-exploration-ui-stage2`
- head `7f5294efaab738b44af116514a65d22478851ad0`
- PR #15 — ready for review
- Assets branch CI `36460454385` — PASS

Coordinator integration should verify:

- meter-space map keeps +x east / +y north
- automatic local focus is readable without changing physical coordinates
- citizen local movement follows authoritative current x/y
- local route line uses only Simulation start/target segment
- reduced-motion disables browser smoothing
- visitor shared movement uses authoritative visitor presence
- proposed/accepted proposal cards remain visibly nonphysical
- active proposal styling requires real `simulation_action_id`
- accept calls final Communication endpoint
- reject calls canonical final Communication/Simulation rejection path
- rejected proposals never produce movement markers
- completed exploration evidence appears only from real observation IDs
- baseline observations do not expose material/geology
- `radius_m` uncertainty remains visible
- hidden seed/generated-body geometry remains inaccessible
- Stage 1 Home progress/chat behavior remains intact
- v0.7 maintenance/history truth boundaries remain intact
- AssetQueue database remains presentation-only and separate from Simulation

Required Assets test:
`tests/smoke_v080_assets_stage2.py`

## Completed — v0.8 Stage 2 Assets

- authoritative continuous local meter-space map
- regional + automatic local-focus viewport
- physical landmark anchors
- authoritative citizen local movement positions
- authoritative visitor shared-walk position
- Simulation-defined movement segment display
- validated observation markers
- observation uncertainty rings
- baseline evidence privacy
- shared-action proposal cards
- explicit accept/start control
- canonical reject control
- active physical progress display
- proposal-vs-physical truth styling
- final Communication/Simulation ID binding
- presentation-only persistent AssetQueue scaffold
- Stage 2 Assets smoke
- real GitHub Actions branch validation

## Citizen Art — Pending Source Files

Approved visual direction is documented, but runtime-ready source art is not currently stored in the repository.

When source files become available:

- export transparent equipment-free full bodies
- export matching head tokens
- export neutral / blink / happy / focused / curious frames as approved
- preserve common canvas/anchor conventions
- keep optional equipment separate
- optimize for WebP/AVIF where appropriate
- populate the existing runtime manifest/profile slots
- add asset-presence/lazy-load smoke coverage

Do not generate replacement runtime art merely to fill these slots.

## Later Asset / Rendering Work

- actual local worker process consuming `asset_jobs`
- deterministic procedural geometry recipes
- runtime generated-asset lookup/cache API
- GLB output integration
- Blender/headless generator only if later justified
- richer object/structure visuals
- equipment overlay attachment slots after Simulation exposes authoritative equipped-state semantics
- LOD / instancing
- quantity-aware resource pile/fullness presentation
- later globe/global-coordinate rendering

## Current Blockers

_None for Assets Stage 2._

Next owner:
**Coordinator / Stage 2 Integration**


## v0.8.1 Citizen Visual Asset Hotfix

- prepare runtime-ready art exports for all six founding citizens
- recommended minimum per citizen:
  - transparent full-body PNG
  - bust/head token PNG
  - compact map/home token PNG
- optional expression frames may follow if approved source art supports them
- populate existing `CITIZEN_VISUAL_PROFILES` asset slots
- preserve silhouette/color/base-body canon
- do not bake optional gear into authoritative identity if it is meant to reflect runtime equipment later
- do not treat concept-art props, scanners, packs, tools, drones, medical kits, or cargo rigs as owned inventory
- keep clean fallbacks when a frame is absent
- no Simulation/Communication/Memory behavior changes
- run Assets smoke plus the full assembled regression suite before publication
