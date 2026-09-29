# Memory & Social — State

_Last updated: 2026-09-28_
_Current release: v0.7.0_
_Current development branch: `memory/v0.9-causal-memory-stage1`_

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


## v0.8 Stage 1 Spatial Knowledge Audit

_Audited against shipped `release-v0.7.0` / `d81a85bf03b69b969532016f59bbbed2233949ee`._

No Memory runtime branch has been created yet.

### What already supports v0.8

The existing Memory/knowledge stack already provides:

- `memory_events` with source type + source ID + metadata
- stable `discoveries.id` event anchors
- stable `discoveries.subject_type / subject_id`
- stable deposit IDs in the current landmark model
- `citizen_knowledge(citizen_id, discovery_id)` for per-citizen possession
- Communication provenance with immutable source/transfer IDs
- bounded per-citizen retrieval
- verified vs unverified knowledge separation

This means v0.8 does **not** justify a new spatial-memory table by itself.

### Current gap

v0.7 discovery records are landmark-oriented:

- `discoveries.location_id` identifies a named landmark
- current deposit rows belong to a landmark
- Memory metadata records `location_id`
- there is no observation coordinate or observation precision in the discovery/memory contract
- coordinate fields exist for landmark/project/structure placement, but not yet as a citizen knowledge source contract

Continuous exploration therefore needs new Simulation source semantics, not a parallel Memory truth model.

### Stage 1 Memory direction

Once Simulation provides stable spatial observation/deposit anchors, Memory should reference them through existing `memory_events`.

Expected Memory metadata for a meaningful spatial observation may include:

- stable physical subject type + subject ID
- authoritative observation/discovery event ID
- observed coordinate
- coordinate reference frame
- precision / uncertainty radius or equivalent
- observation method
- simulation minute
- optional landmark/place association if actually known
- sample/scan ID when a physical sample or scan is the source
- verification state

Memory should store the coordinate **as observed**, not silently replace it with a more precise hidden Simulation coordinate.

### Stable subject continuity

Repeated encounters with the same generated physical deposit/body must use the same stable subject ID.

A second observation of the same body may add:
- a newer observation time
- a different observed coordinate/edge point
- improved precision
- new properties/samples

It must not create the fiction of a second unrelated deposit merely because the citizen encountered it from another meter-scale position.

### Naming / places

A future citizen-created place name should be a social/knowledge label attached to a stable physical/spatial subject or region.

Naming must not replace the underlying stable subject ID.

Different citizens may initially know different names for the same place until Communication transfers or reconciles them.

### Branch status

Do not create `memory/v0.8-spatial-knowledge-stage1` until Simulation's Stage 1 stable coordinate/deposit/observation contract lands.

No release metadata or `update.json` was changed.


## v0.8 Stage 1 Spatial Memory — Runtime Foundation Complete

Branch: `memory/v0.8-spatial-knowledge-stage1`  
Base: `release-v0.7.0` / `d81a85bf03b69b969532016f59bbbed2233949ee`  
Final head: `086e4c2e192b7a22a36d26be8288e01abfd1d197`

Consumed Simulation Stage 1 contract from:
`simulation/v0.8-seeded-world-stage1` @ `0a22813d75b4f4c5cb47a5d06e8a561c95492566`.

### Implemented

New module: `agent_city/spatial_memory.py`

Memory now supports source-linked per-citizen spatial continuity from Simulation's safe `spatial_observations` ledger.

Canonical semantics:
- evidence source: `spatial_observations.id`
- stable physical subject: `deposit_id` / generated deposit stable ID
- observation frame: `frame_id`
- observed coordinate: `x_m / y_m`
- observation uncertainty: `radius_m`
- observer/time/method/source job retained

Memory **does not read**:
- `planet_seed`
- `generated_deposits`
- hidden center/axis/angle geometry
- richness
- unexplored chunk truth

### Salience behavior

Durable spatial Memory keeps:
- first meaningful encounter with a stable deposit/body
- a new observation method for that stable subject
- materially improved localization precision
- explicit non-routine spatial milestones

It suppresses:
- every meter walked
- position ticks
- passive scans with no stable subject
- repeat same-body observations with no method/precision improvement

Repeated encounters retain the same stable `subject_id`; they do not create fictional duplicate deposits.

### Precision behavior

