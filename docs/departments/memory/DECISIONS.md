# Memory & Social — Decisions

## Bounded Context Rule

> **Full history may be stored locally, but model context must remain bounded.**

Never feed a citizen their entire lifetime transcript.

Use:

- recent context
- compact summaries
- relevant retrieval
- persistent raw archive

## Epistemic Rule

> **Conversation memory is not physical truth.**

A citizen remembering that someone claimed something does not make the claim true.

Simulation-validated state remains authoritative.

## Relationship Philosophy

Relationships emerge from recorded history rather than arbitrary starting scores.

Do not initialize citizens with invented friendship, trust, affinity, hostility, or compatibility numbers.

A relationship projection may contain internal counters/indices for retrieval and summarization, but every derived value must be traceable to real source events and must not be presented as the social reality itself.

## Layered Memory Architecture

v0.4 uses four conceptual layers:

1. **raw source history** — conversations and validated physical events remain preserved
2. **per-citizen memory events** — what one citizen experienced/heard/participated in
3. **relationship projection** — compact directional history derived from those memory events
4. **bounded retrieval** — only relevant summaries/memories enter model context

The projection is a cache/summary of history, not an independent source of truth.

## Directional Relationships

Relationship history is directional.

Aris's remembered history with Bex and Bex's remembered history with Aris may eventually differ because citizens can receive different information and interpret different events.

For a shared face-to-face conversation, both receive a memory sourced to the same conversation ID.

## Deduplication Rule

A source event may produce at most one matching memory per citizen, event kind, and source role.

Startup backfill must be idempotent.

Repeated startup, retrieval, summarization, or prompt construction must never inflate relationship history.

## Conservative Classification Rule

Do not infer rich social consequences merely because a conversation occurred.

A stored conversation currently establishes:

- encounter/familiarity history
- remembered content

It does **not** automatically establish:

- trust
- cooperation
- agreement
- friendship
- help
- promise
- reliability

Those require specific evidence.

## Promise Rule

Promises/commitments should become first-class memories only when a specific commitment can be identified and later linked to real outcomes.

A promise is not fulfilled merely because a conversation summary says it was.

Expected lifecycle includes states such as open, fulfilled, broken, withdrawn, or unresolved, with outcome changes grounded in validated events whenever possible.

## Reliability Rule

Information-source reliability changes only when a particular received claim is later verified or contradicted through an allowed information/observation path.

Repeated retelling does not verify a claim.

Do not erase the original claim when later evidence contradicts it.

## Communication Provenance Alignment

Memory adopts Communication & Perception's provenance contract rather than creating a parallel truth system.

Communication owns transfer/observation provenance.

Memory owns retention, retrieval, relationship interpretation, and bounded context.

Simulation remains authoritative for physical truth.

## Social Memory Sources

Valid social memory can come from:

- direct conversation
- direct observation
- cooperation on shared work
- fulfilled/broken promises
- help received
- disagreements
- information later verified or disproven
- repeated encounters

Each source must retain enough provenance to explain why the citizen remembers it.

## Ownership Boundary

Memory records and retrieves experience.

Memory does not alter physical outcomes or declare that an event happened if Simulation did not validate it.


## Runtime Lineage Decision

The complete shipped v0.3.0 runtime is anchored at commit `40f9704b7e84e2dd6279932223105ae93d9fef49`.

The default `main` branch currently contains the coordination/updater lineage and is not a safe base for runtime feature implementation because key v0.3.0 modules are absent there.

Until repository lineage is reconciled, runtime department branches must start from the shipped v0.3.0 runtime commit or another explicitly verified descendant. Documentation/coordination changes may continue on `main`.

Do not silently copy partial runtime files from `main` over the release lineage.


## Project Discussion vs Physical Outcome

A remembered discussion, plan, proposal, intention, or promise about a project is not evidence that the project physically started or completed.

Memory must preserve two distinct source chains:

1. **social/intention evidence** — sourced to the actual conversation or communication record
2. **physical outcome evidence** — sourced to a Simulation-owned validated project/job/event record

Never promote or rewrite the first record into the second.

Example:

- "Bex and Iri discussed building a cargo frame" may be remembered from `citizen_conversations.id = N`.
- "Cargo frame fabrication completed" may only be remembered as physical fact from a later validated Simulation source ID.

Both records may coexist and be linked by a validated `project_id`, but they remain epistemically different.

