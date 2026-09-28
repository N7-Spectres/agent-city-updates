# Memory & Social — State

_Last updated: 2026-09-28_
_Current release: v0.5.0_
_Current development branch: `memory/v0.4-social-memory-core`_

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

### Communication & Perception

Needed next:

- runtime provenance records for specific communicated claims
- stable transfer/exchange source IDs
- verification state for received information
- last-known source/age data suitable for Memory retrieval

### World & Simulation

Needed next:

- stable validated event IDs / participants for cooperation, help, and other physical social outcomes
- enough event metadata to link a Memory record to what physically happened

Neither dependency blocks conversation familiarity, which is already implemented.

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
