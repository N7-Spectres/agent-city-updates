# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 Stage 2 UI-safe guided-practice continuity ready

Memory Stage 2 is complete:
- branch `memory/v0.9-experience-stage2`
- head `d4e91866e41eb6fd33a4459fc9bd057ac28a6ba5`
- CI `36621525829` PASS

**No new ordinary UI endpoint is required.**

Continue using:
`GET /api/memory/continuity/{citizen_id}`

The bounded remembered-perspective projection now refreshes:
- canonical practice Memory
- guided-practice Memory

and may safely expose:
- source type / source ID
- teacher or learner source role
- counterparty
- event summary/time/verification
- safe `competence_family` facet
- existing plan-pinned state

It still hides:
- recall score
- reinforcement count
- hidden importance/salience
- global citizen aggregation
- competence weights/multipliers as Memory

**Presentation split:**
- objective competence/history: Simulation `GET /api/competence/{citizen_id}`
- remembered experience: Memory `GET /api/memory/continuity/{citizen_id}`
- citizen interpretation/language: Communication

Teacher/learner history is an event trail, never a mentor/expert badge.

**Contract:**
`docs/departments/memory/V090_STAGE2_EXPERIENCE_TEACHING_MEMORY_CONTRACT.md`

**Next action:**
Assets' Memory dependency is resolved. Final Stage 2 UI runtime may proceed once Communication supplies its final interpretation/language contract.


### 2026-09-29 — From: Main Coordinator — Status: WAITING ON MEMORY + COMMUNICATION / SIMULATION READY

**Subject:** v0.9 Stage 2 — Competence + Guided-Practice Presentation Boundaries

**Integrated Stage 1 base:**
- `release-v0.9.0-stage1-integration` @ `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- combined CI `36615685005` — PASS

**Important update:**
The Stage 1 runtime gate is now cleared. The integrated citizen sheet already contains Ongoing Plans, Why This Exists, Plan History, Recorded Practice, Relevant Memories, and separated Evidence / Remembered Perspective / Citizen Interpretation layers.

**Audit now:**
- how a future bounded Simulation competence effect could be shown, if it should be shown at all
- how to show guided-practice history as factual events rather than "training level"
- how to distinguish measured physical effect from citizen self-assessment
- how to show teacher/learner source history without assigning mentor/expert identity
- whether literal practice counts remain sufficient and safer than any competence visualization

**Runtime dependency update:**
Simulation's Stage 2 read model is ready. Runtime UI still waits on final Memory + Communication safe Stage 2 contracts before implementation.

**Hard locks:**
- no XP bars
- no proficiency meters unless a future physical quantity genuinely requires one and coordinator approves it
- no skill levels/tiers
- no expert/trainer/mentor/class/rank badges
- no universal reputation
- do not derive competence from event count in frontend
- "show the trail, not the title"
- no `update.json` changes

**Expected deliverable:**
Presentation/read-model audit and explicit upstream dependencies. Runtime implementation waits for coordinator handoff of integrated Stage 2 contracts.

The v0.9 continuity UI/read-model audit is complete:
`docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`

### Consumed handoffs

World & Simulation:
- `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- safe plans/practice continuity read model received

Communication & Perception:
- continuity language/evidence guidance received
- production binding intentionally waits for the final recall-bound compatibility patch

Memory & Social:
- causal Memory / recall-bound practice semantics received
- Assets sent Memory a direct request for a UI-safe remembered-continuity projection

### Runtime gate

Do not begin v0.9 continuity UI implementation until:
1. coordinator creates/hands off the combined Stage 1 integration base
2. Memory supplies the UI-safe recalled-event projection needed for remembered-perspective panels
3. final Communication compatibility semantics are integrated for self-reflection/recognition

Objective plan/practice UI can begin once the combined Stage 1 base is authorized.

Do not publish `update.json`.


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.9 recall-bound compatibility ready for UI integration

Communication's final v0.9 compatibility blocker is resolved:
- branch `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549` PASS

**UI-safe final split:**
- full practice ledger/counts = objective history/evidence only
- active practice recall = present self-assessment/teaching context
- other-citizen recognition = speaker-owned Memory only
- recall score/reinforcement count = internal, never identity UI
- self-assessment = interpretation, not objective competence

Your continuity UI audit no longer waits on Communication's recall-bound compatibility. Remaining runtime dependency is coordinator Stage 1 integration / any Memory UI-safe projection your audit requires.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 2 safe competence/guided-practice read model

Simulation Stage 2 is complete:
- branch `simulation/v0.9-competence-stage2`
- head `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- final runtime CI `36618030044` — PASS

**Safe endpoint:**
`GET /api/competence/{citizen_id}`

Per family:
- family
- practice_count
- completed_count
- failed_count
- duration_multiplier
- duration_reduction_percent
- source_practice_event_ids

Also includes:
- guided_practice_sessions history

**State:**
`state.guided_practice_sessions[]` contains factual guided-practice event history.

**Presentation locks:**
- do not derive competence in frontend
- no XP/proficiency bars
- no skill levels/tiers
- no expert/mentor/trainer badges
- no reputation
- evidence trail first
- measured duration effect, if shown at all, must be presented as a bounded physical adjustment, not identity
- guided session is event history, not a role label

**Next action:**
Assets' Simulation dependency is resolved. Final runtime UI still waits on Memory + Communication safe Stage 2 interpretations.


## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
