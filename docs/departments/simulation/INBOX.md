# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The active v0.8 Stage 2 local exploration/shared physical activity packet was implemented and handed off._


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
