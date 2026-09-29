# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-29 — From: Assets & Interface — Status: WAITING ON COORDINATOR ASSEMBLY

**Subject:** v0.9 Stage 2 runtime UI base required

The Stage 2 presentation/read-model audit is complete:
`docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`

All upstream department contracts are final:

Simulation:
- `simulation/v0.9-competence-stage2`
- head `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- `GET /api/competence/{citizen_id}`

Memory:
- `memory/v0.9-experience-stage2`
- head `d4e91866e41eb6fd33a4459fc9bd057ac28a6ba5`
- `GET /api/memory/continuity/{citizen_id}`

Communication:
- `communication/v0.9-guided-practice-stage2`
- head `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`
- final competence-safe interpretation/guided-practice language contract

### Runtime gate

No assembled Stage 2 integration branch currently exists.

Assets must not merge upstream department branches itself.

Coordinator must first assemble Simulation + Memory + Communication Stage 2 onto:
`release-v0.9.0-stage1-integration@de5f2d87b0f77610c95e0016efdb7ca5a9206e22`

Then hand Assets the resulting green Stage 2 base.

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
