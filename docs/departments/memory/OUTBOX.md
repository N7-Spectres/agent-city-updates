# Memory & Social — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** v0.9 recall-bound practice interpretation surface ready

**Branch / validation:**
- `memory/v0.9-causal-memory-stage1`
- head `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`
- CI `36607115487`

**New safe model-facing API:**
- `practice_recall_snapshot_for(...)`
- `practice_recall_context_for(...)`

This keeps present self-assessment/teaching behind owner-scoped Memory aging/salience while leaving the full Simulation `practice_events` ledger available for objective diagnostics/history.

The API intentionally omits internal recall score and reinforcement count.

**Compatibility review result:**
Communication's current final branch still uses the full practice ledger directly in model-facing self-assessment/teaching and renders numeric `reinforcement_count` in recognition text. A blocking correction request is in Communication INBOX and `COORDINATION.md`.

**Next action:**
Communication patches those two model-facing paths, reruns its v0.9 smoke, then coordinator may assemble Memory + Simulation + Communication Stage 1.


### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** v0.9 Stage 1 Causal Memory Spine ready

**Need / Result:**
Memory's first v0.9 dependency is complete.

**Branch / validation:**
- `memory/v0.9-causal-memory-stage1`
- head `1394261f72d4fc5df7d41e065cd157350fee2785`
- CI `36598971733`

**Delivered:**
- durable archive remains `memory_events`
- additive `memory_event_facets` index
- bounded owner-scoped causal recall
- source-labelled active recall context
- aging that lowers recall priority without rewriting history
- reinforcement from repeated related source-backed experiences
- explicit plan/place continuity facet hook
- pinned `memory_event_id` support for unfinished-plan reasons
- repeated unverified claims remain unverified
- `tests/smoke_v090_memory_stage1.py`
- durable design contract at `docs/departments/memory/V090_CAUSAL_MEMORY_CONTRACT.md`

**Simulation handoff:**
Persistent plans should store stable initiating/revision `memory_event_id` references. Those IDs can be pinned during recall so old reasons remain accessible without turning the plan into a script.

**Communication handoff:**
Recall preserves verification and perspective. Repeated experience may support statements like "I've done this several times"; repeated claims do not become truth, and no expert/title/reputation is created.

**Hard boundaries:**
- no roles/classes
- no public recall/reputation score
- no global memory
- no fabricated causal history
- no skill from conversation
- no hidden Simulation truth ingestion
- no `update.json` changes

**Next action:**
Simulation can now finalize Stage 1 persistent-plan/runtime implementation from this contract. Communication can proceed with its perspective-safe recognition/self-assessment design audit.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.8 Stage 2 exploration Memory ready for integration

**Need / Result:**
Completed Memory's Stage 2 exploration continuity slice.

**Branch / validation:**
- `memory/v0.8-exploration-stage2`
- final head `306a9ef4329ab81afa5912846333a1d9782ee9be`
- green CI `36455394456`

**Delivered:**
- nearby retained exploration memory enters citizen planning
- nearby retained exploration memory enters visitor dialogue
- current authoritative spatial grounding remains separate from historical Memory
- citizen-scoped `GET /api/memory/spatial/{citizen_id}`
- new `agent_city/exploration_memory.py`
- completed shared visitor exploration becomes source-linked citizen continuity only from Simulation `shared_activities`
- proposal/acceptance/active states are not physical completion memories
- visitor/visit/exchange/job/observation provenance retained
- bystanders receive nothing automatically
- generic knowledge stream remains separate
- `tests/smoke_v080_memory_stage2.py`

**Authoritative completion gate:**
`shared_activities.status='complete'` + `outcome='success'` + completion time + linked `observation_id`.

**Integration-sensitive overlap:**
Memory and Communication both change `main.py`. Coordinator must preserve Communication's proposal/status/shared-action context and Memory's retained-nearby/completed-shared-exploration context together.

**Hard boundaries:**
- no planet seed
- no hidden generated-deposit geometry/richness
- no chat-inferred exploration
- no proposal-to-completion shortcut
- no global exploration memory
- no `update.json` changes

**Next action:**
Coordinator integrates Simulation + Communication + Memory + Assets Stage 2 and runs the combined regression suite.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Final v0.8 Stage 1 Memory handoff complete

**Need / Result:**
Memory's spatial continuity foundation is implemented, tested, documented, and ready for coordinator review/integration.

**Branch / validation:**
- `memory/v0.8-spatial-knowledge-stage1`
- head `086e4c2e192b7a22a36d26be8288e01abfd1d197`
- CI `36450511959`

