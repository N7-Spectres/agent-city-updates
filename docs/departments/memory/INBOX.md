# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

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


_None currently._

## Completed This Session

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

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
