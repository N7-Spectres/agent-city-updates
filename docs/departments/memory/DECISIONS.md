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
