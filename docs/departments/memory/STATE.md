# Memory & Social — State

_Last updated: 2026-09-28_
_Current release: v0.6.0_
_Current development branch: `memory/v0.7-maintenance-history`_

## Mission

Preserve citizen continuity across long-running simulation time without overloading the local model context or confusing remembered claims with physical truth.

## Current Implementation

### Visitor conversation persistence

v0.2.7 introduced persistent visits:

- browser refresh restores the active visit
- Leave Visit explicitly ends a session
- raw visitor/citizen exchanges are archived in SQLite
- current visit uses a bounded recent window
- older parts of a long visit are summarized
- previous visit summaries can be viewed
- Ollama receives bounded recent context plus summaries, not an unbounded lifetime transcript

### Citizen conversation memory

v0.2.8 introduced stored citizen-to-citizen conversation records.

Citizens receive recent summaries only for conversations they actually participated in.

Conversation memory is informational, not authoritative physical history.

### v0.4 social-memory core — implemented on development branch

Branch: `memory/v0.4-social-memory-core`

The first v0.4 slice now adds:

- `memory_events`: durable per-citizen memory records with source references and deduplication
- `relationship_state`: directional pair history derived from actual events, not arbitrary starting scores
- automatic idempotent backfill of existing `citizen_conversations`
- automatic memory creation for both participants when a new citizen conversation is stored
- bounded social-history retrieval for citizen planning
- bounded social-history retrieval during citizen dialogue / visitor conversations
- preference for relationship context involving citizens currently co-located with the planner
- a read-only relationship snapshot helper for future API/UI use

Current derived relationship evidence is intentionally conservative:

- recorded conversation count
- first recorded interaction time
- last recorded interaction time
- recent remembered conversation summaries

Fields for cooperation, disagreement, help, promises, and claim reliability exist in the projection schema but are not incremented until validated source events/provenance exist.

No visible or behavioral RPG-style social score was added.

## Migration / Compatibility

The new memory schema is additive.

Existing v0.3.0 databases are preserved. Startup scans existing `citizen_conversations` and inserts missing participant memories using a unique source key, so repeated startups do not create duplicate memories or inflate encounter counts.

Raw conversations remain the source archive.

## Repository Note

The default `main` branch is currently a coordination/updater lineage and does not contain the complete v0.3.0 runtime tree.

The released v0.3.0 manifest points to commit `40f9704b7e84e2dd6279932223105ae93d9fef49`, which contains the full runtime (`db.py`, `comms.py`, `simulation.py`, `visits.py`, etc.).

The Memory runtime branch therefore starts from that exact v0.3.0 commit rather than modifying the incomplete bootstrap tree.

No release metadata or `update.json` has been changed.

## Current Emergent Social Behavior

Observed before a formal relationship system exists:

- Noma sought Cato at Resin Grove
- Noma later initiated conversation with Cato
- Bex initiated conversation with Aris before distant travel
- Iri sought Vale as a possible information source

The new relationship history now gives repeated encounters like these durable continuity without scripting them.

## Current Dependencies

No unresolved v0.6 department dependency remains.

### Simulation contract received

Memory may consume:
- `discoveries.id` as stable validated discovery source
- `experiment_results.id` as stable experiment-result source
- `citizen_knowledge(citizen_id, discovery_id)` as validated citizen possession of discovery knowledge
- discovery subject/location/material/property metadata
- experiment outcomes `discovery | verified | inconclusive`

Simulation remains the authority for hidden world truth and validated discovery state.

### Communication contract received

Memory may consume:
- `information_receipts`
- recipient/source actor
- subject/topic/value
- observation/transfer source IDs
- received/observed simulation time
- assertion kind
- verification state
- immutable source key

Verified Simulation-grounded receipts remain verified. Face-to-face claims remain unverified unless independently validated.

Coordinator integration must preserve Simulation `agent_city/knowledge.py`, Communication `agent_city/provenance.py`, and Memory's bounded consumer read model as separate layers.

## Next Memory Work

After provenance/event interfaces are available:

