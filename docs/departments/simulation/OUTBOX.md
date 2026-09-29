# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 2 World & Simulation session wrapped

**Result:**
The bounded competence + real guided-practice packet is implemented, tested, documented, and fully handed off.

**Authoritative branch / validation:**
- `simulation/v0.9-competence-stage2`
- head `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- final CI `36618030044` PASS

**Downstream handoffs complete:**
- Memory has the canonical practice/competence/guided-session source contract
- Communication has the real guided-practice/language boundary
- Assets has the safe score-free competence read model
- stale downstream "waiting on Simulation" inbox labels were cleared
- COORDINATION already records Simulation in REVIEW and Memory as the next active dependency

**Next action:**
Stop Simulation work. Resume only for integration conflicts or a new routed task.


### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 2 bounded competence + guided practice ready

**Implementation:**
- branch `simulation/v0.9-competence-stage2`
- final head `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- integrated Stage 1 base `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- final runtime CI `36618030044` PASS

**Delivered:**
- family-specific competence derived from real `practice_events`
- 8% max practice duration reduction
- failed attempts contribute partial experience
- no XP/levels/classes/titles/reputation
- degraded workbench remains dominant physical bottleneck
- real guided-practice session with teacher/learner source IDs
- guided session itself grants no competence
- one-use 4% learner support on next matching real task
- total competence+guidance effect capped at 10%
- score-free `GET /api/competence/{citizen_id}`
- auditable job source fields

**No release publication or update.json change.**

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Memory Stage 2 competence/guided-practice source contract

Objective competence sources:
- canonical `practice_events.id`
- family mapping is Simulation-owned
- applied job records `competence_family` + `competence_duration_multiplier`
- optional `guidance_session_id`

Guided practice source:
- `guided_practice_sessions.id`
- physical job `job_id`
- teacher / learner IDs
- activity family
- started/completed time
- optional source conversation ID
- consumed learner job ID

Important:
- guided session is a real event but is not itself learner practice/competence
- learner's later real matching job creates the new practice event
- Memory may remember/recall the session as a social/learning experience without creating additional physical competence
- objective competence does not decay with Memory recall age

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Communication Stage 2 guided-practice language contract

Communication may say a completed session occurred only from real `guided_practice_sessions`.

It may describe:
- who guided whom
- activity family
- when it occurred
- whether the guidance was later consumed by a real matching task
- actual personal practice history

It must not automatically call the guide:
- expert
- mentor
- trainer
- leader
- specialist

Explanation/talk alone remains zero competence transfer.

Self-assessment may interpret practice history; objective physical effect remains Simulation-owned.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Assets Stage 2 safe competence read model

Read endpoint:
- `GET /api/competence/{citizen_id}`

Per family safe facts:
- family
- practice_count
- completed_count
- failed_count
- duration_multiplier
- duration_reduction_percent
- source practice event IDs

Also:
- guided-practice session history

UI guidance:
- show evidence/history first
- no XP bars
- no skill/proficiency levels
- no expert/mentor badges
- do not derive competence in frontend
- objective duration effect may be shown as a factual small physical modifier if useful
- guided-practice history is event history, not identity

## Outbox Rule

Keep durable architecture/rules in STATE/DECISIONS/BACKLOG. Keep this file focused on current handoffs.
