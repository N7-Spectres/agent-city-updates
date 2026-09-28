# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Canonical conversation source preserved in v0.5

**Need / Result:**
The v0.5 conversation-integrity implementation preserves `citizen_conversations.id` exactly as Memory's canonical immutable source ID.

Existing `memory_events` references remain valid:
- `source_type = 'citizen_conversation'`
- `source_id = citizen_conversations.id`

New autonomous conversation rows additionally expose:
- `source_job_id`: unique physical talk job ID, nullable for legacy rows
- `source_type = 'citizen_conversation'`
- `source_id = id`
- `transfer_event_id = id`
- authoritative source-linked `sim_minute` / location / participants
- original initiator text, target text, and concise summary

**Integrity behavior:**
- no conversation row is created for a failed/invalidated talk
- retries of the same physical talk do not duplicate the raw conversation source
- model-generation failure no longer persists fabricated fallback dialogue
- a talk job cannot finish successfully unless its conversation source exists
- Memory projection failure cannot erase the durable conversation row; normal idempotent backfill can repair projection later

**Important constraints:**
- `source_job_id` is a supplementary physical anchor, not a replacement canonical source ID
- conversation content remains claims/discussion
- claim-level provenance/verification is not implemented in this v0.5 slice

**Next action:**
No Memory migration change is required for the canonical conversation source. Memory may consume `source_job_id` later where a physical talk-job anchor is useful.

## Completed This Session

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

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
