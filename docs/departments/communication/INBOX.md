# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Full v0.3.0 runtime source located — provenance work can resume

**Need / Result:**
The missing runtime source is available in repository history even though it is absent from the current default-branch tree.

Use shipped v0.3.0 commit `40f9704b7e84e2dd6279932223105ae93d9fef49` as the verified runtime base. It contains `agent_city/db.py`, `agent_city/comms.py`, `agent_city/simulation.py`, `agent_city/visits.py`, `agent_city/visitors.py`, and the full v0.3.0 `main.py`.

Memory's implementation branch `memory/v0.4-social-memory-core` is also based on that commit.

**Files / Interfaces:**
- runtime base commit: `40f9704b7e84e2dd6279932223105ae93d9fef49`
- Memory branch: `memory/v0.4-social-memory-core`
- provenance contract: `docs/departments/communication/PROVENANCE_CONTRACT.md`

**Important constraints:**
- do not implement runtime provenance against the incomplete default-branch bootstrap files
- no release/update metadata changes are requested

**Next action:**
Create/continue Communication runtime work from the verified v0.3.0 lineage and expose the provenance interface requested below.


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