Coordinates stored in Memory are rounded no finer than the observation uncertainty:
- >=100 m uncertainty -> 100 m coordinate step
- >=10 m -> 10 m
- >=1 m -> 1 m
- sub-meter -> 0.1 m

Memory stores the observed location, not hidden exact body geometry.

### Isolation / retrieval

- observations remain per-citizen
- another citizen does not inherit them automatically
- `spatial_snapshot_for(...)` supports stable-subject filtering and bounded nearby retrieval
- `spatial_context_for(...)` provides compact subject continuity
- spatial events are excluded from generic v0.6 knowledge-fact retrieval
- sync safely no-ops before Simulation's spatial table exists

No planner/UI prompt expansion was added in Stage 1. The retrieval layer is ready for Stage 2 consumers when physical exploration actions begin producing observations.

### Validation

CI `36450511959` passed:
- compile / JS syntax
- full shipped v0.4-v0.7 regression matrix
- new `tests/smoke_v080_memory.py`

Smoke coverage verifies stable-subject continuity, salience suppression, precision bounding, per-citizen isolation, nearby/subject retrieval, idempotency, and absence of hidden seed/geometry fields.

The temporary CI workflow was removed after validation.

No release metadata or `update.json` was changed.


## v0.8 Stage 1 Session Close — Integration Ready

Memory & Social Stage 1 work is complete.

**Memory branch:** `memory/v0.8-spatial-knowledge-stage1`  
**Final head:** `086e4c2e192b7a22a36d26be8288e01abfd1d197`  
**Validation:** CI `36450511959` passed the full shipped v0.4-v0.7 regression matrix plus `tests/smoke_v080_memory.py`.

**Final Simulation contract consumed:**  
`simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`

No unresolved Memory-owned Stage 1 dependency remains.

Coordinator integration must preserve:
- `spatial_observations.id` as observation/evidence identity
- stable `deposit_id` as physical-subject identity
- `radius_m` as epistemic precision
- per-citizen observation ownership
- same-body repeat continuity
- salience filtering against meter-by-meter memory spam
- strict exclusion of `planet_seed`, hidden generated geometry, richness, and unexplored world truth
- separation of spatial observation memory from generic research/location knowledge

Stage 2 may selectively wire this retrieval into exploration/navigation context only after coordinator authorization and real Simulation-owned exploration/shared-action lifecycles exist.

No release was published and `update.json` was not changed.


## v0.8 Stage 2 Exploration Memory — Runtime Complete

**Base:** `release-v0.8.0` / `017b417386f4f4e0f957dfb66285431223283739`  
**Branch:** `memory/v0.8-exploration-stage2`  
**Final head:** `306a9ef4329ab81afa5912846333a1d9782ee9be`  
**Validation:** CI `36455394456` passed the full unified Stage 1 regression matrix plus `tests/smoke_v080_memory_stage2.py`.

Stage 2 contracts consumed from:
- Simulation `simulation/v0.8-exploration-stage2` @ `be3614ad34475a5a5ad9bf7661d053bc3ad6ab42`
- Communication `communication/v0.8-shared-actions-stage2` @ `a6574fcf3988d57d7608f7ccab5c34e3fefaa380`

### Retained exploration enters planning

Citizen planning now receives a bounded section of **historical personal spatial memory near the citizen's current meter-scale position**.

Default selection:
- center: current `position_x_m / position_y_m`
- search radius: 250 m
- max retained memories: 4

The 250 m selection window is relevance filtering only. It is **not** observation precision. Each remembered observation still preserves its own `radius_m`.

Planner instructions explicitly distinguish retained exploration memory from current authoritative physical state.

### Retained exploration enters visitor dialogue

Visitor/citizen dialogue receives:
- Communication-owned current spatial grounding
- a separate bounded retained personal exploration section near the citizen's current position
- completed shared-exploration continuity with the current visitor

Historical Memory is never presented as a fresh current observation unless current grounding independently confirms it.

### Safe spatial read model

`GET /api/memory/spatial/{citizen_id}`

Optional filters:
- `subject_id`
- `center_x_m` + `center_y_m`
- `radius_m`
- `limit`

The API is citizen-scoped. It does not expose a global known-world map.

### Completed shared exploration continuity

New module: `agent_city/exploration_memory.py`.

A shared visitor/citizen exploration becomes verified durable Memory **only** when Simulation records:

