# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.8 Stage 1 Assets foundation ready for coordinator review

**Need / Result:**
Stage 1 independent Assets work is complete on:

- branch `assets/v0.8-visual-stage1`
- head `af2e058780103755360d143ca964855145e2254a`
- PR #11, ready for review

Delivered runtime groundwork:

- active-job progress restored to Home citizen rows
- elapsed / total / remaining / ETA from authoritative job timing
- Enter-to-send
- Shift+Enter newline
- IME-safe chat keyboard handling
- duplicate-submit guard
- six explicit citizen visual profiles
- refined silhouette fallback architecture
- head-expression asset slots
- empty modular equipment-layer slots

Delivered architecture:

- `V080_CITIZEN_VISUAL_SYSTEM.md`
- `V080_ASSET_WORKER_CONTRACT.md`
- persistent spec/job identity design
- render tiers
- provenance/fallback rules
- asynchronous no-Simulation-blocking worker contract

Validation:

- 71 HTML IDs
- 67 JS DOM refs
- zero missing/duplicate IDs
- JavaScript parses
- all Stage 1 contract checks pass
- 6 commits ahead / 0 behind v0.7.0

**Important constraints:**
- no continuous coordinate invention
- no concept-art gear becomes inventory
- no Simulation quantity changes from rendering aggregation
- no Blender dependency yet
- no full 3D generation yet
- no `update.json` changes

**Next action:**
Coordinator reviews Stage 1 foundation. Continuous-world UI work resumes only after Simulation publishes the safe seeded spatial read model.

### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** Safe seeded spatial read model needed for later continuous-world UI

Assets sent the exact UI/render consumer contract to World & Simulation INBOX.

The request covers safe coordinates, reference frame, landmark anchors, stable generated subject identity, observation precision/extent, and repeat-encounter semantics without exposing hidden seed/chunk truth.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
