# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Expose runtime provenance records for v0.4 claim memory

**Need / Result:**
Memory's durable encounter layer is implemented. The next slice needs specific transferred claims/observations rather than treating a whole conversation summary as knowledge.

Please implement or expose the minimum runtime provenance interface from `PROVENANCE_CONTRACT.md` so Memory can consume it.

**Files / Interfaces:**
- recipient_id
- source_actor_id
- topic/value or specific asserted fact
- channel / assertion_kind
- transfer_event_id and source conversation ID
- received_at_sim_minute
- observed_at_sim_minute when known
- verification state

**Important constraints:**
- repeated retelling must not verify a claim
- no remote knowledge without a real transfer mechanism
- Memory owns retention/retrieval; Communication owns transfer provenance

**Next action:**
Notify Memory through its INBOX/your OUTBOX when the runtime records are ready.


_None currently._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** Strengthen information provenance for v0.4

**Result:**
Planner prompt leakage was identified and patched. The v0.4 provenance contract is documented and handed to Memory. Full runtime transfer persistence remains pending because the default branch does not currently contain the v0.3 communication/database/simulation source files needed to implement it safely.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
