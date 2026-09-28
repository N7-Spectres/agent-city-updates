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


## v0.5.0 — Project Continuity

### Audited / ready

- [x] verify durable conversation memory is linked to raw `citizen_conversations.id`
- [x] verify raw conversation source retains participants, time, location, utterances, and summary
- [x] verify bounded social context labels conversation content as claims, not automatic physical facts
- [x] define discussion/intention vs validated physical-outcome separation
- [x] confirm current `memory_events` schema can carry future project links without schema expansion
- [x] avoid creating a speculative v0.5 Memory runtime branch before project/event interfaces exist

### Waiting on Communication

- [ ] confirm/finalize conversation-history persistence path
- [ ] preserve stable canonical conversation source ID
- [ ] expose explicit mapping if a new transfer/provenance record supplements the raw conversation
- [ ] ensure invalidated/failed talk never produces a false conversation/transfer source

### Waiting on Simulation

- [ ] stable project ID
- [ ] stable validated project-event/job ID
- [ ] project state transitions sufficient to distinguish planned/reserved/underway/completed/failed/cancelled
- [ ] participant/owner IDs where socially relevant
- [ ] validated outcome type and simulation minute

### After interfaces arrive

- [ ] add minimal project-intention memory helper using existing `memory_events`
- [ ] add validated project-outcome memory helper using existing `memory_events`
- [ ] link intention and outcome through validated project ID in metadata where useful
- [ ] keep promise/cooperation/help success memory disabled until outcome semantics justify it
- [ ] add bounded project-relevant retrieval only if planner/context needs it


### Session handoff

- [x] v0.5 Memory audit and source-link contract handed off to coordinator
- [x] Communication dependency placed in Communication INBOX
- [x] Simulation dependency placed in Simulation INBOX
- [x] Memory runtime branch intentionally deferred pending stable interfaces
- [ ] resume only after Communication and/or Simulation replies arrive


## v0.6 Location Knowledge

- retain discovered location facts with source/provenance where Simulation/Communication expose them
- support bounded retrieval of what a citizen actually knows about a location
- keep unknown world truth out of memory/UI context
- support gradual accumulation of location summaries as new surveys, experiments, and communicated facts arrive
- avoid treating a single conversation claim as verified location truth unless later validated


## v0.6.0 — Location / Research Knowledge

### Implemented on `memory/v0.6-location-knowledge`

- [x] reuse `memory_events` instead of adding a speculative knowledge table
- [x] durable personal survey/discovery memories with source/time
- [x] idempotent sync of newly validated personal survey discoveries
- [x] bounded retrieval by citizen/location/material/process
- [x] verified vs unverified labeling
- [x] bounded planner-facing local knowledge context
- [x] safe citizen knowledge API
- [x] safe location notebook API partitioned by citizen
- [x] focused v0.6 Memory smoke test

### Simulation v0.6 contract received

- [x] stable `discoveries.id`
- [x] stable `experiment_results.id`
- [x] subject/location/material/property metadata
- [x] validated discovery and experiment outcome semantics
- [x] citizen-scoped validated knowledge through `citizen_knowledge`

### Communication v0.6 contract received

- [x] `information_receipts` provenance shape
- [x] canonical conversation/transfer source mapping
- [x] recipient/source actor/received time/assertion kind/verification
- [x] unverified face-to-face claim semantics
- [x] verified Simulation-knowledge synchronization rules

### Coordinator integration follow-up

- [ ] merge Simulation + Communication + Memory while preserving separate layer ownership
- [ ] map Simulation discovery/experiment anchors beneath Memory retrieval without importing hidden truth
- [ ] map Communication receipts/claims beneath Memory retrieval without automatic verification
- [ ] keep Memory Citizen/Location APIs bounded and per-citizen
- [ ] run combined v0.6 smoke suite including Memory `tests/smoke_v060_memory.py`


### v0.6 session close

- [x] Memory runtime branch complete
- [x] Memory CI green
- [x] Assets read-model handoff delivered
- [x] Simulation final contract received
- [x] Communication final contract received
- [x] no remaining department-owned v0.6 implementation blocker
- [ ] coordinator integration and combined release smoke


## v0.7.0 — Maintenance Continuity

### Audited / ready

- [x] audit v0.6 Memory/event model
- [x] confirm existing `memory_events` can store maintenance history without a new table
- [x] define maintenance salience/noise policy
- [x] define physical-truth vs citizen-knowledge boundary
- [x] avoid speculative runtime branch before Simulation event semantics exist

### Simulation v0.7 contract received

- [x] stable source: `maintenance_events.id`
- [x] physical job anchor: `job_id`
- [x] actor citizen ID
- [x] target type + target ID
- [x] event type semantics
- [x] before/after values
- [x] materials / outcome / sim minute / summary
- [x] microscopic wear intentionally excluded from the event ledger

### Next Memory session

- [ ] create `memory/v0.7-maintenance-history` from `release-v0.6.0`
- [ ] add idempotent maintenance-event ingestion using existing `memory_events`
- [ ] record memories only for citizens with a valid experience/information path
- [ ] add bounded maintenance history retrieval by citizen/subject
- [ ] expose minimal read model for Assets Citizen/History surfaces if useful
- [ ] add smoke tests ensuring passive wear does not flood Memory
- [ ] preserve all v0.4-v0.6 social/knowledge/provenance regressions


### v0.7 session close

- [x] maintenance-memory architecture audit complete
- [x] salience/noise policy locked
- [x] Simulation stable event contract received
- [x] Assets presentation guidance handed off
- [x] no stale dependency remains
- [ ] runtime ingestion/read-model implementation begins next Memory session


### Immediate resume order

1. create `memory/v0.7-maintenance-history` from `release-v0.6.0`
2. inspect final `simulation/v0.7-maintenance` schema at `54f5d838f674d0b278a51382f3a880cc0738b417`
3. ingest `maintenance_events.id` idempotently into existing `memory_events`
4. preserve actor/target/source/job/before-after/material/outcome metadata
5. add bounded subject-specific maintenance retrieval
6. add `tests/smoke_v070_memory.py`
7. run all Memory/regression smoke tests
8. only then mark the coordinator request handled and move Memory to REVIEW
