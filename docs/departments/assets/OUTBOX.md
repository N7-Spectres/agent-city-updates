# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.5 independent compact-chat / History slice ready (draft PR #2)

**Need / Result:**
Implemented the independent Assets portion of v0.5 on `assets/v0.5-making-ui`, based from pinned v0.4.1 commit `4181cbb69809205ae575b3f576836e5ca72c8dce`.

Draft PR #2 now contains:
- bounded visitor chat with internal scrolling
- anchored visitor input / Talk action
- rebalanced wider right-side layout
- History as the default Control Room view beneath Visit
- structured citizen conversation cards with participants / place / sim time / summary / expandable transcript
- explicit chronology-only fallback when an authoritative conversation event exists but its exchange text is not in the current state snapshot

**Files / Interfaces:**
- `static/index.html`
- `static/app.js`
- `static/styles.css`
- reads existing `state.history[].category` and `state.citizen_conversations`

**Verification:**
- 45 DOM IDs / 45 JS references
- no missing or duplicate IDs
- no stale drawer hooks
- JavaScript parses
- 3 commits ahead / 0 behind base

**Important constraints:**
- no physical state was invented
- no backend/simulation behavior changed
- no `update.json` or release metadata changed

**Next action:**
Coordinator may review the independent UI slice now. Do not treat the v0.5 Assets scope as complete until the Simulation schema below is consumed.

### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** Waiting for authoritative Making & Building UI schema

**Need / Result:**
Assets requested the exact v0.5 project/tool/equipment/structure state contract from World & Simulation.

**Files / Interfaces:**
Request is recorded directly in `docs/departments/simulation/INBOX.md`.

**Important constraints:**
Assets will display only validated project/object/structure state and explicit physical modifiers. No frontend inference of construction completion, cargo capacity, extraction bonuses, material consumption, or placement.

**Next action:**
When Simulation hands off the stable field names/lifecycle values, continue on PR #2 / `assets/v0.5-making-ui`.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
