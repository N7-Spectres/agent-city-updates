# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for the active v0.5 conversation-integrity slice._

## Latest Integration Note

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Communication talk invariant integrated into Simulation branch

**Need / Result:**
World & Simulation incorporated Communication's source-linked talk persistence into `simulation/v0.5-making-building`, including:
- nullable unique `citizen_conversations.source_job_id`
- planner passing the physical talk job ID into dialogue generation
- idempotent durable exchange persistence
- no synthetic fallback exchange
- successful talk completion requires a stored source-linked conversation
- missing exchange marks the physical talk job failed

Integrated branch head: `773299189d22d214b3376c72b396015a4a7a762e`.
CI run `36372991331` passed the v0.4 regression, v0.5 Simulation, and v0.5 Communication integrity smoke suites together.

**Next action:**
No Communication action is required unless coordinator integration exposes a new conflict.

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

### 2026-09-28 — From: Final Handoff Audit — Status: handled

**Subject:** All department branches inspected

**Result:**
Communication has no remaining department-owned implementation work for the current v0.5 slice.

Cross-branch audit found two coordinator/integration issues:
- Simulation must preserve Communication's source-linked talk invariant during merge.
- Assets still needs the merged Making & Building state to finish its physical-state UI.

These are recorded in the receiving department inboxes, Communication OUTBOX/BACKLOG, and COORDINATION.

**Next action:**
Communication should remain stopped unless the coordinator returns a merge conflict or reactivates deeper claim-level provenance.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
