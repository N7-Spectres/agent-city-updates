# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.7 independent Home scaling + avatar framework ready

**Need / Result:**
Implemented the independent v0.7 Assets slice on `assets/v0.7-home-avatars`, head `e0daf26a4249584d1560c7aea06b29cd1b5818fb`, draft PR #7.

Delivered:
- desktop full-height citizen/world/Visit alignment
- internal citizen scrolling
- citizen name search/filter
- full-height internally scrolling chat
- compact five-item Recent Activity
- View all history → Records/History
- stored-conversation-only conversation summaries
- failed-talk events remain events
- lightweight 2D avatar asset manifest
- Citizens full-body fallback identity
- matching Home/directory/map avatar tokens
- validated-state idle/travel/charge/talk/work animation
- reduced-motion support
- Assets smoke test: `tests/smoke_v070_assets.py`

**Verification:**
- 69 HTML IDs
- 65 JS DOM references
- no missing referenced IDs
- no duplicate IDs
- JavaScript parses
- 4 commits ahead / 0 behind v0.6.0 base

**Important constraints:**
- no physical equipment/wear/damage appearance invented
- no maintenance thresholds guessed
- no `update.json` or release publication changes

**Next action:**
Resume PR #7 when Simulation hands off the v0.7 maintenance/condition schema.

### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** Waiting for authoritative v0.7 maintenance presentation fields

**Need / Result:**
Assets sent a direct request to World & Simulation INBOX for equipment/structure/battery-health condition semantics and meaningful degradation thresholds/event anchors.

**Next action:**
Simulation should reply through OUTBOX and/or Assets INBOX when the maintenance state contract is stable.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
