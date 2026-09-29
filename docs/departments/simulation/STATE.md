# World & Simulation — State

_Last updated: 2026-09-29_
_Current published release: v0.8.7_
_Active implementation branch: `simulation/v0.9-continuity-stage1`_
_Branch head: `6b027708512671d8c851723fb900cfa1e0fcac73`_
_Base: published v0.8.7 `be617e6e870ec3f1914d76cdb85107a6efc294d7`_

## Mission

Own physical truth and canonical intent/practice event identity.

> **The AI may decide intent. The simulation decides reality.**

v0.9 adds:

> **Persistent behavior must have a traceable history.**

## v0.9 Stage 1 — Persistent Plan Substrate

Implemented canonical citizen-owned plans.

### `citizen_plans`

Stable fields:

- `id`
- `owner_id`
- `created_minute`
- `updated_minute`
- `status`
- `current_intent`
- `next_step`
- `unresolved_question`

Current lifecycle states:

- `active`
- `paused`
- `completed`
- `abandoned`
- `superseded`

A plan is intent continuity, not a command queue.

Every physical step still uses the normal legal-action path.

## Plan Lifecycle History

New durable table:

- `plan_transitions`

Fields:

- stable transition `id`
- `plan_id`
- `owner_id`
- `sim_minute`
- `transition_type`
- `from_status`
- `to_status`
- optional `source_job_id`
- summary

Transition types currently include:

- created
- revise
- pause
- resume
- abandon
- complete
- supersede
- step_started
- step_outcome

Physical job completion never automatically marks a plan complete.

Completion/abandonment/revision remains a separate citizen plan-lifecycle decision.

## Memory Source Anchors

New durable table:

- `plan_memory_sources`

It binds:

- plan ID
- transition ID
- owner citizen
- canonical `memory_event_id`
- source role
- linked minute

Plan creation requires at least one existing Memory event owned by that citizen.

Foreign-citizen Memory cannot justify another citizen's plan.

Plan reason prose is not the causal source. The linked Memory IDs are.

## Memory Integration

Memory v0.9 Stage 1 remains the owner of causal ranking/retrieval.

Simulation consumes, when available:

- `causal_recall_snapshot(...)`
- `causal_recall_context_for(...)`
- `link_memory_event(memory_event_id, "plan", plan_id)`

Simulation does **not** duplicate recall score, aging, salience, or reinforcement.

On the standalone Simulation branch, `agent_city.causal_memory` is intentionally absent. Therefore:

- existing plans/source links work
- canonical plan state works
- explicit source Memory ownership validation works
- autonomous new-plan candidate retrieval fails closed to an empty list

After Memory's Stage 1 branch is merged, the planner automatically receives bounded causal Memory candidates.

`sync_plan_memory_facets()` also backfills previously created plan/source links into Memory's plan facets after merge, so merge order does not lose pinned recall.

## Planner Continuity

Planner context now includes:

- unfinished plans
- current intent
- next known step
- unresolved question
- linked source Memory IDs
- source-backed pinned recall when Memory Stage 1 is present
- bounded Memory candidates eligible to justify a new/revised plan

Planner JSON may choose one plan operation alongside one physical action:

- none
- create
- continue
- revise
- pause
- resume
- abandon
- complete

A plan operation does not make a physical action legal.

If a plan lifecycle choice fails validation, no plan truth is fabricated.

## Real Jobs Linked to Plans

`jobs` now has:

- `plan_id`

A job may be tagged only when:

- the plan belongs to that citizen
- the plan is currently active

When a tagged physical job starts:

- `step_started` is recorded

When the job ends:

- `step_outcome` is recorded
- the plan remains open unless the citizen separately changes its lifecycle

Paused, completed, abandoned, superseded, or foreign plans cannot tag new work.

## Canonical Practice Evidence

New durable table:

- `practice_events`

Practice evidence is one-to-one with a real completed or failed physical job.

Stable fields:

- `id`
- `citizen_id`
- `job_id` UNIQUE
- optional `plan_id`
- `activity_type`
- `job_status`
- `outcome`
- `completed_minute`
- `location_id`
- target/material/project references when present
- observation ID when present
- shared activity ID when present
- summary

Eligible activity types currently include real physical work such as:

- travel / local movement
- local/shared inspection
- survey / extract / deposit
- experiment
- fabrication / construction
- meaningful maintenance/service

Explicitly excluded from practice:

- talk
- wait
- agreement
- proximity
- UI/admin activity

No competence score, XP, title, class, role, or specialization is created in Stage 1.

## Historical Practice Backfill

v0.9 migration idempotently converts eligible historical completed/failed jobs from prior releases into the same `practice_events` evidence table.

This preserves actual citizen history instead of treating v0.9 as day zero.

Backfill does not reinterpret old work as a skill score.

## Safe Read Model

`/api/state` adds:

- `plans[]`
- `plan_transitions[]`
- `practice_events[]`

Plans include linked `memory_event_ids`.

New read-only endpoint:

`GET /api/continuity/{citizen_id}`

Returns:

- citizen ID/name
- bounded plans
- bounded practice events
- explicit semantics:
  - plans are intent, not commands
  - practice is evidence, not a competence score

There is no visitor/admin plan-write endpoint.

## Stage 1 Non-Goals

Stage 1 does not add:

- competence modifiers
- XP/levels
- role/class/specialization
- expert titles
- universal reputation
- automatic self-assessment
- teaching
- habits/customs
- plan auto-execution

Those later systems must descend from this source-backed evidence.

## Validation

Final GitHub Actions run:

`36603570434` — PASS

Passed:

- Python compilation
- JavaScript syntax
- complete published regression matrix v0.4 through v0.8.7
- `tests/smoke_v090_simulation_stage1.py`

A previous full run `36603320118` also passed before the final merge-order Memory-facet hardening.

The final branch commit only restored the release-only workflow.

## Status

World & Simulation v0.9 Stage 1 is ready for integration with Memory's causal-memory branch and for downstream Communication/Assets consumption.

No `update.json` or release metadata was changed.


## v0.9 Stage 1 Session Close

World & Simulation work for this session is complete.

Authoritative implementation:
- branch: `simulation/v0.9-continuity-stage1`
- head: `6b027708512671d8c851723fb900cfa1e0fcac73`
- base: published v0.8.7 `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- final validation: GitHub Actions `36603570434`

Handoffs delivered:
- Memory: canonical plan/source/practice IDs + causal facet backfill contract
- Communication: plan/practice truth contract for self-assessment/recognition work
- Assets: score-free continuity read model
- COORDINATION: Simulation is in REVIEW and downstream Simulation blockers are cleared

No additional World & Simulation Stage 1 work is pending.

Resume only for:
- coordinator Memory+Simulation merge conflicts,
- a new Simulation inbox request,
- or authorized v0.9 Stage 2 competence/teaching work.

No release metadata or `update.json` was changed.