## v0.5 Source-Link Contract

The existing `memory_events` schema should be reused before adding new schema.

Recommended source semantics:

- `source_type='citizen_conversation'`, `source_id=<citizen_conversations.id>` for discussion/claims
- future `source_type='project'` or `'project_event'` only after Simulation defines the stable project/event interface
- future `source_type='job'` may be used for a validated completed job when Simulation confirms job IDs are durable and sufficient

When useful, `metadata_json` may carry cross-links such as a validated `project_id`, related conversation ID, or outcome type. These are references, not substitutes for authoritative source records.

Do not add promise/cooperation/help success counters from a project discussion alone.

## Conversation Source Stability

`citizen_conversations.id` is the canonical Memory source for a citizen-to-citizen exchange in v0.4.1.

Communication may extend conversation provenance, but it should preserve this source ID or provide an explicit immutable mapping from any replacement transfer record back to it.

Memory must not depend on UI chronology strings as a source identifier.


## No Speculative v0.5 Schema Decision

Do not create a v0.5 Memory branch, table, or migration merely to anticipate Simulation's unfinished project schema.

The existing `memory_events` source fields are sufficient for the known continuity requirements. Runtime helper code should be added only after Communication and Simulation publish their stable source interfaces.

This keeps migrations additive, minimal, and evidence-driven.


## v0.6 Knowledge Projection Rule

Memory may project validated discoveries into per-citizen knowledge records, but it must not copy Simulation's complete hidden world tables into Memory.

A knowledge record requires an information path to that citizen:

- personal validated experience/observation
- later, a real Communication transfer record
- later, another explicit physical record the citizen can access

Unknown is a legitimate state.

## Knowledge Source Rule

Use the most specific durable authoritative event ID available.

For current survey discoveries:
- prefer the completed survey `jobs.id` as `source_type='job'`
- if a legacy validated discovery has no recoverable job, use a clearly labeled legacy source and do not fabricate precise provenance

Future Simulation discovery/experiment IDs may be consumed through the generic knowledge-event hook once finalized.

## Knowledge Verification Rule

`memory_events.status='verified'` is allowed only when the caller supplies an authoritative validation source.

Communicated claims stay remembered/unverified until later validation. Repetition does not upgrade verification.

Verified and unverified facts may coexist; later verification should create/link evidence rather than silently rewriting history.

## Location Notebook Rule

A location detail surface must not merge all citizens' knowledge into one implied civilization-wide truth record.

Safe presentation is:

- one selected citizen's notebook, or
- separate labeled per-citizen knowledge sections

Assets may render only the safe Memory read model, not hidden Simulation truth.

## Bounded Knowledge Context Rule

Knowledge retrieval is independently bounded by subject and character budget.

Prefer:
- subject relevance
- recent/source-linked facts
- explicit verification labels

Do not feed a citizen every fact they have ever learned.


## v0.6 Final Layer Ownership

The integrated v0.6 knowledge model has three distinct authoritative layers:

### Simulation
Owns hidden world truth, validated discovery records, experiment outcomes, and current validated citizen knowledge possession.

Canonical anchors:
- `discoveries.id`
- `experiment_results.id`
- `citizen_knowledge(citizen_id, discovery_id)`

### Communication
Owns how information reached a citizen and preserves historical provenance.

Canonical receipt source:
- `information_receipts.source_key`

Transferred face-to-face assertions are speaker claims and begin unverified. Verified Simulation-grounded observations/results may be mirrored as verified receipts.

### Memory
Owns bounded durable retrieval and consumer-facing summaries/views.

Memory may reference Simulation and Communication records, but must not replace them with an independent truth model.

## Final v0.6 Source Semantics

For a validated discovery:
- preferred Memory source type: `simulation_discovery`
- source ID: `discoveries.id`

For a persisted experiment experience/result:
- preferred source type: `simulation_experiment_result`
- source ID: `experiment_results.id`

For a communicated claim:
- use the Communication receipt/conversation provenance
- preserve unverified status until a later validated evidence path exists

Do not infer verification from repeated claims or from Memory summaries.

## Integration Rule

Coordinator integration must preserve all three modules/layers.

Do not resolve merge conflicts by:
- exposing hidden Simulation truth through Memory
- dropping Communication provenance
- replacing Memory's bounded APIs with raw global discovery lists
- unioning all citizen knowledge into a single implied shared encyclopedia


