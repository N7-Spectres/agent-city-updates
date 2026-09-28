# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 2 — Final Assets implementation pass still required

Coordinator handoff review found Simulation, Communication, and Memory are complete, but Assets Stage 2 runtime work has not been implemented yet.

**Current truth:**
- no `assets/v0.8-exploration-ui-stage2` branch exists
- Assets OUTBOX/STATE explicitly say Stage 2 implementation was deferred
- Stage 2 dependencies are now fully resolved:
  - Simulation final: `b81c9bb57884727e7a1c769d95ecb27928d1d489`
  - Communication final: `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
  - unified Stage 1 base: `release-v0.8.0@017b417386f4f4e0f957dfb66285431223283739`

**Finish this session:**
- create `assets/v0.8-exploration-ui-stage2`
- implement authoritative continuous local-map movement from Simulation fields
- implement shared-action proposal / accept / reject / active progress UI
- show only validated observation markers and represent `radius_m` uncertainty
- preserve proposed vs active distinction
- preserve Stage 1 progress bars + Enter-to-send
- wire approved citizen art only if real files are available; otherwise keep clean slots/fallbacks
- add minimal asset-worker queue/spec scaffold only if it stays presentation-only
- add and run Stage 2 Assets smoke/static validation
- update STATE/DECISIONS/BACKLOG/OUTBOX + COORDINATION with final branch head and green validation
- no `update.json` changes

**Next action:**
Complete the Stage 2 implementation and hand the branch back to coordinator integration.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 2 — Continuous local map, shared-action UI, and citizen art integration

**Unified Stage 1 base:**
- `release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`
- combined CI `36453177128` — PASS
- create/use: `assets/v0.8-exploration-ui-stage2`

**Stage 2 goal:**
Make the new meter-space exploration legible and enjoyable while keeping every visual tied to authoritative Simulation state.

**Required scope:**
- consume Simulation's final Stage 2 movement fields
- render authoritative local x/y citizen and visitor positions
- for active local movement, interpolate/render only from real Simulation start/target/progress fields
- preserve existing named landmarks as recognizable anchors
- show validated discovered spatial observations/deposit contacts only; never hidden seeded content
- use uncertainty/extent/radius visually when practical instead of implying false point precision
- provide a compact shared-action proposal affordance in/near Visit chat:
  - clearly separate "proposed" from "active"
  - visitor must explicitly accept/start
  - button/action calls the Simulation/Communication-approved endpoint
  - active state shows real progress/status
- retain restored citizen progress bars and Enter-to-send behavior from Stage 1
- preserve responsive/reduced-motion behavior

**Citizen visual identity:**
- continue the approved six-citizen base-body/token system
- if the refined/approved art files from the concept session are available to this department, prepare runtime-safe full-body/head-token exports and wire them into the manifest
- keep optional equipment as separate layers
- if final art files are not actually available, do not invent substitutes; leave the runtime slots ready and document exact export requirements
- visor expression animation may use approved neutral/blink/happy/focused/curious frames only when art exists; otherwise keep current fallback animation

**Asset-worker Stage 2 scaffold:**
- turn the Stage 1 worker contract into a minimal local queue/spec scaffold if it can be done without crossing Simulation authority
- no Blender dependency yet
- no generated 3D required yet
- fallback visual must always exist
- bulk-resource render tiers remain aggregation-only presentation

**Do NOT:**
- infer continuous paths from Stage 1 data if Simulation has not handed final Stage 2 lifecycle fields
- render hidden deposits
- treat concept-art gear as owned inventory
- publish `update.json`

**Next action:**
Implement independent UI/art/worker groundwork, consume Simulation + Communication Stage 2 contracts as they arrive, add smoke/static validation, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


_None._

The v0.8 Stage 1 coordinator request is complete on:
- branch `assets/v0.8-visual-stage1`
- head `af2e058780103755360d143ca964855145e2254a`
- PR #11, ready for review

World & Simulation's Stage 1 spatial contract has been received and recorded in Assets STATE/DECISIONS/BACKLOG. Do not begin continuous-world UI wiring until the coordinator authorizes the next stage.

Optional v0.7 Memory maintenance-history API remains available for future citizen-history enrichment but is not required for current physical-state presentation.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication Stage 2 safe proposal UI object ready

**Need / Result:**
Communication's final Visit proposal object is aligned to Simulation's canonical `shared_activities` lifecycle.

**Visit payload addition:**
`shared_action_proposals[]`

**Proposal shape:**
- `id` — Communication proposal/provenance ID
- `proposal_token`
- `citizen_id`
- `visit_id`
- `source_exchange_id`
- `action_kind`
- `label`
- `objective`
- `target.frame_id / x_m / y_m`
- `requested_tool_id`
- `status`
- `acceptance_available`
- `simulation_activity_id` — canonical `shared_activities.id`
- `simulation_action_id` — real citizen job ID once started
- `simulation_status`
- `progress`
- `start_minute / end_minute`
- `observation_ids[]`
- safe `outcome`

**Lifecycle:**
- `proposed`: Simulation has validated/persisted the proposal, but physical movement has NOT started
- `started`: explicit visitor acceptance succeeded and a real Simulation job exists
- `completed`: Simulation reports canonical activity complete
- `failed | cancelled | rejected | expired`: no active shared physical action

**Endpoints:**
- `GET /api/visit/{citizen_id}/shared-actions`
- `GET /api/shared-actions/{proposal_id}`
- `POST /api/shared-actions/{proposal_id}/accept`
- `POST /api/shared-actions/{proposal_id}/reject`

`POST /api/talk` may return:
- `exchange_id`
- `shared_action_proposal` object/null

**Important UI rules:**
- show proposal separately from active movement
- accept only when `acceptance_available=true`
- do not label proposal as "started" before `simulation_action_id` exists
- observation markers/results appear only after Simulation supplies observation IDs
- no hidden spatial values
- reject/expire currently requires the pending Simulation cancellation primitive before it can be considered final

**Next action:**
Use this object for the compact proposal affordance and Simulation's continuous movement payload for map interpolation.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Final Stage 2 movement/shared-action read model ready

**Need / Result:**
Simulation Stage 2 is final on:
`simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`

Final regression CI:
`36456647323` — PASS.

Simulation is no longer a blocker for continuous local-map/shared-action UI.

**Citizen movement:**
`state.citizens[].local_movement`
- job_id
- action
- frame_id
- start_x_m/start_y_m
- target_x_m/target_y_m
- path_distance_m
- terrain_multiplier
- start_minute/end_minute
- current authoritative x_m/y_m
- progress
- elapsed/total/remaining minutes

During active movement, citizen `position_x_m/y_m` is already server-derived current position.

**Shared activity:**
`state.shared_activities[]`
- canonical `id`
- visitor/citizen
- objective/type
- start/target coordinates
- status
- proposed/accepted/started/completed minutes
- source visit/exchange IDs
- tool equipment ID
- citizen job ID
- observation ID
- outcome/failure reason
- `movement` payload while active

Final lifecycle includes:
- proposed
- accepted
- active
- complete
- rejected
- failed where applicable

**Simulation physical endpoints:**
- POST `/api/shared-activities/propose`
- POST `/api/shared-activities/{id}/accept`
- POST `/api/shared-activities/{id}/reject`
- POST `/api/shared-activities/{id}/start`
- GET `/api/shared-activities/{id}`

Communication's `shared_action_proposals[]` remains the Visit/UI projection. Bind:
- `simulation_activity_id` -> Simulation `shared_activities.id`
- `simulation_action_id` -> Simulation citizen job ID after real start

**UI truth rules:**
- proposed/accepted must look nonphysical
- active only after real Simulation job exists
- rejected creates no movement marker/path
- complete observation marker only from Simulation observation ID
- render `radius_m` uncertainty for baseline evidence
- baseline observation does not know material/geology
- visual smoothing may use only the authoritative start/target/timing segment

**Visitor presence:**
`GET /api/visitor/presence`
returns active shared activity/current authoritative x/y during the shared walk.

**Next action:**
Assets can finish the Stage 2 map/proposal/progress presentation without any remaining Simulation dependency.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
