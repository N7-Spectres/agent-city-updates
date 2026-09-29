# World & Simulation — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 World & Simulation session wrapped

**Result:**
The Persistent Plans + Practice Evidence Stage 1 packet is implemented, tested, documented, and fully handed off.

**Authoritative branch / validation:**
- `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- CI `36603570434` PASS

**Handoffs complete:**
- Memory has canonical plan/source/practice IDs and merge-order facet-backfill behavior
- Communication has objective plan/practice evidence rules for self-assessment/recognition
- Assets has the safe continuity read model with explicit no-XP/no-expert-badge constraints
- COORDINATION records Simulation in REVIEW

**Next action:**
Stop Simulation work. Coordinator should combine Memory + Simulation Stage 1, run both v0.9 smokes with the full regression matrix, then route any integration conflicts back here.


### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 1 persistent plans + practice evidence ready

**Implementation:**
- branch `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- base published v0.8.7 `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- final CI `36603570434` PASS

**Delivered:**
- stable citizen plan IDs/lifecycle
- plan transition history
- canonical Memory-event source links
- jobs linked to active plans
- real completed/failed physical jobs -> stable practice evidence
- historical physical-work backfill
- planner persistent-plan context/operations
- safe continuity read model
- no competence score/class/role/reputation

**Integration note:**
Memory's `agent_city/causal_memory.py` remains Memory-owned. After Memory + Simulation branches merge, autonomous new-plan candidate retrieval activates through Memory's public API. Simulation includes a facet backfill hook so earlier plan sources gain `plan` facets regardless of merge order.

**No release publication or update.json change.**

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Memory v0.9 canonical plan/practice contract

**Plan identity:**
- `citizen_plans.id`

**Plan fields:**
- owner_id
- created_minute / updated_minute
- status
- current_intent
- next_step
- unresolved_question

**Plan source mapping:**
`plan_memory_sources`
- plan_id
- transition_id
- owner_id
- canonical `memory_event_id`
- source_role
- linked_minute

**Lifecycle history:**
`plan_transitions.id`
- plan_id / owner
- sim minute
- transition type
- from/to status
- optional source_job_id
- summary

**Physical linkage:**
- `jobs.plan_id`

**Practice evidence:**
`practice_events.id`
- one-to-one `job_id`
- citizen_id
- optional plan_id
- activity_type
- job_status / outcome
- completed minute
- location/target/material/project/observation/shared-action references

Simulation dynamically calls:
- `link_memory_event(memory_event_id, "plan", str(plan_id))`

and `sync_plan_memory_facets()` backfills plan facets after merge if the plan existed before causal Memory was present.

**Memory rule:**
Practice evidence is physical source material for future Memory/competence reasoning. It is not itself a Memory event unless Memory chooses to retain/index it according to policy.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Communication v0.9 plan/practice truth contract

Communication may safely describe:
- a citizen has an active/paused/completed/etc. plan if Simulation says so
- current plan intent / next known step / unresolved question
- completed/failed physical practice history from `practice_events`

But:

- a plan is intention, not proof of future completion
- plan existence is not competence evidence by itself
- conversation about an activity is not practice
- practice events are objective physical history, not an "expert" title
- self-assessment remains citizen interpretation backed by owner-scoped Memory + practice evidence
- recognition by another citizen requires that citizen's legitimate knowledge/experience path
- no global reputation/expertise score

Stage 2 Communication can use repeated `practice_events` plus causal Memory to support statements such as "I've done this several times," while preserving perspective and uncertainty.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** Assets v0.9 safe continuity read model

Safe state collections:
- `state.plans[]`
- `state.plan_transitions[]`
- `state.practice_events[]`

Read endpoint:
- `GET /api/continuity/{citizen_id}`

Plans expose:
- ID / owner
- status
- created/updated times
- current intent
- next step
- unresolved question
- linked Memory event IDs
- recent transitions through the continuity endpoint

Practice exposes:
- physical job ID
- activity type
- job status/outcome
- time
- physical subject/location references

**UI rule:**
Do not turn counts into levels, expertise badges, classes, ranks, or reputation.

A useful UI can show:
- unfinished plan
- why it exists through source-linked history
- next known step
- recent plan changes
- actual work history

without exposing Memory recall scores or invented identity labels.

## Outbox Rule

Keep durable architecture/rules in STATE/DECISIONS/BACKLOG. Keep this file focused on current handoffs.
