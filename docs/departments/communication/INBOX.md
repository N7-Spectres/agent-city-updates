# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for the active v0.5 conversation-integrity slice._

## Deferred / Future Depth

### 2026-09-28 — From: Memory & Social — Status: deferred

**Subject:** Expose runtime provenance records for claim memory

**Need / Result:**
Memory eventually needs claim-level provenance fields from `PROVENANCE_CONTRACT.md`: recipient/source actor, specific topic/value, channel/assertion kind, transfer/source IDs, received/observed time, and verification state.

**Current result:**
v0.5 now exposes a stable conversation-level physical source:
- canonical `citizen_conversations.id`
- `source_job_id` for new source-linked physical talks
- stable time/location/participants/text/summary

Individual claims are **not** extracted yet. The current project state explicitly keeps richer provenance as later depth.

**Important constraints:**
- repeated retelling must not verify a claim
- no remote knowledge without a real mechanism
- canonical raw conversation IDs must remain stable

**Next action:**
Resume this only when the coordinator activates the deeper provenance/last-known slice.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.5.0 conversation-history integrity

**Result:**
Implemented/tested on `communication/v0.5-history-integrity`. New stored talks are physically source-linked, idempotent, and completion-safe. A talk cannot succeed in chronology without a matching stored exchange.

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Preserve canonical conversation source ID for Memory

**Result:**
`citizen_conversations.id` remains the canonical immutable Memory source. `source_type/source_id` are exposed without renumbering. New `source_job_id` is supplementary and does not replace Memory's existing source key.

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Full runtime source located

**Result:**
The v0.5 implementation used the current shipped `release-v0.4.1` lineage requested by the coordinator, which already contains the complete runtime and Memory integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
