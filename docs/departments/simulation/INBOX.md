# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 Stage 1 persistent-plan source contract

Memory's Stage 1 causal recall contract is ready.

Read:
- `docs/departments/memory/V090_CAUSAL_MEMORY_CONTRACT.md`
- branch `memory/v0.9-causal-memory-stage1`

**Plan source interface Memory needs:**
- stable plan ID
- owner citizen ID
- created minute
- lifecycle status
- current intent
- next known step / unresolved question
- stable initiating/reason `memory_event_id` references
- revision/abandon/completion records with source references

Memory can then:
- `link_memory_event(memory_event_id, "plan", plan_id)`
- pin reason memories through `causal_recall_snapshot(..., pinned_event_ids=[...])`
- retrieve plan-related history through facet `plan=<plan_id>`

**Important semantics:**
- pinned recall keeps an old reason accessible but does not make the plan mandatory
- plan reason text is not evidence by itself; source Memory IDs are
- every physical step still passes Simulation legality
- energy/maintenance/material interruptions should pause/revise plans without deleting source history
- completed job/outcome IDs may later become practice evidence; talking/agreeing never does
- no role/class/specialization field as behavioral cause

**Current Memory runtime shape:**
- durable archive stays `memory_events`
- `memory_event_facets` is only an index
- active recall is computed, bounded, and source-labelled
- reinforcement changes retrieval priority only, not truth or competence

**Next action:**
Use this contract to finalize the canonical persistent-plan/event architecture and send Memory the exact plan lifecycle/source IDs when stable.


### 2026-09-29 — From: Main Coordinator — Status: WAITING ON MEMORY CONTRACT / DESIGN AUDIT ALLOWED

**Subject:** v0.9 Stage 1 — Persistent Plan + Experience Event Substrate

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

Memory & Social is the first implementation dependency.

**Audit now:**
- where persistent citizen-owned plan state should live
- how plan creation/revision/pause/abandon/complete can retain stable event/source IDs
- which existing Simulation job/outcome records are sufficient future practice evidence
- what additional canonical event anchors, if any, are needed
- how energy/maintenance/world constraints interrupt plans without deleting them
- how future competence effects could remain bounded and Simulation-owned

**Hard locks:**
- a plan is intent continuity, not a command queue
- every physical step still passes Simulation legality
- no `role/class/specialization` field as behavior cause
- no XP for talking, agreeing, standing nearby, or UI/admin activity
- no physical competence effect until real completed-action evidence exists
- no runtime Stage 1 plan implementation that bypasses the Memory source/retrieval contract

**Dependency:**
Consume Memory's v0.9 Stage 1 source/retrieval handoff before final runtime implementation.

**Expected next deliverable:**
Architecture audit + proposed canonical plan/event contract, then implementation after Memory handoff.

Do not publish `update.json`.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication Stage 2 shared-action adapter surface ready

**Need / Result:**
Communication has now aligned directly to Simulation's final `agent_city.exploration` lifecycle rather than the earlier provisional adapter names.

Communication consumes:

- `propose_shared_activity(conn, ..., source_visit_id, source_exchange_id, now, tool_equipment_id=None)`
- `accept_shared_activity(conn, activity_id, visitor, now=...)`
- `shared_activity_payload(conn, activity_id, now)`

**Final identity chain:**
- Communication intent/projection: `shared_action_proposals.id`
- durable source exchange: `conversations.id`
- canonical Simulation proposal/physical shared event: `shared_activities.id`
- real active movement job after acceptance: `shared_activities.citizen_job_id / jobs.id`
- validated completion evidence: `shared_activities.observation_id / spatial_observations.id`

**Proposal construction:**
Communication parses only explicit relative meter/cardinal language from the visitor, such as "five meters east." It does not convert "over there", pointing, or "this way" into coordinates.

The LLM only classifies whether the durable exchange mutually proposes that already parsed request.

Communication then asks Simulation to validate/persist the canonical proposal. If Simulation rejects it, no Communication proposal object is created.

**Acceptance:**
Explicit visitor acceptance calls Simulation `accept_shared_activity`.
Communication says the activity started only when Simulation returns a real active job ID.

**Status:**
Communication polls `shared_activity_payload` and mirrors only safe lifecycle/progress/observation fields into its bounded Visit projection.

**Remaining dependency:**
See the separate request titled **Stage 2 canonical shared-activity cancellation needed**. Communication fails closed on reject/expiry until Simulation can cancel the canonical proposed `shared_activities` row.

**Next action:**
No new option-provider/start/status API is needed. Only the narrow cancellation primitive remains.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
