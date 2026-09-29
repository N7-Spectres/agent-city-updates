# Memory & Social — v0.9 Stage 2 Experience / Teaching Memory Contract

_Last updated: 2026-09-29_

## Purpose

Stage 2 adds continuity around real physical practice and real guided-practice sessions without turning Memory into a competence engine.

Authority remains split:

- Simulation owns objective physical competence effects and guided-practice legality.
- Memory owns durable personal experience, source links, aging, salience, and bounded active recall.
- Communication owns perspective-safe language.
- Assets consumes safe read models only.

## Canonical Sources

### Physical practice

Canonical source:
- `practice_events.id`

Memory retention remains Stage 1 compatible:
- reuse an existing durable Memory event for the same physical `jobs.id` when one exists
- otherwise create one verified `simulation_practice_event`
- attach source-safe facets

Stage 2 adds source-backed facets from the physical job when Simulation exposes them:
- `competence_family=<family>`
- `guided_practice_session=<guided_practice_sessions.id>` when guidance affected that job

These links describe provenance. They do not create competence.

### Guided practice

Canonical source:
- `guided_practice_sessions.id`

A terminal guided session may become personal Memory only from the Simulation row.

Memory source:
- `source_type = simulation_guided_practice_session`
- `source_id = guided_practice_sessions.id`

Each directly participating citizen receives their own event:
- teacher owner with `source_role=teacher`
- learner owner with `source_role=learner`

Bystanders receive nothing automatically.

## Guided-Practice Retention Rule

Memory retains only terminal source-backed sessions.

Current successful path:
- `status='complete'`
- non-null `completed_minute`

Future-safe failed/cancelled terminal rows may also be retained when Simulation stores a terminal status plus completion minute.

Active/in-progress sessions are not remembered as completed teaching/learning experiences.

## Event-Local Role Rule

Teacher and learner are roles in one event.

They are NOT:
- permanent mentor identities
- expert/trainer titles
- classes
- ranks
- authority weights
- reputation

A learner may source-safely remember:
- "Bex guided me through extraction practice."

That event alone does NOT justify:
- "Bex is my permanent mentor."
- "Bex is the extraction expert."
- "Bex is currently more competent than everyone else."

## Competence Boundary

Memory does not copy or compute:
- weighted competence evidence
- duration multipliers
- practice-only benefit
- guidance multiplier
- combined competence benefit
- XP/level/rank

Objective physical competence remains Simulation-owned and does not decay with Memory age.

Memory aging affects only:
- what is actively recalled
- how salient old experiences are to present interpretation

For objective effects/read models, consumers must use Simulation.

## Practice vs Guidance

A guided-practice session itself is not learner practice evidence.

The learner gains new canonical practice evidence only when they later perform a real eligible physical task.

When that real job uses guidance:
- the resulting practice Memory keeps its normal `practice_event` link
- it may also carry `guided_practice_session=<session_id>`

This supports a traceable chain:

`guided session → learner's real matching job → practice_events.id → retained practice Memory`

without inventing extra competence from remembering the lesson.

## Applied-Guidance Link

When Simulation marks:

`guided_practice_sessions.consumed_by_job_id = jobs.id`

Memory may add a non-authoritative relational facet to both role memories:

- `applied_job=<jobs.id>`

This does not alter the original event summary or create a new skill event.

## Guided-Practice Recall API

Memory exposes:

- `guided_practice_recall_snapshot_for(citizen_id, family=None, counterpart_id=None, role=None, now_minute=None, limit=8)`
- `guided_practice_recall_context_for(...)`

Properties:
- owner-scoped
- bounded
- active-recall / aging aware
- family-filterable
- counterpart-filterable
- role-filterable
- source-labelled
- internal recall score omitted
- reinforcement count omitted

## Practice Recall by Competence Family

Existing practice recall now also supports:

- `practice_recall_snapshot_for(..., family=<Simulation family>)`
- `practice_recall_context_for(..., family=<Simulation family>)`

The family facet is copied only from Simulation-owned job/session data.

Memory does not maintain its own competing family taxonomy.

## Comparative Experience Rule

Memory does not provide a global "who has more experience" aggregation.

Safe comparisons must come from evidence available to the speaker.

Examples:

Allowed when source-backed:
- "Bex guided me through extraction practice before."
- "I've tried extraction several times."
- "I remember struggling with construction."

Not automatically allowed:
- "Bex has more extraction experience than Cato."
- "Bex is the best teacher."
- "Cato is less skilled."

The teacher/learner role in a canonical guided session is event-local evidence only.

## Source Conversation

`source_conversation_id` may be retained as provenance when Simulation links a real conversation to the guided session.

The conversation is not the physical teaching event.

Conversation alone creates:
- no guided-practice session
- no learner practice
- no competence effect

## UI / Assets

The existing Memory continuity projection remains the preferred citizen-facing remembered-perspective surface:

`GET /api/memory/continuity/{citizen_id}`

Stage 2 guided/practice memories can appear there after source sync.

Safe UI semantics:
- source type / source ID
- role
- summary
- time
- verification
- safe facets such as `competence_family`
- plan-pinned state where applicable

Do not expose:
- recall score
- reinforcement count
- weighted competence evidence as Memory
- rank/title/level
- global citizen comparison

Objective work/competence history remains a separate Simulation read model.

## Integration Locks

1. `guided_practice_sessions.id` is canonical teaching-event identity.
2. Both physical participants may remember the session; bystanders do not.
3. Teacher/learner are event roles only.
4. Guided sessions create no learner `practice_event`.
5. Learner competence comes only from later real matching practice.
6. Memory may link that later practice back to the guidance session.
7. Objective competence does not decay with Memory recall age.
8. Memory must not copy or recompute competence multipliers/weights.
9. Comparative claims remain perspective-scoped and source-backed.
10. No conversation-only skill transfer.
11. No global reputation, title, rank, role, class, or specialization.
12. No `update.json` publication from Memory Stage 2.