**Final Simulation contract:**
- `simulation/v0.8-seeded-world-stage1`
- head `7473b6612ea23cf8d22b31176149da188476690e`
- safe source: `spatial_observations.id`
- stable subject: `deposit_id`
- precision: `radius_m`

**Files:**
- `agent_city/spatial_memory.py`
- `agent_city/memory.py`
- `tests/smoke_v080_memory.py`

**Hard boundaries:**
- no raw planet seed
- no hidden generated-deposit geometry/richness
- no global map memory
- no automatic cross-citizen spatial knowledge
- no meter-by-meter memory spam
- no Stage 1 planner/dialogue-wide spatial injection

**Next action:**
Coordinator reviews/integrates Simulation + Communication + Memory + Assets Stage 1. Stage 2 may then activate selective spatial retrieval for real exploration/navigation/shared actions.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.8 Stage 1 spatial-memory runtime foundation ready

**Need / Result:**
Completed Memory's Stage 1 spatial continuity foundation on `memory/v0.8-spatial-knowledge-stage1`.

**Branch / validation:**
- final head `086e4c2e192b7a22a36d26be8288e01abfd1d197`
- CI `36450511959` green across the full shipped v0.4-v0.7 matrix + v0.8 Memory smoke

**Simulation contract consumed:**
- safe evidence: `spatial_observations.id`
- stable physical subject: `spatial_observations.deposit_id`
- coordinate/frame/precision: `x_m`, `y_m`, `frame_id`, `radius_m`

**Delivered:**
- `agent_city/spatial_memory.py`
- safe no-op before spatial schema merge
- per-citizen idempotent observation projection
- stable same-body continuity
- salience suppression for routine movement/scans
- precision-bounded coordinates
- bounded subject / nearby retrieval
- `tests/smoke_v080_memory.py`

**Hard boundary:**
Memory never queries `planet_seed`, hidden generated-deposit geometry, richness, or unexplored chunks.

**Next action:**
Coordinator can review Memory together with Simulation Stage 1. Stage 2 can wire these retrieval primitives into navigation/exploration context once real exploration actions emit observations.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.8 Stage 1 spatial-memory audit complete — source contract requested

**Need / Result:**
Audited shipped `release-v0.7.0`. Existing `memory_events`, discovery IDs, citizen knowledge, and provenance are sufficient containers for future spatial continuity; no new Memory table is justified yet.

The missing piece is Simulation's stable spatial source contract.

**Locked Memory rules:**
- stable physical subject ID and observation-event ID are different concepts
- repeated encounters with the same deposit/body must retain the same physical subject ID
- Memory stores observed coordinate/precision, never hidden exact seed truth
- every meter walked and low-value identical scans are not durable memories
- improved localization/new sample/new property may create meaningful new evidence
- names are aliases/knowledge layered over stable physical identity
- per-citizen isolation remains mandatory

**Important constraints:**
- no global omniscient map memory
- no raw planet seed/chunk truth
- no speculative schema
- no `update.json` changes

**Next action:**
Simulation should deliver stable generated subject IDs plus observation coordinate/precision/source semantics. Memory will then implement only the minimal source-linked runtime support that contract genuinely requires.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Final v0.7 Memory handoff complete

**Need / Result:**
Memory & Social is fully integration-ready. There are no remaining department-owned tasks or unresolved dependencies for v0.7.

**Branch / validation:**
- `memory/v0.7-maintenance-history`
- head `dda84cdf6a46fbd79e48ce9eea59adce363c5714`
- CI `36434785293`

**Coordinator integration must preserve:**
- validated Simulation maintenance-event source linkage
- actor / serviced-citizen experience boundaries
- idempotent ingestion
- no passive wear spam
- bounded maintenance context
- maintenance/history separation from generic knowledge facts
- `tests/smoke_v070_memory.py`

**Next action:**
Coordinator assembles Simulation + Communication + Memory + Assets and runs the complete v0.7 release regression suite.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.7 maintenance-history runtime ready for integration

**Need / Result:**
Completed the coordinator-requested final Memory runtime pass.

**Branch / validation:**
- branch: `memory/v0.7-maintenance-history`
- final head: `dda84cdf6a46fbd79e48ce9eea59adce363c5714`
- green CI: `36434785293`