1. ingest validated cooperation/help memories
2. track specific communicated claims separately from conversation summaries
3. update source reliability only when claims are physically verified or contradicted
4. add explicit commitment lifecycle once promises can be safely extracted and linked to outcomes
5. expose relationship history through an API for Assets, without a simplistic social leaderboard


## Session Close — 2026-09-28

Memory & Social work for this session is complete and handed off.

**Development branch:** `memory/v0.4-social-memory-core`  
**Current branch head:** `eb1ccc17e2fc7a44a15fbb73c44fc2b87d47f997`  
**Base runtime commit:** `40f9704b7e84e2dd6279932223105ae93d9fef49`

The implemented slice is ready for integration review. The next richer memory work is intentionally waiting on:

- Communication runtime provenance for specific claims / last-known information
- Simulation-confirmed stable event references for physical cooperation/help/outcome memories

The exact full v0.3.0 runtime source location has been sent to both departments so they do not need this chat history to resume.

### Verification still required before release

- start Agent City against an existing v0.3.0 SQLite database
- confirm startup backfill creates exactly one participant memory per prior conversation
- restart again and confirm idempotency / no relationship-count inflation
- create several new citizen conversations and confirm relationship history updates immediately
- confirm planner context remains bounded and does not promote conversation claims into physical truth
- exercise Ollama-backed citizen/visitor dialogue with the new social-history context

No release was published and `update.json` remains unchanged.


## v0.5.0 Project Continuity Audit

_Audited against immutable runtime commit `4181cbb69809205ae575b3f576836e5ca72c8dce` (`release-v0.4.1`)._

No Memory runtime code change is required yet.

The existing v0.4 schema already provides the minimum v0.5 source-linking primitive:

- every durable citizen conversation memory uses `source_type = 'citizen_conversation'`
- `source_id` is the stable raw `citizen_conversations.id`
- the raw record retains simulation minute, location, both participant IDs, both utterances, and the concise summary
- the model-facing relationship context explicitly labels remembered conversation content as claims rather than automatic physical facts
- unique source keys keep conversation backfill idempotent

This means a discussion such as "we should build a field charger" can remain traceable to the exact conversation without implying that a field charger exists.

### v0.5 project/source rule

Project discussion/intention and physical project outcome must be separate evidence records.

**Conversation / intention record**
- source remains the raw conversation or other real communication record
- semantic class: discussion, idea, intention, proposal, or commitment
- never establishes fabrication/construction success

**Physical outcome record**
- source must be a Simulation-owned validated project/job/event ID
- may record underway/completed/failed/cancelled physical outcome only after Simulation validates it
- does not overwrite or rewrite the earlier conversation memory

The existing `memory_events.source_type`, `source_id`, `event_kind`, `status`, and `metadata_json` fields are sufficient for this distinction. No new table or column should be added until the Simulation project/event interface is final.

### Current v0.5 dependencies

Communication should preserve `citizen_conversations.id` as the canonical source ID when it fixes conversation-history integrity.

Simulation should expose stable project IDs plus stable validated event/job IDs and state transitions. Memory can then add project-intention/outcome helpers without changing the storage schema.

### Branch status

No `memory/v0.5-project-continuity` branch has been created because this audit found no safe runtime code change to make before the upstream source interfaces are finalized.

No release metadata or `update.json` was changed.


## v0.5 Session Close

The v0.5 Memory & Social work packet is complete for this session.

Completed:
- audited `release-v0.4.1` / commit `4181cbb69809205ae575b3f576836e5ca72c8dce`
- verified durable citizen memories remain source-linked to `citizen_conversations.id`
- confirmed current `memory_events` fields are sufficient for future project continuity without a schema migration
- locked the separation between remembered project discussion/intention and validated physical project outcomes
- sent Communication the canonical conversation-source continuity requirement
- sent Simulation the stable project/event identifier requirement
- left runtime code untouched because the upstream interfaces are not final and no safe change is currently required

Memory is ready for coordinator review. Follow-on runtime project-memory helpers remain intentionally deferred until the requested Communication and Simulation interfaces arrive.

No `memory/v0.5-project-continuity` branch was created. No release metadata or `update.json` was changed.


