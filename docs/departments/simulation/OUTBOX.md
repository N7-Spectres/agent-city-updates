# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** World & Simulation session wrapped

**Need / Result:**
The v0.5 physical core and Communication talk-integrity invariant are implemented, tested, documented, and handed off. No additional Simulation implementation is pending in this work session.

**Branch / Validation:**
- `simulation/v0.5-making-building`
- head `773299189d22d214b3376c72b396015a4a7a762e`
- integrated CI run `36372991331` passed all required smoke suites

**Dependencies handed off:**
- Assets received the final `projects` / `project_materials` / `equipment` / extended `structures` contract
- Memory received stable project/job/outcome anchors
- Communication received confirmation that its talk-source invariant is integrated
- COORDINATION records Assets as the remaining active v0.5 department

**Next action:**
Stop Simulation work. Resume only for coordinator merge issues, new inbox requests, or the next milestone.


### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.5 Making & Building physical core ready

**Need / Result:**
Implemented and tested the physical core on `simulation/v0.5-making-building`, head `773299189d22d214b3376c72b396015a4a7a762e`.

Includes:
- persisted fabrication/equipment
- project lifecycle `planned -> reserved -> underway -> complete`
- validated material reservation/consumption
- real completed structure creation
- cargo-capacity equipment
- extraction-speed equipment
- return-energy reserve
- future charger/outpost representation through `structures.provides_charging`
- local coordinate groundwork
- stable job/project physical-event IDs
- Communication's source-linked talk completion invariant

**Files / Interfaces:**
- `agent_city/db.py`
- `agent_city/simulation.py`
- `agent_city/comms.py`
- `agent_city/planner.py`
- `tests/smoke_v050.py`
- `tests/smoke_v050_communication.py`
- state exposed through existing `/api/state`

**Validation:**
GitHub Actions run `36372991331` passed compilation, JS syntax, v0.4 regression smoke, v0.5 simulation smoke, and v0.5 communication-integrity smoke.

**Important constraints:**
- v0.5 construction is settlement-local until explicit project-material transport exists
- local x/y is groundwork, not full free-roam geography
- current fabrication processes are starting workbench processes, not a technology tree
- return/deposit remains an autonomous citizen choice
- no release metadata or `update.json` changed

**Next action:**
Coordinator integrates the branch. Assets can consume the state schema below; Memory can reference durable project/job IDs.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Assets Making & Building state contract

**Need / Result:**
Existing `/api/state` exposes the authoritative physical records.

**Projects — `state.projects[]`:**
- `id`
- `blueprint_id`
- `name`
- `location_id`
- `x_km`, `y_km`
- `status`: `planned | reserved | underway | complete`
- `created_by`
- `created_minute`
- `reserved_minute`
- `started_minute`
- `completed_minute`
- `active_job_id`
- `resulting_structure_id`

**Project materials — `state.project_materials[]`:**
- `project_id`
- `material`
- `required_amount`
- `reserved_amount`

**Equipment — `state.equipment[]`:**
- `id`
- `template_id`
- `name`
- `kind`
- `owner_citizen_id`
- `location_id`
- `condition`
- `extraction_speed_multiplier`
- `cargo_bonus`
- `created_job_id`
- `created_minute`

**Structures — existing `state.structures[]` gains:**
- `location_id`
- `x_km`, `y_km`
- `kind`
- `provides_charging`
- `project_id`

Assets should display these fields, not re-derive capability or completion.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Memory authoritative project/event references

**Need / Result:**
No parallel event table is required.

Use:
- `projects.id` as stable project ID
- `jobs.id` as stable physical transition/action ID
- `jobs.end_minute` as completion time for completed/failed actions
- `jobs.citizen_id` as acting participant
- `jobs.action`, `jobs.target`, `jobs.status`, `jobs.outcome`, `jobs.project_id`
- project lifecycle timestamps/state from `projects`
- `projects.resulting_structure_id` for successful construction output
- `equipment.created_job_id` for fabricated equipment provenance

For multi-citizen physical talk events, `jobs.citizen_id` is initiator and `jobs.target` is the second citizen; `citizen_conversations.source_job_id` anchors the actual transferred exchange.

Legacy completed jobs carry `outcome = legacy_complete` rather than an invented success/failure interpretation.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Communication authoritative physical inputs confirmed

**Need / Result:**
Communication can continue grounding provenance with:
- current minute: `meta.sim_minute`
- citizen physical location: `citizens.location_id`
- co-location: equality of authoritative `location_id`
- traveling state: active job whose `action = travel`
- availability: `active_job_id IS NULL`
- observable physical action/outcome anchor: durable `jobs.id`
- completed time: `jobs.end_minute`
- result: `jobs.status` + `jobs.outcome`

The integrated branch preserves Communication's `citizen_conversations.source_job_id` talk-source invariant.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