## v0.7 Maintenance Salience Rule

Condition change is not itself a memory event.

Memory records selected maintenance experiences from explicit validated Simulation events, not from polling and diffing current condition values.

### Normally memorable

- failure/breakdown
- meaningful repair
- replacement
- substantial preventative service
- repeated failure pattern once supported by multiple real events
- service that materially affects future planning, capability, reliability, or place/equipment significance

### Normally not memorable

- routine passive wear
- tiny condition decrements
- ordinary charging
- trivial upkeep with no meaningful consequence

This prevents lifetime context from becoming a maintenance logbook.

## Maintenance Source Rule

A maintenance memory must reference a stable Simulation-owned source.

Preferred source shape:
- stable event or completed job ID
- simulation minute
- actor/participant citizen ID
- subject type and stable subject ID
- location
- physical event kind
- validated outcome
- before/after condition where naturally available
- replacement/resulting object ID where applicable

Memory may store these in existing `memory_events` metadata. No new table is required unless later evidence proves otherwise.

## Maintenance Epistemic Rule

Physical maintenance truth and who knows about it are separate.

Simulation may know a structure was repaired. That does not mean every citizen knows it.

Memory records only a citizen's valid experience/receipt of the event.

Conversation about a repair remains a claim unless Communication provenance and/or later physical verification supports it.

## Maintenance Context Rule

Maintenance history should be retrieved only when relevant to the current subject or decision.

Examples:
- a citizen considering reusing a tool with prior failures
- planning work at a structure with meaningful repair history
- discussing a citizen's own recent breakdown/repair
- evaluating repeated service needs

Do not add a general maintenance transcript to every prompt.


## v0.7 Final Maintenance Source Contract

Use Simulation `maintenance_events.id` as the canonical physical source for meaningful maintenance history.

Recommended Memory mapping:

- `source_type = 'simulation_maintenance_event'`
- `source_id = maintenance_events.id`
- `event_kind = maintenance_<event_type>`
- `status = 'verified'`
- metadata should retain `job_id`, target type/id, before/after values, outcome, materials, location when available, and Simulation event type

Do not use:
- raw condition snapshots as event sources
- History message strings as event identity
- conversation text as proof of repair/failure success

Routine wear remains physical state only unless Simulation creates a meaningful threshold/failure/service event.


## v0.7 Session Boundary Decision

The final v0.7 maintenance source contract is sufficient to implement Memory runtime ingestion, but implementation is deliberately deferred to the next Memory work session because this session was explicitly wrapped.

Do not mark the coordinator's runtime-pass request complete until:
- `memory/v0.7-maintenance-history` exists
- ingestion/retrieval code is implemented
- a v0.7 Memory smoke test passes
- final branch head/validation are recorded

The current state is **unblocked, not complete**.


## v0.7 Experience Assignment Rule

A validated maintenance event is not automatically shared knowledge.

Initial Memory assignment is deliberately conservative:

- the maintenance actor receives the event
- when `target_type='citizen'` and the target is a different citizen, that serviced citizen also receives the event
- equipment owners do not automatically receive service memories merely because they own the object
- bystanders do not automatically receive the event
- settlement-wide Memory propagation does not occur

Additional awareness must later come through a real observation or Communication provenance path.

## v0.7 Stream Separation Rule

Maintenance history and knowledge/research facts are separate retrieval streams.

`knowledge_snapshot_for` must not include `simulation_maintenance_event` records.

Maintenance history is retrieved through maintenance-specific functions and only injected into model context as a small bounded section.

This prevents character sheets and location notebooks from becoming repair logs.

## v0.7 Compatibility Rule

Memory's maintenance synchronization must safely no-op when the Simulation `maintenance_events` table does not exist.

This allows the Memory branch to remain regression-safe against its shipped v0.6 base while activating automatically after coordinator merge with the Simulation v0.7 schema.


## v0.7 Completion Decision

The Memory department's v0.7 runtime scope is complete.

No additional Memory feature work should be added before coordinator integration unless integration reveals a concrete regression or contract conflict.

The assembled release must preserve the existing Memory source and epistemic boundaries rather than broadening maintenance knowledge during merge.


## v0.8 Spatial Observation Rule

Memory records what a citizen actually observed, at the precision their observation mechanism supports.

Do not copy the Simulation's exact hidden coordinate merely because Memory can technically query it.

