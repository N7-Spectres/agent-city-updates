# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.8 Stage 1 World & Simulation session wrapped

**Need / Result:**
The seeded spatial-world foundation is implemented, tested, documented, and fully handed off.

**Branch / validation:**
- `simulation/v0.8-seeded-world-stage1`
- head `7473b6612ea23cf8d22b31176149da188476690e`
- CI `36449582788` passed the full v0.4-v0.7 regression chain plus Stage 1 Simulation smoke

**Handoffs complete:**
- Communication received coordinate/observation/shared-action boundary contract
- Memory received safe spatial evidence/subject/precision contract
- Assets received safe spatial frame/position/observation read model
- COORDINATION now shows all Stage 1 departments ready/reviewable and coordinator review as the only remaining dependency

**Next action:**
Stop Simulation work. Resume only for coordinator review conflicts, a new inbox request, or authorized Stage 2 work.


### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.8 Stage 1 seeded spatial foundation ready

**Need / Result:**
Implemented/tested on `simulation/v0.8-seeded-world-stage1`.

Branch head:
`7473b6612ea23cf8d22b31176149da188476690e`

Runtime validation:
GitHub Actions `36449582788` passed Python/JS checks, the complete v0.4-v0.7 regression suite, and `tests/smoke_v080_stage1.py`. The only later commit restored the release-only workflow.

Delivered:
- persistent hidden planet seed
- deterministic meter-scale hidden terrain/geology
- stable spatially extended generated deposit bodies
- legacy landmark/deposit additive migration
- meter positions for citizens/locations/structures/projects/visitors
- validated safe spatial observation records
- Simulation-owned hidden-query + local-observation contracts
- strict safe/hidden state separation

**Important constraints:**
- no scanner/free-roam/globe renderer added
- hidden seed/body geometry remains hidden
- no new technology granted
- no release metadata changed

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Communication v0.8 Stage 1 spatial/shared-action contract

**Safe physical coordinates:**
- citizens: `position_x_m / position_y_m`
- locations: `x_m / y_m`
- visitor presence: `x_m / y_m`
- frame: `seed_site_local`, meters, +x east, +y north

**Stable physical observation anchor:**
- `spatial_observations.id`

Safe observation fields:
- observer ID
- optional source job ID
- observation kind
- frame ID
- x/y
- radius
- simulation minute
- terrain class/elevation/geology class
- optional stable deposit ID/material
- summary

**Critical grounding boundary:**
- visitor/citizen speech about an unvalidated coordinate/material/terrain detail remains a claim
- hidden query output is not communication evidence
- a stable generated deposit ID becomes a legitimate physical subject only after a validated observation/action exposes it
- Stage 1 does not implement visitor-linked shared physical actions

**Future shared-action minimum:**
Communication may later request a Simulation-owned action with:
- visitor identity
- citizen identity
- current co-location
- proposed local objective/direction/point
- conversation source ID

Simulation must decide:
- whether action exists/is legal
- participants
- path/point
- duration
- energy/tool needs
- outcome/observation IDs

Chat agreement alone must not move anyone or create discovery.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Memory v0.8 Stage 1 spatial source contract

Use safe validated observations only.

Recommended source:
- source type: `simulation_spatial_observation`
- source ID: `spatial_observations.id`

Fields:
- observer ID
- source job ID
- observation kind
- frame ID
- x/y
- `radius_m`
- observation minute
- terrain/elevation/geology observation
- optional stable deposit ID/material
- summary

Stable deposit subject:
- `deposit_id` when present
- may be a legacy `dep_*` ID or a procedural `gdep_*` ID

Do **not** ingest:
- `planet_seed`
- `generated_deposits`
- hidden richness
- hidden body geometry
- raw `query_hidden_world` output

Coordinate decimals do not imply measurement precision; preserve `radius_m` and source provenance.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Assets v0.8 Stage 1 safe spatial read model

Ordinary state safely exposes:

`state.spatial_frame`
- id = `seed_site_local`
- units = meters
- origin = `seed_site`
- frame type = local tangent plane
- x axis = east
- y axis = north
- global mapping = not yet assigned

Existing state rows now carry safe meter anchors:
- locations: `x_m / y_m`
- citizens: `position_x_m / position_y_m`
- structures: `x_m / y_m`
- projects: `x_m / y_m`
- visitor presence endpoint: `x_m / y_m`

`state.spatial_observations[]` exposes only validated observations.

**Do not render/infer:**
- planet seed
- generated deposit table
- hidden deposit center/axes/richness
- undiscovered procedural resources
- arbitrary continuous travel paths

**Important Stage 1 limitation:**
Legacy route travelers remain at the origin coordinate during travel and snap to the destination coordinate on validated arrival. Continuous interpolation is Stage 2.

Assets may prepare architecture for continuous-world rendering, but must not visually invent intermediate physical positions yet.

## Outbox Rule

Keep durable architecture/rules in STATE/DECISIONS/BACKLOG. Keep this file focused on active handoffs.
