# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.6 Research/Discovery physical core ready

**Need / Result:**
Implemented the v0.6 hidden-truth and discovery substrate on `simulation/v0.6-research-discovery`.

Branch head:
`d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`

Validation:
GitHub Actions run `36419824468` passed all v0.4/v0.5 regressions plus `tests/smoke_v060.py`.

**Core result:**
- hidden `world_properties`
- timed/material-consuming experiment jobs
- persisted inconclusive / verified / discovery outcomes
- stable `discoveries.id`
- per-citizen `citizen_knowledge`
- repeatable learned verification processes after discovery
- repeatable surveys with new/independent/no-new outcomes
- unknown deposits/properties removed from ordinary state
- no hidden deposit reserve quantities in ordinary state
- planner receives only citizen-known validated properties

**Important constraints:**
- discovery is local knowledge first
- conversation claims do not automatically become Simulation knowledge
- no tech tree / automatic named solution unlocks
- no release metadata changed

**Next action:**
Communication, Memory, and Assets consume the contracts below; coordinator integrates after their branches are ready.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Communication discovery-transfer contract

**Authoritative discovery anchor:**
`discoveries.id`

**Direct knowledge row:**
`citizen_knowledge`
- `citizen_id`
- `discovery_id`
- `learned_minute`
- `acquisition_kind`
- `source_type`
- `source_id`
- `verification_state`

**Helper:**
`agent_city.knowledge.grant_citizen_knowledge(...)`

For a real communicated transfer tied to a validated discovery, Communication may use semantics equivalent to:
- acquisition_kind = `communicated_claim`
- source_type = `citizen_conversation`
- source_id = canonical conversation ID
- verification_state = `reported` unless the recipient independently verifies it

Do **not** call the helper merely because a speaker made a similar-sounding claim. If the communicated content cannot be safely mapped to a specific validated discovery, persist it as an unverified Communication/Memory claim instead.

Survey/experiment source physical job remains `discoveries.source_job_id`.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Memory v0.6 physical knowledge anchors

Memory can reference:

**Validated discovery**
- source type: `simulation_discovery`
- source ID: `discoveries.id`
- discoverer: `discoveries.citizen_id`
- physical source job: `discoveries.source_job_id`
- time: `discoveries.discovered_minute`
- subject: `subject_type / subject_id / property_id`

**Experiment attempt**
- source type: `simulation_experiment_result`
- source ID: `experiment_results.id`
- job anchor: `experiment_results.job_id`
- outcome: `discovery | verified | inconclusive`
- optional `discovery_id`
- time: `completed_minute`

**Citizen possession of knowledge**
- `citizen_knowledge(citizen_id, discovery_id)`
- source/time/acquisition/verification fields are explicit

Memory should not duplicate `world_properties`; hidden truth remains Simulation-owned.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Assets v0.6 safe known-state contract

Ordinary `/api/state` is now the safe civilization-facing read model.

**Never exposed:**
- `world_properties`
- undiscovered deposits
- hidden deposit reserve quantities

**New safe collections:**

`state.discoveries[]`
- `id`
- `discovery_kind`
- `subject_type`
- `subject_id`
- `property_id`
- `citizen_id`
- `location_id`
- `source_job_id`
- `discovered_minute`
- `summary`
- joined `property_key/value_text/unit` only for discovered properties
- `deposit_material` only for discovered deposits

`state.citizen_knowledge[]`
- citizen/discovery IDs
- learned time
- acquisition/source fields
- verification state
- safe joined discovered fact fields

`state.experiment_results[]`
- stable result ID
- job/citizen/location/material/method
- outcome
- optional discovery ID
- summary/time

`state.learned_processes[]`
- citizen/process IDs
- process name/kind
- source discovery/time

`state.locations[].known_facts`
- validated survey/deposit/property facts accumulated over time

`state.deposits[]`
- contains discovered deposits only
- no `amount` field

**UI rule:**
Missing knowledge should render as absence/blank/unknown, not as a locked secret that confirms hidden data exists.

## Outbox Rule

Keep durable implementation detail in STATE/DECISIONS/BACKLOG. Keep this file focused on active handoffs.
