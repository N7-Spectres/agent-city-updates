# World & Simulation — State

_Last updated: 2026-09-28_
_Current published release: v0.7.0_
_Stage 2 unified base: `release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`_
_Active implementation branch: `simulation/v0.8-exploration-stage2`_
_Branch head: `b81c9bb57884727e7a1c769d95ecb27928d1d489`_

## Mission

Own physical truth.

> **The AI may decide intent. The simulation decides reality.**

Stage 2 adds:

> **Conversation may propose shared action. Only Simulation may start and complete it.**

## Stage 1 Foundation Preserved

The branch starts from the unified green Stage 1 integration base.

Preserved:
- persistent hidden planet seed
- `seed_site_local` meter tangent-plane frame
- deterministic hidden terrain/geology
- stable generated deposit bodies
- hidden/public knowledge boundary
- `spatial_observations.id` safe evidence
- all v0.5-v0.7 production/research/provenance/memory/maintenance/talk invariants

## v0.8 Stage 2 — Continuous Local Exploration

### Local Movement Job

New Simulation-owned physical action:

- `local_move`

Core implementation:
- `agent_city/exploration.py::start_local_move(...)`

A local move persists real job fields:
- `spatial_frame_id`
- `start_x_m / start_y_m`
- `target_x_m / target_y_m`
- `path_distance_m`
- `terrain_multiplier`
- `start_minute / end_minute`
- status/outcome

Current local move limit:
- 300 m per move

The planner is given safe nearby movement choices without being shown hidden terrain results.

### Terrain-Aware Physical Cost

Local movement samples deterministic hidden terrain along the straight local path.

Simulation computes:
- geometric distance
- hidden terrain traversal multiplier
- effective traversal distance
- simulated duration
- energy cost

The hidden terrain samples are not exposed merely because they affected movement cost.

### Return-Energy Reserve

Before local movement or shared activity starts, Simulation checks whether the citizen will retain enough energy to reach a known operational charger from the destination plus a safety margin.

The check is coordinate-based against actual charger x/y positions.

### Authoritative In-Transit Position

During an active local/shared movement, current position is derived server-side from the real job:

- start position
- target position
- start/end simulation minute
- current simulation minute

Safe state exposes this as:

`state.citizens[].local_movement`

Fields include:
- job_id
- action
- frame_id
- start x/y
- target x/y
- path distance
- terrain multiplier
- start/end minute
- authoritative x/y
- progress
- elapsed/total/remaining minutes

While movement is active, the citizen's public `position_x_m / position_y_m` in `/api/state` is the server-derived current position.

The persisted base citizen position is updated to the target only when the job completes.

Closing/reopening does not invent a new position because the job and simulation clock are persistent.

## Local Inspection

New autonomous action:

- `local_inspect`

It:
- consumes small real energy
- takes 15 simulated minutes
- records one safe `spatial_observations.id` at the actual coordinate on completion
- stores the resulting observation on `jobs.result_observation_id`

### Baseline Observation Boundary

Stage 2 adds observation `detail_level`.

Ordinary direct/shared walk inspection uses:

- `detail_level = baseline`

Baseline inspection may reveal:
- directly observed terrain class
- elevation
- stable physical body contact ID if physically encountered

Baseline inspection does **not** reveal:
- hidden geology classification
- material identity
- chemistry
- richness
- body geometry

For baseline observations:
- `geology_class = unclassified`
- `material = null`

Stage 1 field/tool observations retain their prior richer field detail where legitimately supported.

No scanner was added.

## Meter-Aware Physical Legality

Stage 2 now makes several older systems respect meter-space.

### Citizen face-to-face talk

Same `location_id` is no longer enough.

Citizens must be within approximately 2 m for face-to-face talk legality.

### Visitor face-to-face access

Visitor/citizen access now also uses meter proximity within a named region.

If both are in Seed Site but 80 m apart, the visit is physically remote.

### Settlement infrastructure

Seed Site workbench/storage/maintenance actions are only offered when the citizen is physically near the Seed Site landmark.

Charging requires an operational charger physically within reach.

### Legacy route compatibility

Legacy named-location routes remain supported.

New real Stage 2 local offsets must return to the landmark before entering a legacy route.

For backward compatibility, old saves/tests that have a legacy `location_id` change without any Stage 2 local-movement history retain the old region-based route behavior.

Visitor route departure requires actual landmark proximity after Stage 2 shared/local movement.

## Shared Visitor + Citizen Physical Activity

New persistent table:

- `shared_activities`

Stage 2 supports one narrow physical type:

- `walk_inspect`

This is intentionally not a generic visitor command system.

### Stable Simulation Action Identity

Authoritative shared physical event/action ID:

- `shared_activities.id`

