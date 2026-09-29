# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: READY / FIRST v0.9 DEPENDENCY

**Subject:** v0.9 Stage 1 — Causal Memory Spine

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`
- `docs/departments/COORDINATION.md`

**Locked principle:**

> Persistent behavior must have a traceable history.

Memory is causal infrastructure for v0.9, not biography flavor.

**Stage 1 goal:**
Define the smallest durable + bounded memory contract that can support persistent plans, self-assessment, place meaning, later experience/specialization, and social continuity without global omniscience or context flooding.

**Required audit/design:**
- existing `memory_events` / social / spatial / maintenance memory sources and stable IDs
- citizen-scoped ownership and provenance preservation
- durable archive vs active recall
- salience and retrieval priority
- reinforcement/linking of related experiences without duplicating every event
- meaningful aging / reduced recall priority without rewriting history
- bounded retrieval packet for planner decisions
- retained success/failure experience
- retained visitor/shared-action continuity only from real source-linked encounters
- hooks needed for unfinished persistent plans
- hooks needed later for self-assessment and place-specific meaning

**Hard locks:**
- no global reputation score
- no identity/class fields
- no fabricated memories to justify present behavior
- no skill gain from conversation alone
- no arbitrary habit/custom inference in Stage 1
- hidden Simulation truth never enters Memory merely because it exists
- active recall may fade; durable source history must not be rewritten

**Stage 1 acceptance direction:**
- a citizen can retrieve why an unfinished plan still matters after unrelated work/time passes
- the reason is traceable to real source-linked history
- another citizen without that history does not receive it
- repeated related experience can become more retrievable without copying an unbounded transcript
- low-value old events can fall out of active context while remaining in durable archive
- visitor continuity appears only when real visits/exchanges/shared actions support it

**Deliverables:**
1. Memory Stage 1 contract/design.
2. Minimal schema/API changes only if justified by the audit.
3. Focused smoke coverage for provenance, bounded recall, and continuity.
4. Explicit handoff to Simulation describing the plan/history source interface.
5. Explicit handoff to Communication describing safe perspective/social retrieval.
6. Update STATE / DECISIONS / BACKLOG / OUTBOX.

Do not publish `update.json`.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 2 — Exploration memory enters real planning/dialogue

**Unified Stage 1 base:**
- `release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`
- combined CI `36453177128` — PASS
- create/use: `memory/v0.8-exploration-stage2` if runtime changes are needed

**Stage 2 goal:**
Use the Stage 1 spatial-memory foundation now that real local movement/shared inspection will begin producing observations.

**Required scope:**
- consume Simulation Stage 2 exploration/shared-action source IDs when handed off
- wire bounded spatial memory into citizen planning where it materially helps:
  - current local area
  - nearby previously observed stable subjects
  - previous observations of the same deposit/body
- wire bounded spatial continuity into visitor/citizen dialogue only for facts that citizen personally observed or legitimately received
- preserve `radius_m`/precision limits in model-facing text
- same-body repeat observations should strengthen continuity without flooding context
- meaningful shared exploration may become a durable social/spatial experience for the participating citizen; do not grant it to bystanders
- visitor participation may be remembered as a shared event only when a real Simulation shared-action record exists
- keep generic research/location knowledge and spatial-observation memory distinct where semantics differ
- remain conservative about every-meter movement; movement ticks are not memories
- expose a minimal safe consumer view for Assets only if useful for known-map markers/history

**Do NOT:**
- ingest planet seed or generated-deposit hidden geometry
- create global omniscient exploration memory
- infer exploration from chat agreement
- publish `update.json`

**Acceptance direction:**
- a citizen returning near a previously observed deposit can receive bounded memory of that prior encounter
- a citizen who never observed/heard about the deposit does not
- real shared visitor exploration can become source-linked continuity
- context remains bounded under repeated movement/inspection

**Next action:**
Consume Simulation/Communication Stage 2 contracts, implement only evidence-backed runtime changes, add focused smoke coverage, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


**Result:**
Implemented and tested on `memory/v0.8-exploration-stage2` @ `306a9ef4329ab81afa5912846333a1d9782ee9be`.

CI `36455394456` passed the full unified Stage 1 regression matrix plus `tests/smoke_v080_memory_stage2.py`.

Delivered bounded nearby spatial context for planning/dialogue, citizen-scoped spatial Memory API, and source-linked completed shared-exploration continuity from Simulation `shared_activities`. Proposal/acceptance alone never becomes physical exploration Memory.


### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 1 — Spatial knowledge / discovery continuity audit

**Runtime base:**
- shipped `release-v0.7.0` / `d81a85bf03b69b969532016f59bbbed2233949ee`
- create `memory/v0.8-spatial-knowledge-stage1` only if runtime code is justified by the final Simulation contract

**Stage 1 goal:**
Prepare Memory for a world where discoveries happen at continuous coordinates and stable generated deposits/places can be encountered again.

**Required audit/design:**
- determine how existing `memory_events`, discovery IDs, and provenance can reference:
  - coordinate-based observations
  - stable generated deposit/body IDs
  - samples/scans
  - newly named places later
- preserve per-citizen knowledge isolation
- a citizen should remember where they personally observed/discovered something without receiving raw hidden seed truth
- repeated encounters with the same physical deposit should connect to the same stable subject rather than look like unrelated discoveries
- avoid flooding memory with every meter walked or every low-value scan
- define salience rules for spatial observations and exploration milestones
- keep coordinate precision bounded to what the observation/tool actually supports
- maintain strict separation between hidden Simulation world truth and remembered/communicated knowledge

**Dependency:**
Simulation Stage 1 must provide the stable coordinate/deposit/observation source contract before Memory adds source-specific runtime ingestion.

**Do NOT:**
- invent a global omniscient map memory
- copy hidden chunks/seed data into Memory
- create speculative schema just because continuous coordinates exist
- publish `update.json`

**Next action:**
Audit now, consume Simulation's handoff when ready, implement only minimal justified runtime support, add focused smoke coverage if code changes, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.7.0 final Memory runtime pass required before integration

Handoff review found the maintenance-memory policy is complete, but runtime ingestion/read-model implementation was intentionally deferred after the prior wrap. Simulation's stable `maintenance_events.id` contract is now available.

**Finish before coordinator integration:**
- create/use `memory/v0.7-maintenance-history` from shipped v0.6.0
- idempotently ingest meaningful `maintenance_events` into existing `memory_events`
- grant memory only through a valid experience/information path, beginning with actor/serviced citizen where justified
- retain Simulation source/event/job IDs plus before/after/material/outcome metadata
- add bounded retrieval by citizen and maintenance target
- expose only a minimal consumer read model if Assets/History benefits
- add a v0.7 Memory smoke proving passive wear does not flood durable memory
- preserve all v0.4-v0.6 knowledge/provenance/social-memory behavior
- update STATE/OUTBOX/COORDINATION with final branch head and green validation

Do not infer repairs from condition deltas or dialogue. No `update.json` changes.

**Result:** Implemented/tested on `memory/v0.7-maintenance-history` @ `dda84cdf6a46fbd79e48ce9eea59adce363c5714`; CI `36434785293` passed the full Memory regression matrix. Ready for coordinator integration.


### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** v0.7 stable maintenance event anchors for Memory

**Need / Result:**
Simulation's v0.7 maintenance branch is ready: `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`.

CI run `36429729279` passed all v0.4-v0.7 runtime smoke suites.

For durable maintenance memory use:

- source type recommendation: `simulation_maintenance_event`
- source ID: `maintenance_events.id`
- physical job: `maintenance_events.job_id`
- actor: `citizen_id`
- target: `target_type / target_id`
- `event_type`
- `before_value / after_value`
- `materials_json`
- `outcome`
- `sim_minute`
- `summary`

Current event types:
- `chassis_service`
- `battery_replacement`
- `equipment_service`
- `structure_service`

Jobs also expose `maintenance_event_id`.

**Memory policy guidance:**
Routine per-use wear does not get its own maintenance-event row by design. Prefer remembering completed service/repair/replacement, critical failures/shortages, and major threshold events rather than every 0.3% condition change.

**Important constraints:**
- Memory references validated Simulation events; it does not create wear or repair
- a History threshold message is not a substitute for a completed maintenance event when recording repair success
- preserve bounded retrieval and avoid a maintenance chore diary

**Next action:**
The stable event anchors are available now; Memory can implement/finish its v0.7 maintenance-history ingestion if desired.

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.7.0 — Maintenance memory/history support

**Runtime base / branch:**
- base: `release-v0.6.0` / immutable commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- create/use a branch only if runtime code is needed: `memory/v0.7-maintenance-history`

**Need / Result:**
Support long-term maintenance continuity without inventing physical wear or flooding context with routine service noise.

**Required scope:**
- consume stable Simulation maintenance/repair event IDs when available
- distinguish routine minor upkeep from meaningful maintenance events
- preserve important repair/failure history where it could affect future planning or place/equipment significance
- do not infer damage from conversation
- keep bounded context
- do not add noisy "maintenance memories" for every tiny condition decrement
- consider what minimal read model Assets may need for Citizen/History views
- preserve v0.6 knowledge/provenance/social memory behavior

**Important constraints:**
- Simulation owns condition/damage/repair truth
- Memory records selected experience/history only
- no global hidden diagnostics in citizen context
- no `update.json` changes

**Next action:**
Audit current Memory event model, wait for/use Simulation maintenance anchors as needed, implement only minimal evidence-driven changes, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** v0.6 upstream contracts resolved

**Result:**
Simulation and Communication final v0.6 interfaces have been received and recorded in Memory STATE/DECISIONS/BACKLOG/OUTBOX. Memory is no longer waiting on a department dependency and is ready for coordinator integration.


### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.6.0 — Persistent location knowledge and bounded research memory

**Runtime base / branch:**
- base: `release-v0.5.0` / immutable commit `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- create/use a branch only if runtime code is needed: `memory/v0.6-location-knowledge`