- `shared_activities.status = 'complete'`
- `shared_activities.outcome = 'success'`
- non-null `completed_minute`
- non-null linked `observation_id`

Memory source:
- `source_type = 'simulation_shared_activity'`
- `source_id = shared_activities.id`

Metadata retains:
- visitor identity
- activity type/objective/frame
- source visit ID
- source exchange ID
- citizen physical job ID
- linked spatial observation ID
- physical outcome/status

Proposal, conversational acceptance, and active/in-progress rows do **not** become completed exploration memories.

The participating citizen receives the shared experience. Bystanders do not.

The linked `spatial_observations.id` remains a separate physical evidence record and is not replaced by the shared social event.

### Stream separation

Generic research/location knowledge excludes both:
- `simulation_spatial_observation`
- `simulation_shared_activity`

Spatial observation memory, shared exploration experience, research knowledge, provenance claims, social relationship memory, and maintenance history remain distinct bounded streams.

### Integration note

Memory and Communication both modify `main.py` in Stage 2.

Coordinator conflict resolution must preserve **both**:
- Communication's shared-action proposal/status lifecycle and current authoritative grounding
- Memory's retained nearby exploration context, completed shared-exploration context, and spatial Memory API

No release metadata or `update.json` was changed.


## v0.8 Stage 2 Final Session Close

Memory & Social Stage 2 work is fully complete and integration-ready.

**Memory branch:** `memory/v0.8-exploration-stage2`  
**Final head:** `306a9ef4329ab81afa5912846333a1d9782ee9be`  
**Green validation:** `36455394456`

Final upstream contracts confirmed after Memory implementation:

- Simulation: `simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`, CI `36456647323`
- Communication: `communication/v0.8-shared-actions-stage2` @ `7f40053233d0408b315ed6e9840267650503b63b`, CI `36456134638`

Those final contracts match Memory's implemented source model:

- social exchange: `conversations.id`
- Communication proposal: `shared_action_proposals.id`
- canonical physical shared event: `shared_activities.id`
- physical citizen job: `jobs.id`
- validated spatial evidence: `spatial_observations.id`

Simulation's final pre-start `rejected` state remains intention history only and never becomes completed shared-exploration Memory.

No Memory-owned Stage 2 dependency remains. Resume Memory only for coordinator merge conflicts/regressions or a newly authorized milestone.

No release was published and `update.json` was not changed.


## v0.9 Stage 1 Causal Memory Spine — Complete

**Doctrine:** `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`  
**Contract:** `docs/departments/memory/V090_CAUSAL_MEMORY_CONTRACT.md`  
**Base:** `release-v0.8.7` / `be617e6e870ec3f1914d76cdb85107a6efc294d7`  
**Branch:** `memory/v0.9-causal-memory-stage1`  
**Final head:** `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`  
**Validation:** CI `36607115487` passed the complete v0.4-v0.8.7 regression matrix plus `tests/smoke_v090_memory_stage1.py`.

### Durable archive remains authoritative

Existing `memory_events` remains the durable per-citizen archive.

v0.9 does not rewrite or replace:
- source type / source ID
- event time
- event summary
- status / verification
- owner

Aging affects retrieval priority only.

### New causal facet index

Stage 1 adds:

`memory_event_facets(owner_id, memory_event_id, facet_kind, facet_value)`

This is an additive index/projection over real Memory events.

Initial facet families include:
- event kind
- source type
- counterparty
- visitor
- stable subject
- target
- location
- material
- process
- descriptive activity/action type

Future explicit continuity facets may include plan/place identifiers.

Facets are not facts, skills, classes, habits, or reputation.

### Active recall

New module: `agent_city/causal_memory.py`.

Primary internal interfaces:

- `causal_recall_snapshot(owner_id, now_minute=None, facet_filters=None, pinned_event_ids=None, limit=8)`
- `causal_recall_context_for(...)`
- `link_memory_event(memory_event_id, facet_kind, facet_value)`

Active recall is bounded and source-labelled.

Recall priority considers:
- stored event importance
- meaningful aging/recency
- repeated related source-backed experience

Repeated experience can become more retrievable without merging/copying an unbounded transcript.

Reinforcement affects retrieval only. It never changes verification or physical capability.

### Persistent-plan hook

An unfinished plan can preserve its causal reason by retaining the stable `memory_event_id` references that caused/revised the plan.

Those event IDs can be:
- explicitly linked with facet `plan=<plan_id>`
- passed as `pinned_event_ids` during recall

