# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** Lead v0.4.0 Memory & Relationships architecture

**Need / Result:**
Design the core v0.4.0 social-memory system around behavior already emerging naturally. Focus on durable interaction history, familiarity, cooperation, disagreement, promises, help, and information-source reliability without turning relationships into arbitrary RPG scores.

**Files / Interfaces:**
- inspect current conversations / citizen_conversations / visits schema
- propose or implement a bounded event-memory model
- identify the exact simulation/communication fields needed from other departments

**Important constraints:**
- conversation claims are not physical truth
- full history may remain archived, but LLM context must stay bounded
- preserve current citizen continuity and existing v0.3.0 data

**Next action:**
Read department state/decisions/backlog, inspect the current implementation, then produce the recommended v0.4 architecture and write any cross-department dependencies to the relevant inboxes.

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Provenance interface ready for v0.4 Memory

**Need / Result:**
Use `docs/departments/communication/PROVENANCE_CONTRACT.md` as the source/age/verification boundary for remembered information. Communication distinguishes personal experience, direct observation, and face-to-face claims. A communicated claim remains unverified until a separate physical verification path exists.

**Files / Interfaces:**
- `docs/departments/communication/PROVENANCE_CONTRACT.md`
- fields: recipient, subject/topic/value, channel, source actor, origin event, transfer event, observed/received sim minute, assertion kind, verification
- planner no longer receives live remote citizen state or settlement-wide deposits by default

**Important constraints:**
- summaries do not imply every underlying fact was transferred
- repeated retelling does not convert a claim into physical truth
- legacy summaries should not be retroactively given fabricated precise provenance

**Next action:**
Derive bounded last-known and social-memory retrieval from provenance records while keeping archived event history intact.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