**Need / Result:**
Extend Memory only as needed to preserve what each citizen has actually learned about locations/materials/research while keeping context bounded and claims separate from verified physical facts.

**Required scope:**
- consume Simulation discovery IDs and Communication provenance once handed off
- support durable per-citizen knowledge of discovered location facts
- retain source/time for meaningful facts
- support bounded retrieval of what a citizen knows about a location/material/process
- allow a location summary to become richer over time as new validated knowledge arrives
- keep unverified conversation claims separate from verified discoveries
- avoid duplicating Simulation's hidden truth tables
- preserve v0.4/v0.5 social memory and idempotent migrations

**Important constraints:**
- Memory records knowledge/experience; Simulation owns physical truth
- missing knowledge is allowed and expected
- do not create a global shared encyclopedia merely because one citizen learned something
- no speculative schema if existing `memory_events` can safely represent the needed links
- no `update.json` changes

**Next action:**
Audit current schema, implement only what the v0.6 knowledge model genuinely requires, and hand Assets the safe read model for Citizen/Location detail surfaces.


### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.5.0 memory support for projects and conversation source continuity

**Result:**
Memory's project-continuity audit is complete; Communication has now delivered the final conversation-source shape. Remaining project outcome hooks still depend on Simulation's stable project/event IDs.

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Final audit found stable Simulation physical anchors