Pinned old memories remain candidate-visible after unrelated work/time passes.

Pinning does not make a plan mandatory. Planner may still continue, revise, pause, supersede, abandon, or complete it.

### Active recall vs forgetting

Low-value old events may fall out of the active packet.

They remain in `memory_events`.

This implements reduced access without rewriting the past.

### Citizen isolation

All recall is owner-scoped.

Another citizen cannot receive plan reasons, practice history, visitor continuity, or social evidence merely because another citizen has it.

### Validation coverage

`tests/smoke_v090_memory_stage1.py` verifies:

- repeated related source-backed events gain retrieval reinforcement
- newer equal-family memories outrank older ones
- repeated unverified claims remain unverified
- old plan reasons survive through explicit pinning
- plan facets remain traceable to real Memory events
- another citizen does not inherit the history
- low-value old events can leave active recall while remaining in durable archive
- recall context remains bounded and source-labelled
- existing v0.4-v0.8.7 behavior remains green

### Downstream handoffs

Simulation INBOX now contains the persistent-plan source interface.

Communication INBOX now contains the perspective-safe recall/self-assessment/recognition contract.

No public HTTP recall-score API was added in Stage 1. Recall score is internal retrieval machinery and must not become a visible identity/reputation/memory-strength label.

No release metadata or `update.json` was changed.


## v0.9 Stage 1 Simulation Contract Consumed — Practice Retention Complete

Memory consumed the final Simulation Stage 1 contract:

- branch `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- CI `36603570434`

Memory branch is now:

- `memory/v0.9-causal-memory-stage1`
- final head `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`
- validation `36607115487`

### Canonical practice retention

New module:

`agent_city/practice_memory.py`

Memory now consumes Simulation `practice_events.id` as canonical evidence that real physical practice occurred.

Policy:

1. if the physical job already has a durable Memory event, reuse that event
2. add practice/activity/plan/location/material/target facets to that existing memory
3. if the job has no durable autobiographical event, create one verified `simulation_practice_event` memory
4. never create practice from talk, agreement, waiting, proximity, UI/admin interaction, or concept art

This avoids double-counting one physical service/survey/shared exploration merely because multiple authoritative ledgers reference it.

### New practice Memory source

When a new event is required:

- `source_type = simulation_practice_event`
- `source_id = practice_events.id`
- `event_kind = practice_<activity_type>`
- owner = `practice_events.citizen_id`
- status = verified

Metadata preserves:
- practice event ID
- physical job ID
- optional plan ID
- activity type
- job status/outcome
- location
- target/material
- project/observation/shared-activity IDs when present

### Outcome continuity

Completed and failed practice are both eligible personal history.

Failure/no-yield may be more salient for future recall but does not create a permanent negative identity label.

### Integration behavior

Memory startup safely no-ops before `practice_events` exists.

After Memory + Simulation merge:
- Simulation creates/backfills canonical practice events
- Memory retains/dedupes them
- causal facets become available to recall
- Simulation plan-source facet backfill links prior plan reasons regardless of merge order

No additional Memory schema beyond `memory_event_facets` is required.

### Validation

CI `36606247505` passed the complete v0.4-v0.8.7 matrix plus the expanded `tests/smoke_v090_memory_stage1.py`.

The expanded smoke verifies:
- unmatched canonical practice creates one verified Memory event
- an already remembered job is not duplicated
- existing event gains a stable `practice_event` facet
- plan/activity practice facets become recallable
- failed physical practice remains source-backed history
- repeated synchronization is idempotent

No release metadata or `update.json` was changed.


### Recall-bound practice interpretation surface

Memory now exposes a model-facing practice bridge that preserves active recall rather than exposing the full durable physical ledger:

- `practice_recall_snapshot_for(citizen_id, activity=None, now_minute=None, limit=8)`
- `practice_recall_context_for(...)`

These surfaces:
- require `practice_event` facets
- remain owner-scoped
- preserve aging/salience
- optionally filter by activity
- hide internal `recall_score`
- hide internal `reinforcement_count`
- preserve source/time/verification/summary

This is the safe source for present self-assessment and teaching/explanation language.

The full `practice_events` ledger remains appropriate for objective diagnostics/history, not direct autobiographical prompt injection.

Final Memory branch head: `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`  
Final Memory validation: `36607115487`
