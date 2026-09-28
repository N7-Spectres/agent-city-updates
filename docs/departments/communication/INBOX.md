# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for the active v0.6 Communication slice._

## Waiting for Integration Responses

- final Simulation v0.6 discovery/experiment event shape and any merge notes
- coordinator integration feedback if `main.py`, planner context, or knowledge schema conflicts require reconciliation

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.6 discovery/claim provenance + visitor availability

**Result:**
Implemented and tested on `communication/v0.6-knowledge-provenance`.

Delivered:
- per-citizen information receipt ledger
- validated observation/result ingress for Simulation
- face-to-face claim projection with unverified semantics
- transcript-grounded assertion safeguard
- provenance-backed planner/dialogue context
- per-citizen low-level knowledge endpoint
- structured Visit availability state machine
- initiator/target counterpart bug fixed
- remote state no longer leaks local busy/talk details

Final branch head: `0cd9642c720e2950cb2a50728e19c08092408591`  
Final green CI run: `36420188139`.

## Deferred / Future Depth

- richer verified/contradicted claim reconciliation
- source reliability derived from evidence
- third-party overhearing
- physical written/recorded information channels
- any invented long-distance communication technology

These should resume only when the coordinator activates the relevant milestone.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