A spatial memory should preserve:
- observed coordinate
- observation precision/uncertainty
- method/source
- stable physical subject ID
- observation time

If later evidence improves precision, preserve the earlier observation and add/link the improved evidence rather than rewriting historical perception.

## Stable Physical Subject Rule

A generated deposit/body/place candidate needs one durable Simulation-owned identity independent of:
- current citizen position
- chunk loading
- UI tile/cell
- current name
- repeated scans
- discovery order

Memory uses that stable subject ID to connect repeated encounters.

Discovery-event IDs describe **encounters/evidence**.
Stable subject IDs describe **the physical thing**.

Do not conflate them.

## Spatial Salience Rule

Do not create durable memory for:
- every meter walked
- every position tick
- every low-value scan with no new information
- repeated identical observations with no meaningful precision/content change

Durable spatial memory is appropriate for:
- first meaningful encounter with a stable body/place
- materially improved localization/precision
- new validated property/sample from an existing body
- route/landmark milestone that changes future planning
- named-place creation/recognition when socially meaningful
- meaningful contradiction between prior location belief and new evidence

## Coordinate Precision Rule

Memory precision must be bounded by the source.

Examples:
- visual estimate may retain a broad radius
- field survey may support tighter coordinates
- instrument scan may support meter-scale or better precision if Simulation says so

Never report more decimal precision than the source justifies.

## Hidden Seed Boundary

Planet seed/chunk generation data remains Simulation-only hidden truth.

Memory may reference stable generated subjects and validated observations derived from that truth, but must never receive:
- raw seed
- unexplored chunk contents
- deterministic future deposit placements
- undiscovered extent/quantity
- exact hidden geometry beyond what was observed

## Place Naming Rule

Names are labels/knowledge, not physical identity.

A citizen-created place name should point to a stable subject/region ID where possible.

Multiple aliases may coexist. Communication determines how names spread; Memory retains which label reached which citizen.


## v0.8 Stage 1 Runtime Source Decision

Memory consumes only Simulation's safe `spatial_observations` ledger.

It must not query `generated_deposits` to enrich a memory, even when a stable deposit ID is known. The generated-deposit table contains hidden authoritative geometry/richness beyond what an observation may reveal.

Use:
- `source_type='simulation_spatial_observation'`
- `source_id=spatial_observations.id`
- metadata `subject_id=spatial_observations.deposit_id` when present

The event ID answers **which observation/evidence**.
The stable deposit ID answers **which physical thing**.

## v0.8 Repeat-Encounter Decision

Repeat contact with the same stable physical subject is not automatically a new durable memory.

Retain a later observation when it adds meaningful information, including:
- new observation method
- materially better precision
- later Stage 2 sample/property evidence
- explicit milestone semantics

Stage 1 uses a conservative improved-precision threshold of at least 25%.

## v0.8 Stage 1 Consumer Decision

Do not inject spatial memory into every planner/dialogue prompt yet.

Stage 1 establishes persistence, identity, precision, salience, and bounded retrieval. Stage 2 should add context only where exploration/navigation intent makes it relevant.


## v0.8 Stage 1 Completion Decision

The Stage 1 Memory scope is complete and should not expand before coordinator review.

No planner/dialogue-wide spatial context injection is part of Stage 1.

Future Stage 2 changes should be driven by real exploration/navigation/shared-action consumers and should reuse the existing spatial retrieval primitives rather than broadening Memory into a global map or hidden-world cache.


## v0.8 Stage 2 Current-vs-Retained Spatial Rule

Communication/Simulation current spatial grounding and Memory retained spatial continuity are separate context channels.

Current grounding answers what is authoritatively observable/known **now**.

Memory answers what this citizen personally observed/retained **before**.

Do not let historical spatial memory silently override current physical state.

## Nearby Retrieval Rule

The Stage 2 default 250 m nearby-memory radius is a relevance window, not a sensor or epistemic precision claim.

Observation precision remains solely determined by the retained observation's `radius_m` and source method.

## Shared Exploration Completion Rule

A visitor/citizen shared exploration becomes verified durable Memory only from an authoritative completed Simulation record:

- `shared_activities.status = 'complete'`
- `outcome = 'success'`
- non-null completion time
- non-null linked spatial observation

Conversational proposal, visitor acceptance, and active/in-progress physical state are not completed exploration memory.

## Proposal / Physical Event Separation

