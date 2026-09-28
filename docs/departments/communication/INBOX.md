# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for the active v0.7 Communication slice._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.7 autonomous talk reliability

**Result:**
Implemented and tested on `communication/v0.7-talk-reliability`.

Delivered:
- raw-exchange-first two-phase conversation flow
- one bounded retry for raw structured dialogue
- tolerant JSON-object recovery without synthetic fallback text
- non-fatal claim/provenance enrichment
- `talk_diagnostics` failure/retry/degraded/success ledger
- separate concise History diagnostic for hard failed talks
- failure-code separation for model/network/schema/physical/persistence/claim paths
- lock-safe diagnostic lookup during Simulation completion

Final branch head: `61eecc4c047dd3fd22b71612251769a8cb456737`  
Final green CI: `36428495003`.

All v0.4/v0.5/v0.6 regression suites plus `tests/smoke_v070_communication.py` passed.

## Deferred / Future Depth

- live diagnostic aggregation/admin summary
- claim-enrichment retry/backfill after degraded projection
- measured model/timeout tuning based on post-release diagnostics
- claim contradiction/reliability semantics
- overhearing / physical records / invented remote communication

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
