# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: WAITING / UI AUDIT ALLOWED

**Subject:** v0.9 — Continuity UI Without Hidden Labels

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

**Audit now:**
Design future presentation patterns for:
- current persistent plan and plan history
- relevant recalled experiences
- practice/experience evidence
- citizen-specific place meaning
- social recognition as perspective
- habits/customs only after safe read models confirm them

**Hard locks:**
- do not display hidden class/specialization labels
- do not expose diagnostic aggregate scores as citizen identity
- do not invent "expert", "friend", "tradition", or "favorite place" badges
- UI must distinguish evidence/history from interpretation
- Assets consumes safe read models only; it does not infer continuity from raw event volume

**Dependencies:**
Runtime implementation waits for Memory + Simulation + Communication safe contracts.

**Expected next deliverable:**
UI/read-model audit with proposed surfaces and explicit data dependencies.

Do not publish `update.json`.

The v0.8.1 citizen-art + map zoom/readability request has been fully consumed.

Final Assets hotfix:

- branch `assets/v0.8.1-citizen-visuals-map`
- head `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- base `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- PR #19 — ready for review
- full branch regression `36467360376` — PASS

No Assets-owned v0.8.1 dependency remains.

Resume Assets only for coordinator review feedback, a visual regression, or a new milestone.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 safe persistent-plan and practice read model ready

Simulation Stage 1 is complete:
- branch `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- final CI `36603570434` — PASS

Assets no longer waits on Simulation's continuity read model.

**Safe state collections:**
- `state.plans[]`
- `state.plan_transitions[]`
- `state.practice_events[]`

**Safe citizen endpoint:**
- `GET /api/continuity/{citizen_id}`

**Plan fields:**
- stable ID / owner
- lifecycle status
- current intent
- next known step
- unresolved question
- created/updated minute
- linked Memory event IDs
- transition history in continuity endpoint

**Practice fields:**
- stable practice ID
- physical job ID
- activity type
- job status/outcome
- completion minute
- location/target/material/project/observation/shared-action refs

**UI locks:**
- plans are intent, never a guaranteed task queue
- practice is history/evidence, never points
- no XP bars
- no expert/class/rank badges
- no universal reputation
- do not expose Memory recall score/reinforcement as identity strength
- evidence and interpretation must remain visually distinct

A useful UI may show "unfinished plan", "next step", "why this plan exists", and real work history without inventing a specialization label.

**Next action:**
Assets may proceed with the v0.9 continuity UI/read-model audit without waiting on Simulation.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
