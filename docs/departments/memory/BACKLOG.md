# Memory & Social — Backlog

## v0.4.0 Core

### Implemented on `memory/v0.4-social-memory-core`

- [x] durable per-citizen memory-event schema
- [x] directional relationship projection
- [x] familiarity based on actual recorded encounters
- [x] source-based deduplication
- [x] idempotent backfill of existing citizen conversations
- [x] bounded relationship retrieval during autonomous planning
- [x] bounded relationship retrieval during dialogue
- [x] preserve raw conversation archive and source IDs

### Next

- [ ] cooperation history from validated Simulation events
- [ ] disagreement history from safely classified interaction evidence
- [ ] remembered promises / commitments with lifecycle
- [ ] remembered help given/received
- [ ] information-source reliability over time
- [ ] specific claim memories using Communication provenance
- [ ] relevant visitor long-term memories beyond per-visit rolling summaries
- [ ] relationship-history API for Assets/UI

## Memory Architecture

- [x] define event-memory schema for social encounter foundation
- [x] separate raw source history from derived relationship state
- [x] avoid duplicate memories
- [x] preserve source references/IDs
- [x] bound model-facing social context
- [ ] integrate Communication provenance records
- [ ] define claim verification/contradiction update path
- [ ] add significance/importance rules for non-conversation events
- [ ] add long-horizon compaction policy once memory volume becomes meaningful
- [ ] consider semantic retrieval only if deterministic relational/recency retrieval becomes insufficient

## Social Consequences

Explore how prior interactions influence:

- who a citizen approaches
- whose information they seek
- who they prefer to cooperate with
- whether they verify someone else's claim
- whether they follow up on promises

Current v0.4 slice allows repeated encounter history to enter planning naturally but does not hard-code social choices.

## Dependencies

### Communication & Perception

Waiting for runtime provenance/transfer records that Memory can consume:

- recipient
- source actor
- topic/value or specific claim
- transfer event ID / source conversation ID
- received simulation time
- assertion kind
- verification state
- source age / last-known semantics

### World & Simulation

Need stable validated event references for physical social outcomes such as:

- shared/cooperative work
- assistance
- promise fulfillment outcomes
- later verification/contradiction evidence

## Conversation History Visibility

- ensure durable citizen conversation memories remain linked to their raw conversation source
- support History/UI access to concise conversation summaries and transcripts without promoting claims into physical truth
- preserve enough source metadata to diagnose a chronology entry that says a conversation occurred but has no visible content card

## UI Requests for Assets

Future Memory/Relationships view may need:

- relationship history
- important shared events
- recent interactions
- source/provenance for remembered information
- no simplistic leaderboard or friendship meter unless evidence later justifies a specific visualization

## Open Questions

- What threshold should promote an ordinary memory into a long-lived summarized relationship milestone?
- Should disagreement classification be deterministic/structured, LLM-assisted with conservative validation, or deferred until interactions become richer?
- How should visitor memories be represented alongside citizen-to-citizen relationships without assuming every visitor statement is factual?


## Integration / Release Readiness

Before v0.4 can be considered release-ready:

- [ ] runtime-test `memory/v0.4-social-memory-core` against an existing v0.3.0 SQLite save
- [ ] confirm conversation backfill is idempotent across repeated startups
- [ ] confirm new conversations create exactly two participant memories
- [ ] confirm relationship counts do not inflate from retrieval or restart
- [ ] confirm bounded prompt size under growing conversation history
- [ ] confirm no conversation summary is treated as authoritative physical state
- [ ] integrate Communication provenance once delivered
- [ ] integrate Simulation event references once delivered
- [ ] decide/reconcile runtime branch lineage before assembling the v0.4 release package
- [ ] expose relationship-history API only after core runtime behavior is verified
