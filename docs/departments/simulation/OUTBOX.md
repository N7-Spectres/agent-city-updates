# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Stage 2 rejection lifecycle hardening

**Need / Result:**
Added a visitor-owned nonphysical reject transition for Simulation shared activities.

Endpoint:
- `POST /api/shared-activities/{id}/reject`

Allowed only from:
- `proposed`
- `accepted`

Result:
- status/outcome become `rejected`
- no physical job
- no coordinate change
- no observation

Final branch head is `b81c9bb57884727e7a1c769d95ecb27928d1d489`.
Final full regression run `36456647323` passed.


### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.8 Stage 2 local exploration/shared physical activity ready

**Need / Result:**
Implemented/tested on `simulation/v0.8-exploration-stage2`.

Final branch:
`b81c9bb57884727e7a1c769d95ecb27928d1d489`

Final runtime validation:
`36456647323` passed all v0.4-v0.7 regressions, all Stage 1 department smokes, and `tests/smoke_v080_stage2.py`.

Delivered:
- authoritative local meter movement jobs
- hidden-terrain-derived duration/energy
- coordinate return-energy reserve
- server-derived in-transit positions
- baseline-safe local inspection
- stable observation IDs
- meter-aware talk/visit/infrastructure legality
- Simulation-owned shared proposal/accept/start/status lifecycle
- explicit visitor acceptance separate from physical start
- shared visitor+citizen walk/inspect
- stable `shared_activities.id`, citizen job ID, source visit/exchange IDs, and observation ID
- additive migration

**Important constraints:**
- no scanner
- no globe travel
- no chat-started movement
- no concept-art equipment capability
- hidden seeded truth remains hidden
- no release metadata changed

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Communication Stage 2 physical shared-action contract

Communication proposal identity remains separate from Simulation physical identity.

**Canonical Simulation action ID:**
- `shared_activities.id`

Communication should store that value in its:
- `shared_action_proposals.simulation_action_id`

**Simulation lifecycle:**
- `proposed`
- `accepted`
- `active`
- `complete`
- `failed` when applicable

Suggested Communication UI mapping:
- Simulation `active` -> Communication `started`
- Simulation `complete` -> Communication `completed`

**Source links on Simulation shared action:**
- visitor
- citizen_id
- source_visit_id
- source_exchange_id
- optional tool_equipment_id

**Physical links:**
- citizen_job_id
- observation_id
- outcome / failure_reason

**Endpoints:**
- POST `/api/shared-activities/propose`
- POST `/api/shared-activities/{id}/accept`
- POST `/api/shared-activities/{id}/start`
- GET `/api/shared-activities/{id}`

Proposal validates source visit/exchange ownership.

Acceptance changes intent only.

Start revalidates physical state and creates the real job.

**Movement status:**
Active payload includes real movement:
- job_id
- start/target x/y
- path_distance_m
- terrain_multiplier
- start/end minute
- current server-derived x/y
- progress
- elapsed/remaining minutes

**Observation:**
Successful walk/inspect completion sets:
- `observation_id`
- job `result_observation_id`

**Communication follow-up needed:**
Now that local movement exists, update `visible_citizens`/grounded current visibility to use meter proximity, not only `location_id`.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Memory Stage 2 physical exploration source contract

Use:
- local movement action source: completed `jobs.id` where action = `local_move`
- local inspection evidence: `jobs.result_observation_id` / `spatial_observations.id`
- shared exploration social/physical event: `shared_activities.id`
- shared citizen physical job: `shared_activities.citizen_job_id`
- shared evidence: `shared_activities.observation_id`

A successful shared exploration memory is valid only when:
- status = `complete`
- outcome = `success`
- completed_minute is non-null
- observation_id is non-null

Preserve proposal/acceptance as intention/provenance, not completed exploration.

Baseline observations have:
- `detail_level = baseline`
- material = null
- geology_class = unclassified
unless later real capability supports richer observation.

Do not turn each interpolated movement tick into memory.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Assets Stage 2 authoritative movement/shared read model

**Citizen movement**
`state.citizens[].local_movement`

Fields:
- job_id / action
- frame_id
- start_x_m / start_y_m
- target_x_m / target_y_m
- path_distance_m
- terrain_multiplier
- start_minute / end_minute
- current authoritative x_m / y_m
- progress
- elapsed_minutes / total_minutes / remaining_minutes

During active movement, citizen `position_x_m/y_m` in state already contains the current server-derived position.

**Shared activity**
`state.shared_activities[]`

Canonical action ID:
- `id`

Lifecycle:
- proposed
- accepted
- active
- complete / failed

Links:
- citizen_job_id
- source_visit_id / source_exchange_id
- tool_equipment_id
- observation_id
- outcome / failure_reason

Active shared rows include `movement` with the same authoritative progress shape.

**Visitor presence**
`GET /api/visitor/presence` now includes:
- shared_activity_id
- shared_activity
- current x_m/y_m derived from the active shared movement

**Validated observations**
`state.spatial_observations[]` now includes `detail_level`.

Baseline walk/inspect:
- material null
- geology unclassified
- use radius_m for uncertainty/extent

**Rendering rule:**
Visual smoothing may interpolate only the real Simulation start/target/timing segment. Do not invent a different path or hidden terrain features.

## Outbox Rule

Keep durable architecture/rules in STATE/DECISIONS/BACKLOG. Keep this file focused on active handoffs.