**Need / Result:**
Inspection of finished `simulation/v0.5-making-building` shows the physical references Memory requested are available in the branch, pending coordinator integration.

Useful stable anchors:
- `projects.id` — durable project identity
- `projects.status` plus created/reserved/started/completed simulation minutes
- `projects.created_by`
- `projects.resulting_structure_id`
- `jobs.id` — durable physical action/outcome reference
- `jobs.citizen_id`, `action`, `target`, `end_minute`, `status`, `outcome`, `project_id`
- fabricated `equipment.created_job_id`
- built `structures.project_id`

Simulation's smoke test explicitly verifies completed jobs retain stable IDs and non-null outcomes.

**Important constraints:**
- these become authoritative only from the integrated Simulation runtime
- project discussion remains sourced to conversation and must not be upgraded into completion
- Communication claim-level provenance remains future depth

**Next action:**
No Memory schema change is required now. After integration, these IDs can back future physical project/outcome memories.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Final authoritative v0.5 project/outcome anchors

**Need / Result:**
Simulation's final integrated branch confirms no parallel physical-event table is needed.

Use:
- `projects.id` as stable project identity
- `projects.status` and lifecycle timestamps for authoritative project state
- `jobs.id` as stable physical action/outcome identity
- `jobs.citizen_id`, `action`, `target`, `end_minute`, `status`, `outcome`, `project_id`
- `projects.resulting_structure_id` as construction output
- `equipment.created_job_id` as fabrication provenance
- `citizen_conversations.source_job_id` as the physical talk-job anchor for actual transferred exchanges

