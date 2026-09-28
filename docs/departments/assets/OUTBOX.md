# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.4 Control Room + map readability pass ready for runtime review

**Need / Result:**
Implemented the substantial interface pass on branch `assets-v0.4-control-room`, based from `release-v0.3.0`.

The right side now keeps Visit visible and adds a persistent utility Control Room for Region / Stores / Structures / History / Updates. The bottom drawer is removed on the branch.

The map now uses existing route distances for relative spacing, labels route lengths, highlights the selected citizen's active route, uses initial-bearing citizen tokens and compact location clusters, and separates visitor/location/citizen presentation zones.

**Files / Interfaces:**
- `static/index.html`
- `static/app.js`
- `static/styles.css`
- reads existing `state.routes[].distance_km`, citizen jobs, visitor presence, locations, deposits, and inventories

**Important constraints:**
- no simulation-owned rules changed
- no `update.json` or release publication changed
- static structural checks passed, but a real browser/runtime test is still required

**Next action:**
Coordinator or runtime-capable task should test the branch in the running app. If visual/runtime behavior is sound, incorporate it into the next coordinated release branch.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
