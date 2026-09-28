# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.6 independent Home / Citizens / Locations / Records shell ready

**Need / Result:**
Implemented the independent v0.6 information-architecture pass on `assets/v0.6-knowledge-ui`, head `280417e7361d888c7bd740c80f436493a13d85a1`, draft PR #3.

Delivered:
- simplified map-centered Home
- compact citizen quick rows
- compact visitor location badge
- dedicated Citizens character sheets
- dedicated Locations field notebook
- dedicated Records view for Making / Stores / History / Region / Updates
- placeholder-safe citizen/location visual slots
- existing discovered resources only
- specific backend visit accessibility reason instead of generic wording

**Verification:**
- 65 HTML IDs
- 60 JS DOM references
- no missing referenced IDs
- no duplicate IDs
- JavaScript parses
- 4 commits ahead / 0 behind v0.5.0 base

**Important constraints:**
- this is not the final v0.6 knowledge UI
- no hidden Simulation truth was intentionally exposed
- no appearance/environment art was invented
- no `update.json` or release metadata changes

**Next action:**
Resume PR #3 after the three knowledge contracts arrive.

### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** Waiting for v0.6 safe read models

**Need / Result:**
Assets sent direct dependency requests to:
- World & Simulation INBOX — knowledge-safe world/location state + cargo capacity
- Communication & Perception INBOX — visit-status/provenance contract
- Memory & Social INBOX — bounded citizen/location knowledge read model

**Next action:**
Owning departments should reply through their OUTBOX and/or Assets INBOX with exact field/endpoint shapes.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
