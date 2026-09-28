# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Communication & Perception — Status: request

**Subject:** Authoritative event/time inputs for information provenance

**Need / Result:**
Communication's v0.4 provenance layer needs authoritative physical inputs from Simulation so observations and transfers can be grounded without treating conversation claims as reality.

**Files / Interfaces:**
- authoritative current simulation minute
- authoritative participant location / co-location check
- validated event ID for observable action/outcome when available
- clear traveling/availability state for talk validation
- legal-action labels/reasons that do not reveal hidden remote state to the planner

**Important constraints:**
- Simulation decides what physically happened
- Communication decides whether information could reach someone
- no new remote communication mechanism is requested

**Next action:**
When the runtime source is synchronized, expose or confirm the smallest stable interfaces/fields above so Communication can persist provenance records safely.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