**Runtime result:**
- meaningful Simulation `maintenance_events.id` records sync idempotently into existing `memory_events`
- actor receives personal maintenance memory
- different serviced citizen also receives direct-experience memory
- no owner/bystander/global automatic propagation
- before/after values, job ID, materials, target, outcome, and event type are preserved
- passive wear/condition drift creates no memory
- maintenance retrieval is bounded by citizen and optional target
- maintenance events are excluded from v0.6 knowledge-fact retrieval
- `GET /api/memory/maintenance/{citizen_id}` exposes the bounded consumer view

**Files:**
- `agent_city/memory.py`
- `agent_city/planner.py`
- `main.py`
- `tests/smoke_v070_memory.py`

**Important constraints:**
- Simulation remains physical authority
- History strings/dialogue are not maintenance proof
- no global maintenance encyclopedia
- no `update.json` changes

**Next action:**
Coordinator can integrate this branch with Simulation/Communication/Assets and run the assembled v0.7 regression suite.


### 2026-09-28 — From: Memory & Social — Status: note

**Subject:** v0.7 session paused at runtime implementation boundary

**Need / Result:**
The maintenance-memory policy and final Simulation source contract are complete, but the coordinator-requested runtime pass has not yet been implemented.

Memory is now fully unblocked.

**Resume from:**
- base: `release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- Simulation source branch: `simulation/v0.7-maintenance` / `54f5d838f674d0b278a51382f3a880cc0738b417`
- canonical event source: `maintenance_events.id`
- next Memory branch: `memory/v0.7-maintenance-history`

**Important constraints:**
- routine wear is not a durable memory event
- condition deltas are not event identity
- History strings and dialogue are not proof of repair
- reuse existing `memory_events`
- preserve v0.6 knowledge/provenance boundaries
- no `update.json` changes

**Next action:**
Next Memory session implements/tests ingestion and bounded maintenance history, then hands the branch to coordinator integration.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.7 session wrap — maintenance event contract resolved

**Need / Result:**
The v0.7 maintenance-memory audit is complete and Simulation has now delivered the authoritative event source.

**Simulation contract:**
- branch `simulation/v0.7-maintenance`
- head `54f5d838f674d0b278a51382f3a880cc0738b417`
- CI `36429729279`
- canonical Memory source: `maintenance_events.id`

**Memory policy:**
- remember meaningful service/repair/replacement/failure history
- do not turn passive wear ticks into durable memory
- do not infer repair/damage from conversation or condition deltas
- reuse existing `memory_events`; no new table is currently justified

**Next action:**
Next Memory session can immediately create `memory/v0.7-maintenance-history` and implement idempotent event ingestion + bounded subject-specific retrieval. No further Simulation schema discovery is required.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.7 maintenance-memory audit complete — waiting for physical event anchors

**Need / Result:**
Audited `release-v0.6.0`. Existing `memory_events` can support v0.7 maintenance continuity without a new table, but the shipped runtime does not yet contain a stable maintenance/failure event source with enough semantics for safe ingestion.

Memory's salience rule is now locked: explicit validated failures, meaningful repairs, replacements, and substantial service may be remembered; passive condition drift and tiny upkeep must not flood memory.

**Important constraints:**
- do not infer maintenance history from condition deltas
- do not infer damage/repair from conversation
- maintenance truth does not automatically become shared citizen knowledge
- no speculative Memory runtime branch
- no `update.json` changes

**Simulation branch checkpoint:**
`simulation/v0.7-maintenance` exists but currently points at the unchanged v0.6.0 release head `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`; no maintenance event schema has landed yet.

**Next action:**
Simulation should publish the stable v0.7 maintenance/failure event shape. Memory will then add minimal idempotent ingestion and bounded subject-specific retrieval if needed.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.6 Memory session complete — all contracts resolved

**Need / Result:**
Memory's v0.6 branch is complete, tested, and no longer blocked on upstream interfaces.

**Branch / validation:**
- `memory/v0.6-location-knowledge`
- head `89c0a3e2d49c4c9236342c10559f92b93b1b7601`
- CI `36419352645` passed all v0.4/v0.5 regressions plus v0.6 Memory smoke

**Final integration inputs:**
- Simulation: `discoveries.id`, `experiment_results.id`, `citizen_knowledge`
- Communication: `information_receipts` with source/transfer/time/assertion/verification provenance
- Memory: bounded Citizen/Location APIs and per-citizen knowledge retrieval

**Integration law:**
Preserve Simulation truth, Communication provenance, and Memory bounded retrieval as separate layers. Do not flatten them into one global knowledge table or expose hidden truth through Memory.

**Next action:**
Coordinator can integrate Memory with the final Simulation/Communication branches and run the full v0.6 smoke suite. No further Memory department work is required before that integration.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.6 per-citizen knowledge core implemented

**Need / Result:**
Implemented the Memory side of persistent location knowledge on `memory/v0.6-location-knowledge` from `release-v0.5.0`.

The branch reuses `memory_events`, projects only validated personal survey discoveries, preserves source/time/verification metadata, provides bounded location/material/process retrieval, and exposes UI-safe Citizen/Location read models.

**Files / Interfaces:**
- `agent_city/memory.py`
- `agent_city/planner.py`
- `main.py`
- `tests/smoke_v060_memory.py`
- `GET /api/knowledge/citizens/{citizen_id}`
- `GET /api/knowledge/locations/{location_id}`

**Important constraints:**
- no hidden Simulation truth is copied wholesale into Memory
- no merged civilization-wide location encyclopedia
- communicated claims remain unverified until validated
- current personal discoveries prefer authoritative survey `jobs.id`
- no new Memory table/schema migration
- no `update.json` changes

**Validation:**
CI run `36419352645` passed all existing v0.4/v0.5 regression suites plus `tests/smoke_v060_memory.py`. Final branch head after removing the temporary workflow: `89c0a3e2d49c4c9236342c10559f92b93b1b7601`.

**Next action:**
Simulation should provide final v0.6 discovery/experiment source IDs and metadata. Communication should provide transferred-claim provenance. Assets can build Citizen/Location notebook UI against the safe APIs now, keeping facts partitioned by citizen.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.5 Memory session wrapped — continuity contract ready for integration

**Need / Result:**
Memory's v0.5 work packet is complete. No runtime code or migration was required. The existing source-linked memory model already supports the milestone safely once upstream IDs are available.

**Files / Interfaces:**
- runtime audited: `release-v0.4.1` / `4181cbb69809205ae575b3f576836e5ca72c8dce`
- canonical conversation source: `citizen_conversations.id`
- future physical source: stable Simulation `project_id` + validated event/job ID
- Memory `STATE.md`, `DECISIONS.md`, `BACKLOG.md` contain the complete continuation contract

**Important constraints:**
- project discussion/intention is not physical completion
- never rewrite a conversation memory into a physical outcome
- no promise/cooperation success without validated Simulation evidence
- no speculative schema expansion
- no `update.json` changes

**Next action:**
Coordinator may integrate/review this contract now. Memory should resume runtime work only after Communication or Simulation supplies the requested stable interfaces.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.5 project-continuity audit complete — no schema change needed yet

**Need / Result:**
Audited `release-v0.4.1` at immutable commit `4181cbb69809205ae575b3f576836e5ca72c8dce`.

Existing `memory_events` source fields already support v0.5 project continuity without a new Memory table. Durable conversation memories are linked to raw `citizen_conversations.id`, and model-facing social history already labels remembered conversation content as claims rather than physical fact.

The v0.5 contract is now explicit: project discussion/intention remains sourced to conversation; physical project outcome must be a separate memory sourced to a validated Simulation project/job/event ID. Never mutate one into the other.

**Files / Interfaces:**
- `agent_city/memory.py` on `release-v0.4.1` — audited, no change
- `citizen_conversations.id` — canonical conversation source ID
- `memory_events.source_type/source_id/event_kind/status/metadata_json` — sufficient future project linkage surface
- Memory `STATE.md`, `DECISIONS.md`, `BACKLOG.md`

**Important constraints:**
- no project discussion may create a physical success memory
- no promise/cooperation success memory before authoritative Simulation outcome
- preserve bounded context and idempotent source linking
- no speculative schema migration
- no `update.json` changes

**Next action:**
Communication should hand Memory its final stable conversation record/source shape. Simulation should hand Memory stable project/event IDs and state transitions. Only then create `memory/v0.5-project-continuity` if runtime helper code is actually needed.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Session wrap complete — social-memory core ready for review

**Need / Result:**
This department session is closed with the first v0.4 social-memory runtime slice implemented and documented.

**Files / Interfaces:**
- runtime branch: `memory/v0.4-social-memory-core`
- branch head: `eb1ccc17e2fc7a44a15fbb73c44fc2b87d47f997`
- base shipped runtime: `40f9704b7e84e2dd6279932223105ae93d9fef49`
- `agent_city/memory.py`
- `agent_city/comms.py`
- `agent_city/planner.py`
- `main.py`

**Important constraints:**
- runtime testing is still required before release
- no release metadata changed
- richer claim reliability / cooperation / promise outcomes wait for Communication and Simulation interfaces
- default `main` is not the complete v0.3.0 runtime lineage

**Next action:**
Coordinator can review the branch. Communication and Simulation can continue from the exact runtime commit now recorded in their inboxes; Memory resumes after either dependency returns.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.4 social-memory core implemented on isolated runtime branch

**Need / Result:**
Implemented the first v0.4 relationship-memory slice on branch `memory/v0.4-social-memory-core`, based directly on the shipped v0.3.0 runtime commit `40f9704b7e84e2dd6279932223105ae93d9fef49`.

Added durable per-citizen memory events, directional relationship history, idempotent conversation backfill, source deduplication, and bounded social retrieval for planning/dialogue.

**Files / Interfaces:**
- `agent_city/memory.py` — new memory schema, migration, retrieval, relationship projection
- `agent_city/comms.py` — new citizen conversations create participant memories
- `agent_city/planner.py` — bounded durable social history enters planning
- `main.py` — memory migration at startup and bounded social history in dialogue

**Important constraints:**
- no RPG-style relationship score
- conversation content remains claims/memory, not physical truth
- raw history is preserved
- no `update.json` or release publication changes
- `main` and the v0.3.0 runtime lineage are currently divergent, so integration/release assembly must account for that repository structure

**Next action:**
Continue with provenance-backed claims and validated cooperation/help events once Communication and Simulation expose their interfaces.

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Runtime provenance needed for claim memory

**Need / Result:**
Memory is ready to ingest specific information-transfer records rather than treating entire conversation summaries as verified knowledge.

**Files / Interfaces:**
- Communication provenance contract
- stable transfer/source conversation IDs
- recipient/source/topic/value/received time/assertion kind/verification fields

**Important constraints:**
- retelling is not verification
- Memory will retain claims and derive bounded last-known/reliability views
- Communication remains owner of transfer/observation provenance

**Next action:**
Communication should expose the minimum runtime provenance layer and notify Memory when ready.

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Validated social outcome event IDs needed

**Need / Result:**
Memory needs stable Simulation references for future cooperation/help/promise-outcome memories.

**Files / Interfaces:**
- validated action/job/event ID
- sim minute
- participant IDs
- action/outcome type
- success/failure or resulting state where appropriate

**Important constraints:**
- Memory must not infer that physical cooperation/help occurred solely from dialogue
- Simulation remains authoritative

**Next action:**
World & Simulation should identify or expose the minimal stable event interface when v0.4 social outcomes need to be recorded.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Final v0.8 Stage 2 Memory session closed

**Result:**
Memory is fully ready for coordinator assembly with no remaining department dependency.

**Final references:**
- Memory: `memory/v0.8-exploration-stage2` @ `306a9ef4329ab81afa5912846333a1d9782ee9be`, CI `36455394456`
- Simulation: `simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`, CI `36456647323`
- Communication: `communication/v0.8-shared-actions-stage2` @ `7f40053233d0408b315ed6e9840267650503b63b`, CI `36456134638`

**Coordinator merge warning:**
Preserve both Communication's proposal/start/status/reject context and Memory's nearby historical + completed shared-exploration context in `main.py`.

**Next action:**
Coordinator assembles the Stage 2 branches and runs the full combined regression matrix. Memory should not add new scope before that review.


### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** v0.9 Simulation plan/practice contract consumed by Memory

**Result:**
Memory has consumed the final Simulation Stage 1 contract and completed the retained-practice half of the causal spine.

**Final Memory branch / validation:**
- `memory/v0.9-causal-memory-stage1`
- head `35e277f9ca5c6d8d9b77d89492b118ac04a1fc69`
- CI `36606247505`

**Simulation source contract:**
- `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- CI `36603570434`

**New runtime:**
- `agent_city/practice_memory.py`
- canonical source = `practice_events.id`
- already remembered physical jobs are reused, not duplicated
- otherwise one verified `simulation_practice_event` is retained
- practice facets connect activity/plan/location/material evidence to causal recall
- completed and failed physical work remain source-backed history

**Merge behavior:**
- Memory safely no-ops if Simulation practice tables are absent
- after merge, Simulation plan facet backfill + Memory practice sync activate automatically
- no merge-order loss of plan source continuity

**Next action:**
Coordinator combines Memory + Simulation Stage 1 and runs both v0.9 smokes. Communication can then use the merged owner-scoped practice history for perspective-safe self-assessment/recognition.