## Shipped v0.5.0 Integration

v0.5.0 shipped without a new Memory schema migration, as intended.

The published runtime preserves:
- canonical conversation source IDs
- source-linked talk jobs
- stable Simulation project/job/equipment/structure IDs
- the distinction between remembered discussion and validated physical outcome

Published runtime commit:
`d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`.


## v0.6 Location Knowledge — Implementation

Branch: `memory/v0.6-location-knowledge`  
Base: `release-v0.5.0` / `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`

Memory now provides a bounded per-citizen knowledge layer without duplicating Simulation's hidden truth.

### Implemented

- existing `memory_events` reused; no new table/migration
- personally validated survey discoveries are projected into Memory using the authoritative survey job ID when available
- legacy validated discoveries without a matching job use a clearly labeled legacy deposit source instead of invented provenance
- new knowledge records retain source type, source ID, simulation minute, verification status, and structured metadata
- knowledge retrieval can filter by location, material, or future process
- model-facing knowledge context is bounded separately from social context
- planner receives only the planning citizen's retained knowledge for their current location
- visitor conversation can use only that citizen's retained local knowledge
- location notebook read model partitions facts by citizen; it never unions all citizen knowledge into one omniscient summary

### Safe read APIs

- `GET /api/knowledge/citizens/{citizen_id}`
  - optional filters: `location_id`, `material`, `process`, `limit`
  - returns only that citizen's retained facts plus a bounded summary
- `GET /api/knowledge/locations/{location_id}`
  - optional `citizen_id`
  - without a citizen filter, returns separate per-citizen views rather than a merged location truth record

### Current authoritative source support

Today, personal deposit knowledge is sourced from validated survey/deposit records already present in v0.5.

The generic `record_knowledge_event(...)` hook is ready for future Simulation discovery/experiment IDs and Communication-transferred claims. Callers must mark communicated claims unverified until a real verification path exists.

### Compatibility

- v0.4/v0.5 social memory remains unchanged
- conversation memories remain source-linked to canonical `citizen_conversations.id`
- idempotent backfill is preserved
- missing knowledge remains valid and expected
- hidden undiscovered deposits are never imported into Memory
- no global shared encyclopedia was added

A focused `tests/smoke_v060_memory.py` covers per-citizen isolation, idempotency, source linkage, unverified claims, location notebook partitioning, and API imports.


### v0.6 Validation

Branch head: `89c0a3e2d49c4c9236342c10559f92b93b1b7601`

Temporary branch CI run `36419352645` passed:
- Python compile
- JavaScript syntax
- v0.4 regression smoke
- v0.5 Simulation smoke
- v0.5 Communication integrity smoke
- v0.5 UI integration smoke
- new v0.6 Memory knowledge smoke

The temporary branch-only workflow was removed after validation.


## v0.6 Final Session Handoff

Memory & Social v0.6 work is complete and ready for coordinator integration.

**Branch:** `memory/v0.6-location-knowledge`  
**Head:** `89c0a3e2d49c4c9236342c10559f92b93b1b7601`  
**Validation:** CI run `36419352645` passed all v0.4/v0.5 regressions plus the v0.6 Memory smoke.

Final upstream contracts received:

- Simulation: `simulation/v0.6-research-discovery` @ `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`, CI `36419824468`
- Communication: `communication/v0.6-knowledge-provenance` @ `6a483fcc4d143606f3e401218002e06ae43076d1`, CI `36421263078`

No further Memory branch change is required before integration. The coordinator should preserve the three-layer model:

1. Simulation owns hidden truth + validated discoveries/current verified citizen knowledge.
2. Communication owns immutable information receipts and unverified transferred claims.
3. Memory owns bounded retention/retrieval and consumer-facing Citizen/Location knowledge views.

Assets has already received the safe Memory read-model contract.

No release was published and `update.json` was not changed.


## Shipped v0.6.0 Integration

Memory v0.6 work is included in the published runtime:
`6092aeafd685a3ba4cb8e9d455e586771d3f6d26`.

