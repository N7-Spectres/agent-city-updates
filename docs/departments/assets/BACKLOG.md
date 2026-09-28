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

## Ready for Next Authorized Stage — Simulation Spatial Contract

Simulation contract is now ready on:
`simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`

Safe future UI inputs:
- `state.spatial_frame`
- location `x_m/y_m`
- citizen `position_x_m/position_y_m`
- structure/project `x_m/y_m`
- visitor `x_m/y_m`
- `state.spatial_observations[]`
- observation `radius_m`
- stable discovered subject/deposit identity

Stage 2 guardrails:
- no hidden seed/generated-body access
- no precision beyond `radius_m`
- no continuous travel interpolation yet
- existing route travel remains discrete until Simulation adds continuous movement

Do not begin this wiring until coordinator authorizes the next stage.

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

The spatial contract is ready, but continuous-world UI remains intentionally deferred to the next coordinator-authorized stage.


## Active Next Session — v0.8 Stage 2 Assets

Base:
`release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`

Create/use:
`assets/v0.8-exploration-ui-stage2`

### Continuous local map
- consume authoritative citizen `position_x_m/y_m`
- consume `local_movement`
- consume authoritative visitor x/y
- preserve named landmarks
- render only validated observations/discovered contacts
- show uncertainty/radius rather than false exactness
- smooth only authoritative start/target/timing segment
- preserve reduced-motion fallback

### Shared-action UI
- consume `shared_action_proposals[]`
- compact proposal card near/in Visit
- proposed/accepted styling must look nonphysical
- explicit visitor acceptance
- show real active progress only after Simulation job exists
- support canonical reject path
- complete marker/result only from Simulation observation ID
- never render rejected proposals as paths

### Existing Stage 1 behavior to preserve
- Home active-job progress
- Enter-to-send
- Shift+Enter newline
- IME-safe chat
- six citizen visual profiles
- maintenance/history boundaries

### Citizen art
- wire refined full-body/head-token exports only if actual approved files are available
- otherwise keep manifest slots empty and document exact export requirements
- optional equipment stays separate
- expression animation only from approved real frames

### Asset worker
- minimal local queue/spec scaffold only if presentation-owned
- no Blender dependency
- no generated 3D requirement
- fallback visual always available
- render aggregation remains presentation-only

### Validation
- add `tests/smoke_v080_assets_stage2.py` or coordinator-approved equivalent
- preserve all Stage 1/v0.7 Assets smoke coverage
- static DOM ID/reference audit
- JS syntax
- runtime checks for proposal lifecycle and movement truth boundaries

## Current Dependencies

Simulation: **resolved**
- final Stage 2 head `b81c9bb...`
- CI `36456647323` PASS

Communication:
- Stage 2 proposal bridge exists on `communication/v0.8-shared-actions-stage2`
- Assets still needs the final post-reject-adapter branch head/handoff before coordinator assembly
- request routed to Communication INBOX during this wrap-up

No other Stage 2 Assets dependency is currently known.