Communication's `shared_action_proposals.id` is social intent/proposal provenance.

Simulation's `shared_activities.id` is the physical shared-action source.

If both histories are later retained, they remain separate records connected through source visit/exchange/action metadata. Do not rewrite a proposal into a physical completion event.

## Shared Exploration Participant Rule

The citizen participant may retain the completed shared physical experience.

The visitor identity is retained as metadata for continuity, not inserted into `relationship_state`, which is currently citizen-to-citizen.

Bystanders and other citizens do not automatically receive the shared experience.

## Linked Observation Rule

A completed shared activity may reference `spatial_observations.id`, but the activity does not replace the observation.

Use:
- shared activity = social/participation event
- spatial observation = physical evidence

Both identities remain durable and independently explainable.

## Stage 2 Stream Separation Rule

Keep these retrieval streams distinct:
- generic research/location knowledge
- spatial observations
- completed shared exploration
- Communication provenance/claims
- citizen social relationship history
- maintenance history

This prevents one broad Memory feed from becoming an omniscient context dump.


## v0.8 Stage 2 Final Contract Confirmation

Final Simulation and Communication Stage 2 handoffs confirm the Memory implementation without requiring code changes.

Canonical sequence remains:

1. durable conversation may create social proposal intent
2. Communication proposal projection may exist
3. Simulation validates/persists canonical `shared_activities.id`
4. acceptance remains pre-start intent/state
5. only Simulation physical start creates `jobs.id`
6. successful completion creates/links `spatial_observations.id`
7. only then may Memory create verified `simulation_shared_activity` continuity

Simulation `rejected` is a pre-start terminal state with no movement/job/observation and must never be classified as completed exploration.

Memory's current implementation is therefore contract-complete for Stage 2.


## v0.9 Durable Archive vs Active Recall

`memory_events` is the durable archive.

Active recall is a computed bounded view.

Forgetting/aging may reduce active retrieval priority but must not mutate or delete the underlying source-backed event.

## v0.9 Facet Index Decision

Use `memory_event_facets` as a lightweight relational index over durable events.

Facets exist to answer "which past experiences are related to this current decision?"

They are not:
- identity
- class
- skill
- reputation
- habit
- physical truth

Future plan/place facets are allowed only when they point back to real retained events.

## v0.9 Reinforcement Decision

Repeated related experience may raise recall priority.

Reinforcement is based on multiple distinct source-backed memory events sharing meaningful facets.

It does not:
- merge events
- increase verification
- prove competence
- create titles
- convert claims into facts

Repeated unverified claims remain unverified.

## v0.9 Aging Decision

Stage 1 recall scoring combines:
- stored event importance
- recency decay
- bounded reinforcement

Aging reduces access probability/priority, not historical truth.

No summary/history rewriting occurs.

## v0.9 Persistent Plan Pinning Decision

A persistent plan should store stable `memory_event_id` references for the evidence/reasons that created or revised it.

Pinned memory IDs are guaranteed candidate inclusion in active recall.

This solves long-horizon plan continuity without:
- hard scripting the plan
- keeping every life event in prompt context
- inventing a hidden plan-priority explanation

Pinning preserves access, not obligation.

## v0.9 Source-first Plan Rule

A plan reason string is descriptive context, not causal evidence by itself.

The causal explanation must be reconstructable from stable Memory source IDs and their underlying real/communicated sources.

Preferred chain:

`source event → memory_event_id → plan source link → bounded recall → current interpretation → new intent`

## v0.9 Perspective Rule

Causal recall remains citizen-scoped.

Another citizen needs their own observation/communication/shared experience to form a related memory.

No global continuity packet, reputation, or settlement-wide personal memory exists.

## v0.9 UI Boundary

Do not expose internal recall score, reinforcement boost, or facet count as a canonical citizen identity metric.

Assets may later present source-backed plans/history/experience summaries through safe read models, but internal retrieval ranking is not citizen-visible truth.

## v0.9 Stage 1 Scope Boundary

Stage 1 does not yet implement:
- competence physics
- self-assessment beliefs
- teaching transfer
- habits/customs
- place attachment
- universal practice XP
- public reputation
- planner-wide persistent plans

It establishes the source/retrieval spine those features must use.


## v0.9 Canonical Practice Retention Decision

Simulation `practice_events.id` is the canonical Stage 1 evidence that real physical practice occurred.

