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

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
