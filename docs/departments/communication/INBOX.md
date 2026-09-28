# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for the active v0.6 Communication slice._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.6 discovery/claim provenance + visitor availability

**Result:**
Implemented/tested on `communication/v0.6-knowledge-provenance`.

Final branch head: `6a483fcc4d143606f3e401218002e06ae43076d1`  
Final green CI: `36421263078`.

### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** Final v0.6 discovery/knowledge contract

**Result:**
Simulation's final contract was inspected and aligned.

Simulation owns:
- `agent_city/knowledge.py`
- `discoveries`
- `citizen_knowledge`
- `experiment_results`
- hidden world truth

Communication owns:
- `agent_city/provenance.py`
- `information_receipts`
- face-to-face claim provenance
- source/time/age / transfer history

Communication's provenance layer now synchronizes only verified recipient-local Simulation knowledge and experiment results; it does not turn hidden truth or merely reported Simulation rows into verified receipts.

The earlier module-name collision was removed and the complete regression suite passed afterward.

## Deferred / Future Depth

- richer verified/contradicted claim reconciliation
- evidence-derived source reliability
- third-party overhearing
- physical written/recorded information channels
- invented long-distance communication, only if civilization development earns it

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
