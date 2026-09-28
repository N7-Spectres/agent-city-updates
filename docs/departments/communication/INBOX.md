# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None requiring additional Communication-owned code right now._

## Waiting on Upstream Dependency

### 2026-09-28 — From: Communication & Perception — Status: blocked

**Subject:** Simulation canonical shared-activity cancellation

**Need / Result:**
Stage 2 proposal/start/status wiring is complete and tested.

Communication is waiting only for World & Simulation to provide a cancellation/rejection primitive for unstarted canonical `shared_activities.status='proposed'` rows.

Without it, Communication correctly refuses to mark its projection rejected/expired while Simulation still reports the canonical proposal as proposed.

Requested function:
`cancel_shared_activity(conn, activity_id, visitor, now=..., reason=...)`

The request is already in World & Simulation INBOX.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 2 — Shared-action proposals and exploration-aware dialogue

**Result:**
Implemented on `communication/v0.8-shared-actions-stage2`.

Delivered:
- structured proposal object after durable face-to-face exchange
- explicit meter/cardinal target parsing
- Simulation-validated canonical proposal creation
- explicit visitor acceptance
- real physical start only from Simulation job creation
- bounded active progress/status in dialogue context
- safe completion/observation linkage
- Visit proposal API for Assets
- full regression smoke coverage

Final branch head:
`7f40053233d0408b315ed6e9840267650503b63b`

Final green CI:
`36456134638`

Reject/expiry finalization remains fail-closed pending the Simulation cancellation primitive.

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Memory Stage 2 proposal-to-physical source mapping

**Result:**
Final source mapping was handed to Memory:

- `conversations.id` — social exchange
- `shared_action_proposals.id` — Communication proposal projection
- `shared_activities.id` — canonical Simulation shared exploration
- `jobs.id` — active physical job
- `spatial_observations.id` — validated evidence

Memory's completed shared-exploration source plan already matches this contract.

## Deferred Communication Depth

- additional shared activity types after Simulation exposes safe contracts
- richer visitor-claim provenance if justified
- claim contradiction/source reliability
- overhearing / physical records
- emergent place-name propagation
- invented long-distance communication only after real physical invention

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
