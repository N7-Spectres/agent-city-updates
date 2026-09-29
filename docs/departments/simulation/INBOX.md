# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: READY / PRIMARY v0.9 STAGE 2 DEPENDENCY

**Subject:** v0.9 Stage 2 — Practice → Bounded Competence + Real Guided Practice

**Integrated base:**
- branch: `release-v0.9.0-stage1-integration`
- green head: `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- combined CI: `36615685005` — PASS
- all v0.4-v0.8.7 regressions + all four v0.9 Stage 1 smokes passed together

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`
- `docs/departments/COORDINATION.md`
- current Simulation STATE / DECISIONS / BACKLOG

**Stage 2 goal:**
Determine the smallest physically grounded mechanism by which repeated real practice can produce bounded differences in capability, and define any real guided-practice/teaching action needed for one citizen to help another learn through doing.

**Audit before implementation:**
- which completed/failed `practice_events` legitimately contribute to competence
- whether competence should be derived on demand or persisted as a source-linked projection
- activity boundaries so extraction practice does not magically improve unrelated fabrication/construction
- diminishing returns / bounded effect sizes
- how failures contribute useful experience without becoming permanent weakness
- how recency/tool/material/environment differences should or should not matter
- how maintenance/energy/integrity constraints remain dominant where appropriate
- what a real guided-practice event would physically require: co-presence, legal task, teacher/learner roles, actual job/outcome, and source IDs
- whether teaching needs any competence transfer bonus at all, or simply better learner practice conditions

**Hard locks:**
- no XP, levels, skill trees, classes, professions, ranks, titles, or permanent specialization field
- no competence from conversation, agreement, proximity, plan existence, UI use, or admin activity
- no hidden "expert" threshold
- practice history is evidence; any physical effect must remain bounded and Simulation-owned
- citizens must still be allowed to choose unfamiliar work
- competence may bias outcome/efficiency only where physically justified; it must not create knowledge or bypass tools/materials/world legality
- teaching must involve a real Simulation-owned physical/guided-practice event; explanation alone grants nothing
- plans remain revisable intent, never command queues
- preserve Energy, maintenance, travel, world truth, and information-boundary contracts
- no `update.json` changes

**Acceptance direction:**
- two citizens with different real practice histories may become measurably but modestly different at the same relevant task
- the difference is reconstructable from canonical practice history
- removing/altering the practice history removes/changes the justification
- a novice remains legally able to attempt the task
- no citizen receives an identity label because of competence
- if guided practice is implemented, learner gains can only descend from a real completed shared/guided physical event

**Required handoffs:**
- exact competence source/effect contract to Memory
- exact guided-practice/teaching event contract to Memory + Communication
- safe read model to Assets, if any visible factual evidence is justified
- focused smoke coverage + full regression
- update STATE / DECISIONS / BACKLOG / OUTBOX, then stop

Do not publish `update.json`.


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.9 practice/plan language contract ready

**Need / Result:**
Communication Stage 1 is complete on `communication/v0.9-recognition-stage1` @ `f266c333a1fe3afb1a744c9c48e3cc2dc1ab8c63`; CI `36607321183` passed.

Communication consumes:
- `practice_snapshot_for(citizen_id)` for the citizen's own physical work history
- `plan_snapshot_for(citizen_id)` for read-only plan discussion

**Language semantics:**
- own repeated practice may support ordinary self-description
- >=3 practice events permits wording such as "I've done this several times"
- count is not XP/competence/rank/title
- self-assessment remains interpretation
- plan existence is intent, not capability
- conversation does not create/revise/complete a plan

**Teaching boundary:**
Communication creates no skill transfer from explanation.

If a future real teaching/guided-practice system is authorized, Communication will require a Simulation-owned physical/action event before any learner practice/competence effect may be claimed.

**Important constraints:**
- no competence score requested
- no expert/leader/rank field requested
- no new Simulation dependency for current Stage 1

**Next action:**
No Simulation change is required for Communication Stage 1. Preserve canonical plan/practice IDs and ownership during coordinator integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
