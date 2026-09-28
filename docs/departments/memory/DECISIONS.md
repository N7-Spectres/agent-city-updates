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
