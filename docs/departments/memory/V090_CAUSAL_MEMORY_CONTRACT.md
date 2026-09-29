# Memory & Social — v0.9 Stage 1 Causal Memory Contract

_Last updated: 2026-09-29_

## Purpose

v0.9 Stage 1 separates:

- **durable archive** — source-backed `memory_events`
- **active recall** — a bounded ranked packet selected for a current decision

Persistent behavior may use active recall only when the recalled item remains traceable to the durable archive and its real source.

> Persistent behavior must have a traceable history.

## Durable Archive

`memory_events` remains the canonical retained-event archive.

Active recall MUST NOT rewrite:
- source type / source ID
- summary
- status / verification
- owner
- simulation time

Aging changes retrieval priority, not history.

## Facet Index

Stage 1 adds:

`memory_event_facets(owner_id, memory_event_id, facet_kind, facet_value)`

This table is an index/projection, not new truth.

Automatically indexed facet families may include:
- event kind
- source type
- counterparty
- visitor
- stable subject
- maintenance/physical target
- location
- material
- process
- activity/action type

Future explicit continuity facets may include:
- `plan:<plan_id>`
- `place:<place_id>`

A facet links source-backed experiences. It does not create a role, class, habit, reputation, or fact.

## Reinforcement

Repeated events sharing a meaningful facet can become easier to retrieve.

Reinforcement:
- changes recall priority only
- does not merge source events
- does not increase verification
- does not turn repeated claims into truth
- does not create competence by itself

Each original memory remains individually traceable.

## Aging

Active recall score considers:
- event importance
- recency
- repeated related experience

Low-value old events may fall out of a bounded recall packet.

They remain in the durable archive.

High-salience history may remain retrievable through its importance or explicit plan linkage.

## Persistent Plan Pinning

Unfinished plans need durable causal anchors.

Recommended Simulation/planner contract:

A plan stores stable Memory references to the evidence/reasons that caused it to exist.

Minimum:
- `plan.id`
- `owner_id`
- `created_minute`
- lifecycle status
- current intent
- next known step / unresolved question
- initiating/reason `memory_event_id` references
- revision / abandonment / completion history with source references

Memory exposes:

- `link_memory_event(memory_event_id, "plan", plan_id)`
- `causal_recall_snapshot(..., pinned_event_ids=[...])`
- `causal_recall_context_for(..., pinned_event_ids=[...])`

Pinned plan memories are guaranteed candidate inclusion even when old.

Pinning affects access, not truth or destiny.

A plan may still be revised, paused, superseded, abandoned, or completed.

## Retrieval API

Internal Python contract:

`causal_recall_snapshot(owner_id, now_minute=None, facet_filters=None, pinned_event_ids=None, limit=8)`

Returns bounded per-citizen items with:
- memory event ID
- source type / source ID / source role
- event kind
- simulation time / age
- summary
- importance
- status / verification
- facets
- matching facets
- reinforcement count
- recall score
- pinned flag

`causal_recall_context_for(...)` returns a bounded model-facing text packet with source labels.

Facet filters are relevance hints and match any supplied facet.

No global-citizen union is allowed.

## Plan → Memory → Planner Interface

Preferred Stage 1 flow:

1. real event/claim becomes a source-linked Memory event
2. planner forms a plan for a real reason
3. plan stores the relevant `memory_event_id` reference(s)
4. those events receive a `plan` facet
5. later planning retrieves:
   - pinned initiating/revision memories
   - current plan facet
   - current action/subject/location facets where useful
6. model decides whether to continue/revise/pause/abandon
7. Simulation validates each physical step

Do not use an opaque hidden plan-priority score as the causal explanation.

## Simulation Handoff

Simulation may safely treat completed physical jobs/outcomes as future practice evidence only when they have canonical IDs/outcomes.

For persistent plans, Simulation/planner should expose stable lifecycle records and retain the Memory event IDs that justify creation/revision.

Energy, maintenance, unavailable materials, failed actions, and new evidence may interrupt a plan without deleting its source history.

## Communication Handoff

Recall is citizen perspective, not global truth.

Communication may use owner-scoped recall to support statements such as:
- "I've done this several times."
- "I remember that repair going badly."
- "N7 and I walked there before."

Only when source history supports them.

Rules:
- repeated unverified claims stay unverified
- no global reputation
- no expert/leader/title assignment
- self-assessment remains interpretation
- explanation/teaching conversation alone does not create practice or competence
- visitor continuity requires real visit/exchange/shared-action sources

## Future Stage Hooks

Stage 1 intentionally leaves room for:
- plan facets
- place facets
- self-assessment packets
- practice/outcome facets
- later habit/custom detection

These future features must descend from repeated source-backed events.

## Non-Goals

Stage 1 does not add:
- roles/classes
- XP
- universal reputation
- fabricated autobiographies
- authored habits
- global memory
- automatic skill from conversation
- automatic place attachment


## Canonical Practice Evidence Retention

Simulation Stage 1 now exposes canonical physical practice through `practice_events.id`.

Memory consumes that ledger through `agent_city/practice_memory.py`.

### Source rule

Practice evidence may enter durable personal Memory only from a real Simulation `practice_events` row.

Practice does **not** come from:
- conversation
- agreement
- proximity
- waiting
- UI/admin interaction
- concept art

### Dedupe rule

The same physical job should not produce two autobiographical copies merely because it has multiple valid source ledgers.

When a `practice_events.job_id` already corresponds to a durable Memory event, for example:
- maintenance memory
- spatial observation memory
- shared-exploration memory
- job/discovery memory

Memory reuses that existing event and adds practice facets.

If no durable Memory event represents the physical job, Memory creates one:

- `source_type='simulation_practice_event'`
- `source_id=practice_events.id`
- `event_kind='practice_<activity_type>'`
- owner = `practice_events.citizen_id`
- status/verification = verified

### Practice facets

Practice-linked memories may receive:
- `practice_event=<practice_events.id>`
- `activity=<activity_type>`
- `plan=<plan_id>` when present
- location/material/target facets when safely available

This improves later source-backed retrieval without creating XP, levels, titles, or a universal competence score.

### Outcome rule

Completed and failed real practice are both legitimate history.

A failed/no-yield event may be more salient for later recall, but it is not a permanent negative trait.

Practice outcome changes what happened, not who the citizen "is."

### Authority split

Simulation owns:
- which jobs qualify as practice
- `practice_events.id`
- job status/outcome
- later physical competence effects, if any

Memory owns:
- whether/how that evidence is retained
- dedupe against existing autobiographical events
- causal facets
- bounded recall/reinforcement

Communication may later interpret this history as perspective-safe self-assessment, but may not convert counts into authoritative expertise titles.


## Model-Facing Practice Recall

Communication and future self-assessment logic should not read the full durable physical practice ledger as though every old event is equally active autobiographical recall.

Memory exposes:

- `practice_recall_snapshot_for(citizen_id, activity=None, now_minute=None, limit=8)`
- `practice_recall_context_for(...)`

These functions:

- require the `practice_event` facet family
- preserve normal Memory aging/salience
- remain owner-scoped
- optionally filter by activity
- return only actively recalled source-backed practice
- omit internal recall score
- omit internal reinforcement count
- keep source type / source ID / verification / time / summary

This is the preferred model-facing bridge for:
- self-assessment
- teaching/explanation boundaries
- later habit/preference reasoning

The full Simulation `practice_events` ledger remains valid for objective diagnostics, continuity UI, and physical-history accounting, but should not bypass Memory when deciding what a citizen is presently recalling/interpreting.
