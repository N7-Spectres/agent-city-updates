# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

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