New physical job outcomes include `success`, `failed`, and `no_yield`. Pre-v0.5 completed jobs are deliberately backfilled as `legacy_complete` rather than assigned invented richer semantics.

Integrated branch head: `773299189d22d214b3376c72b396015a4a7a762e`.
Integrated CI run: `36372991331` passed all three smoke suites.

**Important constraints:**
- conversation/project discussion remains a claim or intention until Simulation records a physical transition
- do not reinterpret `legacy_complete` as a newly verified detailed outcome
- Memory references physical state; it does not create it

**Next action:**
No additional Memory runtime work is required for this v0.5 slice.

### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** v0.6 Assets citizen/location knowledge read model

**Need / Result:**
Assets has built placeholder-safe Citizens character sheets and Locations field notebooks. To finish their knowledge sections safely, Assets needs Memory's bounded consumer read model rather than direct access to hidden/global memory state.

**UI consumers need:**
- per-citizen bounded known facts relevant to:
  - locations
  - materials/resources
  - research/experiment results
  - learned processes when legitimately known
- source/time/age metadata that is safe to show
- distinction between verified discovery/observation and remembered communicated claim
- location-oriented summaries that can grow over time without becoming a global omniscient encyclopedia
- stable subject/source IDs where already natural to the model

**Important constraints:**
- missing knowledge is expected and should render as absence, not a locked secret
- one citizen's knowledge must not automatically populate every citizen sheet
- Assets will not promote conversation summaries into verified facts
- keep payload bounded for UI and model-context safety

**Next action:**
When Memory's v0.6 read model is stable, send Assets the exact field/endpoint shape to consume in the Citizens and Locations views.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Final v0.6 Simulation discovery/result IDs for Memory

**Need / Result:**
Simulation's v0.6 branch is ready: `simulation/v0.6-research-discovery` @ `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`. CI run `36419824468` passed all regressions + v0.6 research smoke.

Memory may use these stable physical anchors:

**Validated discovery**
- source_type recommendation: `simulation_discovery`
- source_id: `discoveries.id`
- `discoveries.citizen_id`
- `discoveries.source_job_id`
- `discoveries.discovered_minute`
- `discovery_kind`
- `subject_type / subject_id / property_id`
- `summary`

**Experiment attempt/result**
- source_type recommendation: `simulation_experiment_result`
- source_id: `experiment_results.id`
- job anchor: `experiment_results.job_id`
- outcome: `discovery | verified | inconclusive`
- optional `discovery_id`
- `completed_minute`

**Citizen possession of validated knowledge**
- `citizen_knowledge(citizen_id, discovery_id)`
- learned time
- acquisition kind
- source type/source ID
- verification state

**Important constraints:**
- do not duplicate or read hidden `world_properties`
- one citizen's knowledge is not a global encyclopedia
- direct discovery is verified physical knowledge
- communicated claims remain claim/provenance records unless Communication safely ties them to a validated discovery

**Next action:**
Simulation IDs are stable enough for Memory's v0.6 branch to consume/integrate. No further Simulation schema dependency remains.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.6 provenance receipts ready for Memory

**Need / Result:**
Communication implemented recipient-local provenance records on `communication/v0.6-knowledge-provenance`.

New table: `information_receipts`.

**Important fields:**
- `recipient_id`
- `subject_type`, `subject_id`
- `topic`, `value_text`
- `channel`
- `source_actor_id`
- `origin_event_type`, `origin_event_id`
- `transfer_event_type`, `transfer_event_id`
- `source_conversation_id`
- `observed_at_sim_minute`
- `received_at_sim_minute`
- `assertion_kind`
- `verification`
- unique `source_key`

**Semantics:**
- Simulation-grounded observations/results are `validated_observation + verified`
- face-to-face transferred assertions are `speaker_claim + unverified`
- conversation claim text must be verbatim text actually present in the attributed speaker's durable transcript
- the claim reaches only the other conversation participant
- retelling never promotes a claim to verified
- legacy conversation summaries are not backfilled into precise claims

Communication also exposes a low-level:
- `GET /api/knowledge/{citizen_id}`

Your existing v0.6 Memory endpoints remain the preferred bounded consumer read model for Citizens/Locations UI. Communication's endpoint is provenance-oriented and should not replace Memory's retention/retrieval layer.

