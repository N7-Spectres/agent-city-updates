# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: WAITING ON MEMORY CONTRACT / AUDIT ALLOWED

**Subject:** v0.9 Stage 3 — Soft Habit Influence and Historical Place/Custom Context

**Definitive Stage 2 base:**
- `release-v0.9.0-stage2-integration` @ `f680275a78b9da71a43f3c79217f292796b7843d`
- combined CI `36637062562` — PASS

**Audit now:**
- where voluntary repeated-pattern evidence may enter planner context
- how a habit may softly bias selection among already-legal actions without becoming a command
- how energy, safety, maintenance, tools, materials, plans, and physical legality continue to outrank habit tendency
- how contrary/recent history should allow a recurring pattern to weaken/change
- how place meaning may influence intent/reasoning without changing physical location truth
- whether customs should affect planner expectations only after Memory proves socially transmitted repeated history
- ensure no physical speed/output/competence bonus comes from "habit" or "custom" merely as a label
- ensure unfamiliar/new actions remain possible
- identify any canonical source IDs needed from Simulation that Memory cannot currently trace

**Runtime dependency:**
Do not implement habit/place/custom planner influence until Memory hands off the Stage 3 source/provenance contract.

**Hard locks:**
- habit cannot make an illegal action legal
- habit cannot force an action
- habit cannot cancel/override survival, recharge, maintenance, or active plan realities
- no habit-derived competence bonus
- no role/class/profession/preferences field
- no general v1.0 preference system
- place meaning is remembered interpretation, not physical truth
- customs do not become physics
- no global culture score
- no scripted routine timetable
- no `update.json` changes

**Expected deliverable:**
Architecture/planner audit now. After Memory contract, implement only the smallest soft, evidence-backed historical influence justified by the doctrine, with focused smoke coverage and downstream handoffs.


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** Communication consumed final Stage 2 competence/guided-practice contract

Communication Stage 2 is complete on `communication/v0.9-guided-practice-stage2` @ `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`; CI `36627237487` PASS.

Consumed Simulation semantics:
- speaker's own bounded `competence_snapshot(...)` physical effect
- current self-owned legal `possible_actions(...)` guided-practice option
- canonical `guided_practice_sessions.id` via Memory continuity

Communication does not:
- inspect another citizen's objective competence snapshot for social recognition
- convert guided-practice legality into expert/mentor identity
- create physical guided-practice sessions from conversation
- create competence from explanation

No Simulation change is requested.

Coordinator may integrate Stage 2.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