Memory should retain this evidence, but must avoid duplicating a physical event already represented by another durable Memory source.

Dedupe precedence:

- if a Memory event already references the same `jobs.id`, reuse it and add practice facets
- otherwise create one `simulation_practice_event` Memory event

Job equivalence may be established through:
- `source_type='job' / source_id=jobs.id`
- Memory metadata `job_id`
- `source_job_id`
- `citizen_job_id`

Practice facets improve retrieval only.

They do not:
- create XP
- prove competence
- create role/class/specialization
- create a title
- create global reputation

## v0.9 Practice Outcome Decision

Both successful and failed eligible physical work are legitimate personal experience.

A failed or no-yield event may receive somewhat higher recall salience because it can affect future reasoning, but it remains one historical event rather than a permanent trait.

## v0.9 Plan/Practice Authority Split

Simulation owns:
- plan lifecycle
- job linkage
- `practice_events.id`
- later physical competence effects

Memory owns:
- durable retention
- causal linking
- practice dedupe
- bounded recall / reinforcement / aging

A practice event may carry a `plan` facet when `practice_events.plan_id` exists, connecting actual plan work to causal recall without making the plan itself a skill score.


## v0.9 Model-Facing Practice Recall Decision

Objective physical practice history and present autobiographical recall are different layers.

Simulation's full `practice_events` ledger may support diagnostics, read models, and historical accounting.

Model-facing self-assessment/teaching must use Memory's bounded active recall:

- `practice_recall_snapshot_for(...)`
- `practice_recall_context_for(...)`

This preserves aging, salience, and bounded context.

Internal `recall_score` and `reinforcement_count` must not be surfaced as natural-language citizen facts or hidden reputation/experience metrics.

Other-citizen recognition may use speaker-owned causal recall, but should present the source-backed events rather than internal retrieval weights.


## v0.9 Final Stage 1 Handoff Decision

Memory's Stage 1 scope is closed.

Do not add new Memory behavior before coordinator integration unless a concrete cross-department regression requires it.

The only remaining v0.9 Stage 1 semantic blocker is outside Memory:
Communication must keep model-facing self-assessment/teaching behind Memory active recall and must not expose internal reinforcement counts as citizen-visible evidence.

A green branch is insufficient if it bypasses archive-vs-recall semantics.

Memory remains in REVIEW until coordinator integration.


## v0.9 Stage 2 Guided-Practice Memory Rule

`guided_practice_sessions.id` is the canonical teaching-event identity.

A terminal guided session may create one durable personal Memory event for each direct participant:
- teacher
- learner

The same source ID is shared, while source role and counterparty preserve perspective.

Bystanders receive no automatic Memory.

## Guided Session != Practice Rule

A guided-practice session is a social/learning experience, not learner physical practice.

Never give the session a `practice_event` facet.

Learner practice exists only when Simulation later records a real eligible physical job and `practice_events.id`.

## Event-Local Role Rule

Teacher/learner are roles in one event only.

They do not create:
- permanent mentor/expert/trainer identity
- rank/class/specialization
- reputation
- behavioral authority

## Applied Guidance Rule

If Simulation later links a real learner job through:
- `jobs.guidance_session_id`
- `guided_practice_sessions.consumed_by_job_id`

Memory may preserve relational facets connecting:
- guided session
- later job
- later practice memory

This keeps causality traceable without creating competence.

## Competence Authority Rule

Simulation alone owns objective competence family mapping, evidence weights, duration effects, caps, and guidance effects.

Memory may retain the Simulation-supplied `competence_family` as a source facet.

Memory must not duplicate or recompute the competence projection.

Objective competence does not decay when Memory recall ages.

## Stage 2 Comparative Experience Rule

Do not expose a cross-citizen global experience ranking.

A citizen may interpret:
- their own actively recalled practice
- their own guided-practice history
- source-backed knowledge that actually reached them

The existence of a teacher/learner session supports "X guided me then," not "X is currently the best/more skilled."

## Terminal Failure Rule

If Simulation stores a terminal failed/cancelled guided session with a completion minute, Memory may retain it as a verified failed learning/social experience for both participants.

Failure is history, not a permanent negative trait.

## Stage 2 UI Rule

Use Memory's bounded continuity projection for remembered perspective.

Use Simulation's competence endpoint for objective physical effect/history.

Do not blend these into one skill/reputation meter.
