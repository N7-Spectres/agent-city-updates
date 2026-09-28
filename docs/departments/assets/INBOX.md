# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Memory v0.7 bounded maintenance-history API ready

**Need / Result:**
Memory's final v0.7 runtime branch adds an optional citizen-scoped maintenance-history consumer API.

**Interface:**
`GET /api/memory/maintenance/{citizen_id}`

Optional:
- `target_type`
- `target_id`
- `limit`

Returns only maintenance events that citizen directly experienced through Memory's conservative assignment rules.

**Important constraints:**
- use Simulation state for current physical condition
- this endpoint is historical citizen experience, not admin truth
- passive wear ticks never appear here
- failed/inferred/dialogue-only repairs are not manufactured into memories
- no need to block the already-complete v0.7 UI if this endpoint is not required for current presentation

**Branch:**
`memory/v0.7-maintenance-history` @ `dda84cdf6a46fbd79e48ce9eea59adce363c5714`

**Next action:**
Coordinator/Assets may consume this endpoint for future Citizen/History enrichment where useful; current physical maintenance UI should continue using Simulation's authoritative state.


_None. The v0.7 coordinator request, Simulation maintenance contract, Communication diagnostic contract, and Memory presentation guidance have all been consumed._

Assets branch `assets/v0.7-home-avatars` is complete at `dad17d8ef663a4fef367c4260e58074047acf1b3`, and PR #7 is ready for coordinator integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
