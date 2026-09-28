# Memory & Social — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_
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