The assembled release passed the full cross-department smoke suite. Coordinator integration preserved Simulation truth, Communication provenance, Memory bounded retrieval, and Assets safe presentation as distinct layers.


## v0.7 Maintenance Memory Audit

_Audited against published `release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`._

No Memory runtime branch has been created yet.

### Existing physical substrate

v0.6 already has durable physical condition fields:

- citizens: `integrity`, `joint_wear`
- equipment: stable `id`, `condition`, owner/location
- structures: stable `id`, `condition`, location/type
- jobs: stable physical action IDs and outcomes

However, v0.6 does **not** yet expose a durable maintenance/failure event ledger with enough semantics to distinguish routine wear from meaningful service history.

### Memory direction

The existing `memory_events` table remains sufficient.

Maintenance should enter Memory only from explicit validated Simulation events. Memory should not poll condition values and synthesize history from deltas.

Examples that can become durable memories once validated:

- breakdown/failure that affects operation or interrupts work
- explicit repair that restores a damaged citizen/equipment/structure
- component/battery/equipment replacement
- preventative service that is substantial enough to be a real action/event
- major maintenance tied to a meaningful place, tool, or repeated reliability issue

Routine noise that should **not** become a memory:

- every small condition decrement
- ordinary charging
- passive wear ticks
- tiny lubrication/service adjustments with no meaningful consequence
- inferred damage from conversation or current condition alone

### Knowledge boundary

A maintenance event is not automatically known by every citizen.

A citizen may remember it when they:
- experienced the failure themselves
- performed the repair/service
- directly observed it through a valid mechanism
- later received it through Communication provenance

Memory will not inject hidden diagnostics or settlement-wide maintenance truth into citizen context.

### Branch status

No `memory/v0.7-maintenance-history` branch is justified until Simulation publishes stable maintenance/repair event anchors.

No release metadata or `update.json` was changed.


### Simulation v0.7 branch checkpoint

`simulation/v0.7-maintenance` now exists, but at the time of this Memory audit its head is still the published v0.6.0 commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`.

No maintenance/failure schema, event ledger, repair action, or v0.7 smoke test is present yet.

Memory should therefore remain in policy/design review rather than creating runtime ingestion against nonexistent fields.


## v0.7 Final Session Handoff

Memory & Social is stopping this session at the implementation boundary.

Simulation's final v0.7 maintenance contract is now available:

- branch: `simulation/v0.7-maintenance`
- head: `54f5d838f674d0b278a51382f3a880cc0738b417`
- CI: `36429729279`
- stable source: `maintenance_events.id`

Authoritative maintenance event fields:

- `id`
- `job_id`
- `citizen_id`
- `event_type`
- `target_type`
- `target_id`
- `before_value`
- `after_value`
- `materials_json`
- `outcome`
- `sim_minute`
- `summary`

Current event types:

- `chassis_service`
- `battery_replacement`
- `equipment_service`
- `structure_service`

Simulation intentionally does not emit a maintenance event for every microscopic wear tick.

### Next Memory implementation

The next Memory session should create `memory/v0.7-maintenance-history` from published `release-v0.6.0` and add only minimal runtime support:

1. idempotently ingest meaningful `maintenance_events` into existing `memory_events`
2. give the event to citizens with a valid experience path, starting with the acting citizen and, where appropriate, the directly serviced citizen
3. preserve Simulation source/event IDs and before/after values in metadata
4. add bounded retrieval by citizen / target type / target ID
5. expose a compact maintenance-history read model only if Assets needs it
6. add a v0.7 Memory smoke proving passive wear does not flood memory

Do not infer failures or repairs from conversation or from condition deltas alone.

No Memory runtime code was changed this session. No release metadata or `update.json` was changed.


## v0.7 Wrap Status — Runtime Pass Still Open

This work session is closed, but the coordinator's final v0.7 Memory runtime request is **not complete yet**.

The blocker is resolved. Simulation delivered the stable maintenance event contract:

- branch: `simulation/v0.7-maintenance`
- head: `54f5d838f674d0b278a51382f3a880cc0738b417`
- CI: `36429729279`
- canonical source: `maintenance_events.id`

The next Memory session should immediately implement the runtime slice on:

`memory/v0.7-maintenance-history`

from published base:

`release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

