# Memory & Social — v0.9 Stage 3 Pattern Evidence Contract

_Last updated: 2026-09-29_

## Primary Law

> Persistent behavior must have a traceable history.

Stage 3 adds evidence for recurring behavior, place significance, and socially transmitted patterns.

It does **not** add permanent habit, preference, profession, culture, or reputation identity fields.

## New Evidence Ledger

Memory owns:

`memory_pattern_evidence`

This is an additive source-linked projection.

It stores evidence, not conclusions.

Fields include:
- owner citizen
- simulation minute
- evidence kind
- source type / source ID / source role
- action key
- context key
- optional location
- optional actor
- optional transmission mode
- verification state
- source-backed summary

Deleting the canonical source causes the derived evidence row to be pruned.

No pattern survives its source history.

## Habit Candidate Evidence

Habit candidates come only from explicitly classified **voluntary-choice evidence**.

Memory does not infer voluntariness from repetition alone.

Stage 3 API:

`record_voluntary_choice_evidence(owner_id, job_id, action_key, context_key, location_id=None, summary=None)`

Memory validates:
- job exists
- job belongs to owner
- job is terminal
- a decision reason was recorded
- action matches the job
- known forced/survival actions are rejected

Known automatic exclusions include:
- wait
- recharge
- travel
- chassis/battery/equipment/structure maintenance

Simulation/planner remains responsible for deciding whether a non-excluded action was genuinely voluntary.

## Habit Threshold

A recurring voluntary pattern becomes a Memory **habit candidate** only when:

- same citizen
- same deterministic context key
- same action key
- at least 3 distinct source events
- spread across at least 2 simulation days

This is not a personality trait or preference.

### Later divergence

Memory keeps all source events.

Recent voluntary choices in the same context can change the candidate state:

- `current` — recent choices still mostly repeat the action
- `mixed` — repetition continues but alternatives also appear
- `fading` — recent choices mostly diverge

The old events remain preserved.

Deleting/changing source events changes the candidate justification.

## Context Key Contract

The context key must come from deterministic runtime context, not free-form LLM prose.

Examples of safe context dimensions:
- location / physical zone
- task opportunity class
- ordinary free-choice window
- planner state that is not survival/emergency forced

Unsafe:
- "likes mining"
- "is an explorer"
- "feels productive"
- any inferred personality/preference label

Simulation should define the canonical Stage 3 context-key construction.

## Place Continuity / Meaning

Place meaning is not factual location knowledge and not a favorite field.

Memory exposes citizen-specific **place continuity evidence** derived from source-backed memories carrying a location/place facet.

A place becomes eligible for the read model after either:
- at least 2 experiences spanning at least 2 event kinds, or
- one unusually high-salience retained event

The read model returns:
- location
- event count
- event kinds
- source-linked memories
- latest event time

It does not return:
- favorite
- affinity
- preference score
- home score
- attachment meter

Two citizens can have different place continuity evidence for the same physical location.

## Social Transmission Evidence

A custom candidate requires legitimate information travel.

Stage 3 API:

`record_social_pattern_evidence(memory_event_id, pattern_key, actor_id, transmission_mode, context_key="")`

The source must already be a real owner-scoped Memory event.

Supported transmission modes:
- observed
- heard
- participated

This function does not create the underlying source memory.

Communication/Simulation must first establish the legitimate source path.

## Custom Candidate Threshold

A custom candidate is always **owner-perspective evidence**, never a global culture fact.

Minimum:
- at least 3 source-backed transmission events
- at least 2 distinct actors
- at least 2 simulation days
- at least one actor other than the observing citizen

One private citizen repeating an action can never satisfy this.

A custom candidate disappearing after source deletion is expected and correct.

## Verification

Social transmission evidence preserves the underlying Memory verification state.

Repeated unverified reports remain unverified.

A custom candidate may therefore contain mixed verified/unverified evidence.

Candidate existence does not upgrade claim truth.

## Score-Free Read Model

Memory exposes:

`GET /api/memory/patterns/{citizen_id}`

Optional:
- `location_id`

Payload sections:
- habit candidates
- place continuity evidence
- owner-perspective custom candidates

Semantics:
- habits are candidates, not identity
- place evidence is not favorite/preference
- customs are perspective, not global culture
- no global score
- source events remain authoritative

## Internal Python APIs

- `habit_candidates_for(owner_id, ...)`
- `place_continuity_for(owner_id, ...)`
- `custom_candidates_for(owner_id, ...)`
- `continuity_pattern_snapshot(owner_id, ...)`
- `record_voluntary_choice_evidence(...)`
- `record_social_pattern_evidence(...)`

## Simulation Handoff

Simulation/planner should:
- define deterministic voluntary-choice classification
- define deterministic context keys
- call Memory only for genuinely voluntary terminal decisions
- never mark recharge/survival/forced maintenance as voluntary habits
- treat habit candidates as decision evidence, never commands
- allow later choices to diverge freely
- never make a pattern physically legal merely because Memory exposes it

## Communication Handoff

Communication should:
- describe habits as observed recurring patterns, not personality facts
- preserve "seems to / often has / has recently tended to" style uncertainty where appropriate
- treat place meaning as citizen interpretation of source events, not a favorite field
- register social transmission evidence only after real information travel
- never say "our custom is..." merely because one citizen repeats behavior
- keep mixed/unverified source status visible
- never create a custom by saying one exists

## Assets Handoff

Assets may show:
- recurring-pattern evidence trail
- current/mixed/fading candidate state
- place-specific source events
- custom evidence actors/modes/sources

Assets must not show:
- habit meter
- preference score
- culture score
- favorite-place badge
- profession/role/class
- permanent trait icon

Preferred presentation:
"show the trail, not the title."

## Integration Locks

1. `memory_pattern_evidence` stores source links, not habit/custom truth.
2. Habit candidates require explicit voluntary-choice evidence.
3. Known survival/maintenance forced actions are excluded.
4. Habit threshold is 3 supporting events across 2 simulation days.
5. Later contrary choices can make a candidate mixed/fading without rewriting history.
6. Place continuity is personal experience evidence, not location knowledge or preference.
7. Custom candidates require real social transmission/observation.
8. Custom threshold requires 3 events, 2 actors, 2 days, and another actor.
9. One private habit is never a custom.
10. Candidate evidence stays citizen-scoped.
11. Repeated claims do not become verified through repetition.
12. Deleting source events removes their pattern justification.
13. No global habit/culture/reputation score.
14. No role/class/profession identity.
15. No automatic personality/preference inference.
16. No planner legality/mandatory behavior from Memory candidates.
17. Preserve `tests/smoke_v090_memory_stage3.py`.
18. No `update.json` publication from Stage 3 Memory.
