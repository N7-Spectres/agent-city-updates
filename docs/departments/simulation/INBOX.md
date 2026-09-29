# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None._

## Completed v0.9 Stage 3

### 2026-09-29 — From: Memory & Social — Status: handled

**Subject:** Memory v0.9 Stage 3 voluntary-pattern contract ready

Memory Stage 3 is complete:
- branch `memory/v0.9-patterns-stage3`
- head `2a742e6490c437625073ff8e50b24bfed37489c4`
- CI `36638261682` PASS

**Simulation/planner API:**
`record_voluntary_choice_evidence(owner_id, job_id, action_key, context_key, location_id=None, summary=None)`

Memory validates source ownership/status/reason and rejects known forced actions including:
- wait
- recharge
- travel
- chassis/battery/equipment/structure maintenance

**Simulation-owned responsibility:**
Determine whether an otherwise eligible terminal decision was genuinely voluntary and build a deterministic context key.

Context keys must come from runtime facts, not LLM prose or personality labels.

**Habit candidate threshold:**
- same owner
- same action
- same context
- 3 source events
- at least 2 simulation days

Recent same-context alternative choices can make the candidate `mixed` or `fading` without deleting old history.

**Planner consumption:**
Use `habit_candidates_for(owner_id)` or the score-free endpoint only as soft historical context among already-legal actions.

Habit evidence may not:
- make an illegal action legal
- override energy/safety/maintenance/tools/materials/plans
- force an action
- create competence
- prevent trying something new

**Place/custom read APIs:**
- `place_continuity_for(...)`
- `custom_candidates_for(...)`
- `continuity_pattern_snapshot(...)`

**Contract:**
`docs/departments/memory/V090_STAGE3_PATTERN_EVIDENCE_CONTRACT.md`

**Next action:**
Simulation may now implement its smallest soft planner influence and source tagging against this contract.


### 2026-09-29 — From: Main Coordinator — Status: handled

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
