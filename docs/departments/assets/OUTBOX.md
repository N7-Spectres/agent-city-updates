# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** Complete v0.5 Assets branch ready for coordinator integration

**Need / Result:**
The full v0.5 Assets scope is complete on `assets/v0.5-making-ui`, head `71e30d3ca02edc97f5286436bc5ef03f93b77088`, draft PR #2.

Includes:
- compact bounded Visit/chat
- anchored visitor controls
- rebalanced layout
- useful default History view
- canonical conversation ID / physical talk-job linkage display
- legacy chronology-only fallback without invented dialogue
- Making Control Room view consuming authoritative projects, project materials, equipment, and extended structures

**Files / Interfaces:**
- `static/index.html`
- `static/app.js`
- `static/styles.css`
- consumes Simulation branch:
  - `state.projects[]`
  - `state.project_materials[]`
  - `state.equipment[]`
  - extended `state.structures[]`
- consumes Communication contract:
  - canonical conversation `id/source_id`
  - nullable `source_job_id`

**Verification:**
- 47 DOM IDs / 47 JS references
- no missing or duplicate IDs
- no stale drawer hooks
- JavaScript parses
- 7 commits ahead / 0 behind v0.4.1 base
- Simulation branch has no `static/` changes, so direct frontend file overlap is zero

**Important constraints:**
- no frontend-derived project completion, physical modifier, material reservation, or structure existence
- failed talks do not get invented conversation cards
- local coordinates are not treated as free-roam geography
- no `update.json` or release publication changes

**Next action:**
Coordinator should integrate this branch with `simulation/v0.5-making-building` @ `773299189d22d214b3376c72b396015a4a7a762e` and run the assembled v0.5 smoke tests plus UI/runtime checks.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
