# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-10-02 — From: World & Simulation / Coordinator — Status: published

**Subject:** v1.0.0 Material Independence is live

**Release / validation:**
- `release-v1.0.0@b8119734ff5d0793fd2e07f45e3be3b20ff20c6f`
- full CI `37032876262` PASS
- PR #52 merged; test-correction PR #53 merged

**Physical contract:**
- verified property discoveries are the only source of production-process learning
- `learned_processes` stores citizen-owned production capability
- `process_material` is a real Simulation job
- `production_events.id` is the durable production audit source
- inputs are consumed at job start; outputs exist only after real job completion
- material processing uses real energy/time and wears its workbench/smelter
- all seven manufactured starter categories have at least one evidence-backed local replenishment path in the current world
- the v1.0 smoke proves the loop from zero manufactured starter stock through local production to successful charger maintenance

**Downstream boundary:**
Memory/Communication/Assets may describe production only from real process/discovery/job evidence. Do not turn process names into ranks, professions, universal knowledge, or UI-derived capability.

### 2026-10-02 — From: World & Simulation / Coordinator — Status: published

**Subject:** v0.9.28 finite starter-stock sustainability context is live

**Release / validation:**
- `release-v0.9.28@a530afb661e9a1cd6f1820551c73d3b944b9b36c`
- full CI `37022302296` PASS

**Contract:**
- Seed Site citizens can assess finite manufactured starter stock and the absence of a currently validated replenishment process.
- This context does not identify hidden deposits, suggest a specific region, create a conversion/fabrication recipe, or force exploration.
- Existing physical surveys remain the discovery gate. The v0.9.28 smoke explicitly proves hidden ore names are absent before survey and become knowable only after a real survey completes.
- Future material loops must be explicit Simulation processes built from validated evidence.

### 2026-10-02 — From: World & Simulation / Coordinator — Status: published

**Subject:** v0.9.26 local maintenance-awareness boundary is live

**Release / validation:**
- branch `release-v0.9.26`
- exact green head `937f300e8870f6baed2031e6f69b68b7da667a08`
- full CI `37017820397` PASS
- PR #47 merged
- updater published as `v0.9.26`

**Delivered:**
- service-due local maintenance remains visible to the planner even when missing stock blocks the physical service action
- known starter procedure requirements and exact local Seed Site stock shortfalls are exposed only while the citizen is physically at the Seed Site landmark
- `possible_actions` remains the legality authority
- real in-progress service suppresses duplicate same-target repair
- planner is explicitly forbidden from inventing supply sources, substitutions, conversions, or fabrication recipes
- remote citizens do not receive exact Seed Site maintenance/stock state

**Downstream note:**
Memory/Communication may describe a citizen discussing or remembering a maintenance shortage only from real source-backed events. This change does not create global shared maintenance knowledge, procurement knowledge, a new role, or a technology unlock.


### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 3 voluntary-pattern + soft-planner contract ready

**Final branch / validation:**
- `simulation/v0.9-habits-stage3`
- head `fb17d3a2fb0776c490cdd4805feae8ab97c763ac`
- CI `36642152013` PASS

**Delivered:**
- Simulation-owned voluntary-choice classification
- deterministic context key from runtime facts
- additive job provenance fields
- successful terminal jobs retain Memory evidence only after physical commit
- recurring pattern context reaches planner only when context matches and action is already legal
- place continuity and social pattern evidence remain interpretation context
- no legality, competence, resource, energy, plan, role, preference, or culture effects

**Communication handoff:**
Communication may consume Memory's owner-scoped pattern/place/custom evidence knowing that recurring-choice sources now have a Simulation provenance gate. Communication must not turn `current` into a personality trait or `custom` into universal tradition truth.

**Assets handoff:**
Simulation adds no new Stage 3 presentation score. Existing Memory pattern endpoint remains the primary UI evidence source. The new job audit fields are diagnostic provenance, not badges/meters.

**Contract:**
`docs/departments/simulation/V090_STAGE3_HABIT_PLANNER_CONTRACT.md`

No `update.json` changes.

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
