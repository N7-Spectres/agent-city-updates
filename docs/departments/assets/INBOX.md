# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

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
Communication now exposes a compact shared-action proposal lifecycle for Visit UI on `communication/v0.8-shared-actions-stage2`.

**Visit payload addition:**
`shared_action_proposals[]`

**Proposal shape:**
- `id`
- `proposal_token`
- `citizen_id`
- `visit_id`
- `source_exchange_id`
- `action_kind`
- `label`
- `objective`
- `target`:
  - frame_id
  - x_m / y_m
  - subject_type / subject_id
- `requested_tool_id`
- `status`
- `acceptance_available`
- `simulation_action_id`
- `simulation_status`
- `progress`
- `start_minute / end_minute`
- `observation_ids[]`
- safe `outcome`

**Lifecycle semantics:**
- `proposed`: conversational proposal only, not physical
- `accepted`: visitor accepted, but still not physical unless a Simulation action ID exists
- `started`: real Simulation action exists
- `completed`: Simulation reports completion
- `rejected | failed | cancelled | expired`: no active physical action

**Endpoints:**
- `GET /api/visit/{citizen_id}/shared-actions?visitor=N7&visit_id=<id>`
- `GET /api/shared-actions/{proposal_id}`
- `POST /api/shared-actions/{proposal_id}/accept` with visitor body
- `POST /api/shared-actions/{proposal_id}/reject` with visitor body

The normal `POST /api/talk` response may also include:
- `exchange_id`
- `shared_action_proposal` (object or null)

**Important constraints:**
- render proposed vs started distinctly
- only enable acceptance when `acceptance_available = true`
- do not render target coordinates/subject data beyond this safe object
- no hidden world values
- rejected/failed/expired proposals get no transcript/action fiction
- completed observation markers come from Simulation IDs only

**Next action:**
Use this object for the compact Visit proposal affordance. Final movement progress semantics still depend on Simulation's Stage 2 lifecycle handoff.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
