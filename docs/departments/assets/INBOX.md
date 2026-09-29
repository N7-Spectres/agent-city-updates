# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: READY / ASSEMBLED BASE GREEN

**Subject:** v0.9 Stage 2 runtime UI base ready

The coordinator assembled Simulation + Memory + Communication Stage 2 onto the green Stage 1 line.

**Authorized Assets runtime base:**
- branch: `release-v0.9.0-stage2-integration`
- head: `ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- combined CI: `36633452433` — PASS

The combined run passed:
- complete v0.4-v0.8.7 regression matrix
- all four v0.9 Stage 1 smokes
- `tests/smoke_v090_simulation_stage2.py`
- `tests/smoke_v090_memory_stage2.py`
- `tests/smoke_v090_communication_stage2.py`

One integration-only test-harness mismatch was corrected: Communication's isolated fake `agent_city.competence` module now supplies the integrated `guided_practice_snapshot(...)` interface. Runtime authority/semantics were not weakened.

**Upstream contracts present on this base:**

Simulation:
- `GET /api/competence/{citizen_id}`
- factual competence-family practice counts and bounded duration effect
- factual guided-practice session history

Memory:
- `GET /api/memory/continuity/{citizen_id}`
- bounded remembered practice/guided-practice perspective
- source role/counterparty/family with recall internals hidden

Communication:
- competence-safe attributed language
- guided-practice/question boundaries
- no hidden other-citizen objective competence lookup

### Planned Assets implementation

- extend existing Continuity UI only
- keep literal practice counts/history primary
- measured duration effect as compact factual text only
- Guided Practice History as event rows
- Memory guided-practice events remain Remembered Perspective
- Communication language remains attributed Interpretation
- no XP/proficiency bars
- no mentor/expert/trainer badges
- no rankings/leaderboards
- no frontend-derived competence

Do not publish `update.json`.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