Required implementation remains:

- idempotent ingestion of meaningful `maintenance_events` into existing `memory_events`
- valid experience-path assignment, beginning with the actor and directly serviced citizen where justified
- Simulation source/event/job IDs and before/after/material/outcome metadata retained
- bounded retrieval by citizen and maintenance target
- minimal consumer read model only if useful to Assets/History
- v0.7 Memory smoke proving passive wear does not flood durable memory
- preservation of all v0.4-v0.6 social/knowledge/provenance behavior

Do not infer maintenance from condition deltas, History strings, or dialogue.

No Memory runtime branch was created in this session. No release metadata or `update.json` was changed.


## v0.7 Maintenance History — Runtime Complete

Branch: `memory/v0.7-maintenance-history`  
Base: `release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`  
Final branch head: `dda84cdf6a46fbd79e48ce9eea59adce363c5714`

### Implemented

- reuses existing `memory_events`; no new Memory table
- safely no-ops before Simulation's `maintenance_events` table is merged
- idempotently ingests explicit validated `maintenance_events`
- canonical source: `source_type='simulation_maintenance_event'`, `source_id=maintenance_events.id`
- actor citizen receives the event as direct personal experience
- if a different citizen is the physical maintenance target, that serviced citizen also receives the event
- equipment owners, bystanders, and the whole settlement are **not** auto-granted maintenance memory
- source metadata retains:
  - maintenance event ID
  - physical job ID
  - event type
  - target type / target ID
  - before / after physical values
  - consumed materials
  - outcome
  - experience role
- maintenance importance is bounded by event class
- routine passive wear remains absent because Simulation does not emit maintenance-event rows for microscopic wear
- v0.6 knowledge retrieval explicitly excludes `simulation_maintenance_event`, so service history does not pollute research/location knowledge sheets
- planner and visitor conversation receive only a bounded selection of that citizen's own meaningful maintenance experiences

### Read model

`GET /api/memory/maintenance/{citizen_id}`

Optional filters:
- `target_type`
- `target_id`
- `limit`

Returns:
- citizen identity
- applied filters
- bounded `events[]`
- compact maintenance summary

This is a citizen-experience view, not a settlement-wide physical maintenance ledger. Current condition/status remains Simulation-owned.

### Validation

Green branch CI: `36434785293`

Passed:
- Python compile
- JavaScript syntax
- v0.4 regression smoke
- all v0.5 smoke suites
- all v0.6 Simulation / Communication / Memory / UI smoke suites
- new `tests/smoke_v070_memory.py`

The v0.7 Memory smoke verifies:
- safe no-op before Simulation maintenance schema merge
- passive condition change creates no durable memory
- actor-only equipment service memory
- actor + serviced-citizen memory for citizen-target service
- no bystander/global propagation
- idempotent repeated synchronization
- target-scoped bounded retrieval
- maintenance history stays separate from knowledge facts
- API returns citizen-scoped history

The temporary branch-only workflow was removed after the green run.

### Integration note

Coordinator must merge this branch with Simulation's `maintenance_events` schema from `simulation/v0.7-maintenance`. The Memory branch is intentionally compatible before and after that merge.

No release metadata or `update.json` was changed.


## v0.7 Session Close — Integration Ready

Memory & Social v0.7 work is fully complete for this session.

Final branch:
`memory/v0.7-maintenance-history`

Final head:
`dda84cdf6a46fbd79e48ce9eea59adce363c5714`

Validation:
GitHub Actions run `36434785293` passed the full shipped v0.4-v0.6 regression chain plus `tests/smoke_v070_memory.py`.

No Memory-owned dependency remains.

Coordinator integration should preserve:
- Simulation `maintenance_events.id` as the physical source
- Memory actor / serviced-citizen experience boundaries
- no passive-wear memory spam
- separation between maintenance history and research/location knowledge
- bounded planner/visitor maintenance context
- citizen-scoped `GET /api/memory/maintenance/{citizen_id}`

No release was published and `update.json` was not changed.