**Important constraints:**
- keep per-citizen knowledge separate
- do not merge receipts into a global shared encyclopedia
- preserve verified vs unverified semantics
- later contradiction/reliability derivation should preserve historical claim + later evidence rather than rewriting history

**Branch / tests:**
- Communication head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- CI: `36421263078`

**Layering note:**
Simulation `agent_city/knowledge.py` remains authoritative for validated discoveries/current validated citizen knowledge. Communication `agent_city/provenance.py` supplies immutable receipt/claim provenance beneath Memory's bounded read model.

**Next action:**
During coordinator integration, map/consume these receipts as the Communication provenance source beneath Memory's bounded read model. Communication is no longer blocking the v0.6 Memory contract.



### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.8 Stage 1 stable spatial observation/subject contract

**Need / Result:**
Simulation Stage 1 is complete on `simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`.

Use only validated safe spatial records.

**Canonical source:**
- source_type recommendation: `simulation_spatial_observation`
- source_id: `spatial_observations.id`

Fields:
- observer_id
- source_job_id
- observation_kind
- frame_id
- x_m / y_m
- radius_m
- observed_minute
- terrain_class / elevation_m / geology_class
- optional stable deposit_id/material
- summary

**Stable deposit subject IDs:**
- legacy bodies retain `dep_*`
- procedural bodies use deterministic `gdep_*`
- body identity is independent of who discovered it

**Coordinate precision contract:**
Stored x/y decimals are computational precision only.
Epistemic/measurement precision comes from:
- `radius_m`
- source action/tool semantics

Do not infer finer knowledge from decimal places.

**Never ingest:**
- planet_seed
- generated_deposits
- hidden body geometry
- hidden richness
- raw hidden-world query payloads

**Next action:**
Memory can now complete its Stage 1 spatial continuity audit/ingestion decision. No additional Simulation subject-ID dependency remains.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication Stage 2 proposal/source semantics ready

**Need / Result:**
Communication's final Stage 2 source chain is aligned to Simulation.

**Distinct identities:**
- `conversations.id` — durable visitor/citizen exchange where shared activity was proposed
- `shared_action_proposals.id` — Communication intent/projection identity
- `shared_activities.id` — canonical Simulation shared-activity identity
- `jobs.id` / `shared_activities.citizen_job_id` — actual physical movement job after acceptance
- `spatial_observations.id` / `shared_activities.observation_id` — validated spatial evidence at completion

**Memory semantics:**
- conversation/proposal = intention/social continuity
- Simulation `status='proposed'` = physically validated proposal, still not movement
- Simulation active job = shared activity actually underway
- successful completed `shared_activities.id` = physical/social exploration event anchor
- linked `spatial_observations.id` = separate physical evidence anchor

Do not rewrite proposal/acceptance history into completion.

**Visitor text parsing:**
Communication only turns explicit meter/cardinal movement language into a candidate target and Simulation must validate/persist it before any structured proposal exists.

**Next action:**
Your current `source_type='simulation_shared_activity'` / `source_id=shared_activities.id` completed-event plan matches the final contract.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Final Stage 2 physical exploration IDs confirmed

**Need / Result:**
Final Simulation Stage 2 branch:
`simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`

Final CI:
`36456647323` — PASS.

Your existing Stage 2 Memory source model matches the final Simulation contract.

**Physical source chain:**
- local move job: `jobs.id` with `action='local_move'`
- local inspection evidence: `jobs.result_observation_id` -> `spatial_observations.id`
- shared physical/social event: `shared_activities.id`
- shared citizen job: `shared_activities.citizen_job_id`
- shared observation evidence: `shared_activities.observation_id`

**Completed shared-memory validity remains:**
- `status='complete'`
- `outcome='success'`
- non-null completed minute
- non-null observation ID

**New final rejection semantics:**
A `shared_activities.status='rejected'` row is pre-start intention history only:
- no physical job
- no movement
- no observation
- never becomes completed shared-exploration memory

Baseline Stage 2 observations remain:
- `detail_level='baseline'`
- material null
- geology unclassified
unless a later earned capability produces richer evidence.

**Next action:**
No additional Memory dependency remains. Preserve your current physical-event/evidence separation during coordinator integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
