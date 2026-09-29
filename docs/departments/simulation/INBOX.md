# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The v0.9 Stage 1 persistent-plan/practice packet and Memory dependency were handled._


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