Related stable links:
- physical citizen job: `citizen_job_id`
- source visitor visit: `source_visit_id`
- source visitor exchange: `source_exchange_id`
- requested runtime equipment: `tool_equipment_id`
- resulting evidence: `observation_id`

### Lifecycle

Simulation lifecycle is explicitly:

`proposed -> accepted -> active -> complete`

A pre-start proposal may also become `rejected`. Failure can be represented separately.

Important:
- `proposed`: intent/proposal only
- `accepted`: visitor acceptance only, **no physical movement**
- `active`: a real Simulation job exists and movement has begun
- `complete`: movement/inspection completed and safe evidence exists

Acceptance and physical start are separate API calls.

### Proposal Validation

A shared proposal validates:
- real visitor presence
- real citizen
- same location
- <= 2 m physical proximity
- citizen availability
- visitor not route-traveling
- Stage 2 shared distance <= 180 m
- supplied source visit belongs to that visitor/citizen
- supplied source exchange belongs to that visitor/citizen/visit
- requested equipment is real, operational, and physically available

Concept art cannot satisfy equipment requirements.

### Start Revalidation

Physical start rechecks:
- accepted visitor identity
- citizen/visitor co-location and proximity
- citizen availability
- visitor travel state
- requested equipment availability
- target local range
- terrain-derived movement cost
- return-energy reserve

Only then does Simulation create the real `shared_local_activity` job.

### Shared Movement

During active shared movement:
- citizen and visitor follow the same authoritative Simulation job progress
- visitor presence exposes the same derived current x/y
- ordinary route travel is blocked
- face-to-face Visit status returns `shared_activity_active`

### Shared Completion

On completion:
- citizen persisted x/y moves to the target
- visitor persisted x/y moves to the same target
- one baseline-safe `spatial_observations.id` is created
- job stores `result_observation_id`
- shared activity stores `observation_id`
- shared activity becomes `complete` with `outcome = success`

## Shared Activity API

Simulation now exposes:

### Propose
`POST /api/shared-activities/propose`

Body:
- visitor
- citizen_id
- target_x_m / target_y_m
- objective
- source_visit_id
- source_exchange_id
- optional tool_equipment_id

Creates proposal only. No movement.

### Accept
`POST /api/shared-activities/{id}/accept`

Body:
- visitor

Transitions:
- proposed -> accepted

No movement.

### Reject
`POST /api/shared-activities/{id}/reject`

Body:
- visitor

Allowed only from `proposed` or `accepted`.

Transitions to `rejected` with no physical movement, no citizen job, and no observation.

### Start
`POST /api/shared-activities/{id}/start`

Body:
- visitor

Revalidates physical conditions and, if legal:
- accepted -> active
- creates real citizen job

### Status
`GET /api/shared-activities/{id}`

Returns authoritative Simulation lifecycle/status and active movement progress when present.

## Safe State Read Model

`/api/state` now includes:

- existing safe Stage 1 spatial state
- citizen `local_movement`
- active jobs with real movement fields
- `shared_activities[]`

`shared_activities[]` may include:
- id
- visitor/citizen
- activity type/objective
- frame/start/target coordinates
- lifecycle times/status
- source visit/exchange IDs
- tool equipment ID
- citizen job ID
- observation ID
- outcome/failure reason
- active movement payload when status = active

No hidden world seed/body geometry/richness is added to the public read model.

## Legacy Travel

Existing named route travel remains intact and all historical travel smoke tests pass.

Stage 2 does not replace the route network or add globe travel.

## Migration

Stage 2 migration is additive.

New schema:
- `shared_activities`
- movement/source/result fields on `jobs`
- `spatial_observations.detail_level`

No save reset is required.

## Validation

Final Stage 2 code passed GitHub Actions:

`36456647323`

Passed:
- Python compilation
- JavaScript syntax
- every v0.4-v0.7 regression suite
- all four v0.8 Stage 1 department smokes
- `tests/smoke_v080_stage2.py`

A first run correctly exposed a v0.5 legacy-location compatibility issue; the fix preserves legacy route semantics only when no real Stage 2 local offset exists.

The final runtime hardening added a visitor-owned pre-start rejection transition and re-ran the complete regression matrix successfully. The final branch commit only restored the release-only workflow.

## Status

World & Simulation Stage 2 physical exploration/shared-activity core is ready for dependent department integration/review.

No `update.json` or release metadata was changed.


## Stage 2 Session Close

World & Simulation Stage 2 implementation is complete.

Authoritative handoff:
- branch: `simulation/v0.8-exploration-stage2`
- head: `b81c9bb57884727e7a1c769d95ecb27928d1d489`
- unified Stage 1 base: `017b417386f4f4e0f957dfb66285431223283739`
- final CI: `36456647323`

Dependent contracts are being routed to Communication, Memory, and Assets. Simulation should resume only for integration conflicts or a new coordinator request.
