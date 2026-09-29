# v0.9 Stage 3 — History Pattern Memory Contract

_Status: Memory & Social implementation contract_  
_Base: `release-v0.9.0-stage2-integration@f680275a78b9da71a43f3c79217f292796b7843d`_

## Purpose

Stage 3 lets accumulated history leave source-backed grooves in continuity without turning those grooves into identity labels, command queues, favorite-place fields, or authored culture.

Core law:

> **Persistent behavior must have a traceable history.**

Stage 3 Memory therefore exposes evidence bundles. Downstream systems may interpret them only within their own authority.

## 1. Recurring Voluntary Pattern Evidence

Runtime:
- `agent_city.pattern_memory.behavior_pattern_snapshot_for(...)`
- `agent_city.pattern_memory.history_patterns_context_for(...)`

A recurring pattern is derived, never stored as XP/personality/preference state.

Current conservative Stage 3 context key:
- exact physical activity
- exact location

Pattern key:
- `<activity>@<location_id>`

Eligible Stage 3 activities:
- survey
- extract
- experiment
- fabricate
- construct
- local_inspect
- shared_local_activity

Explicitly excluded from automatic habit evidence:
- travel
- local_move
- deposit/cargo shuttling
- recharge
- maintenance/service actions

Reason: repetition forced by transport, survival, energy, maintenance, or infrastructure pressure must not automatically become personality/habit evidence.

Minimum evidence:
- 3 canonical practice events
- spanning at least 120 simulation minutes
- every pattern row re-validates the canonical `practice_events.id`

A retained Memory facet without its canonical practice source is insufficient.

### Current support vs historical support

The durable source trail remains available after a pattern weakens.

`currently_supported` is true only when the recent two-sim-day window contains:
- at least 2 matching source events, and
- more matching events than same-activity events at competing locations.

This is not a preference score.

It exists only to let later contrary history weaken a recurring pattern without deleting the older events.

Safe returned evidence:
- pattern key
- activity
- location
- literal event count
- first/last event time
- recent support count
- recent competing count
- current-support boolean
- source Memory IDs
- source practice-event IDs
- bounded recent source summaries

Not returned:
- habit strength score
- personality score
- preference score
- rank/tier
- profession/class
- hidden weighting

## 2. Citizen-Specific Place Meaning Evidence

Runtime:
- `place_meaning_snapshot_for(...)`

A place-meaning row exists only when one citizen has at least two retained source-backed Memory events carrying that location/place facet.

The row is citizen-scoped.

It may include:
- location ID
- literal evidence count
- first/last remembered event
- source Memory event IDs
- source types
- event kinds
- actual counterparties represented in those events
- bounded recent summaries

It does **not** mean:
- favorite place
- home
- sacred place
- preferred place
- globally important place
- physical property of the location

Two citizens may have different place-meaning evidence for the same location.

Physical location truth remains Simulation-owned.

## 3. Pattern Transmission

Durable table:
- `pattern_transmissions`

Validated ingress:
- `record_pattern_transmission(...)`

A transmission may be recorded only when:

1. a canonical `citizen_conversations.id` exists,
2. source actor and recipient are the actual two participants,
3. the supplied transmitted text appears verbatim in the source actor's durable transcript,
4. the source actor has a currently supported source-backed recurring pattern matching the transmitted pattern key.

The receipt begins:
- owner = recipient
- verification = unverified
- channel = face-to-face claim

It becomes a recipient Memory event:
- source type `pattern_transmission`
- source ID = transmission ID
- counterparty = source actor
- source conversation retained
- safe `pattern_key` facet
- safe activity/location facets when parseable

Speech does not create the underlying behavior.

Repeated retelling does not make a claim verified.

## 4. Social Custom Candidates

Runtime:
- `custom_candidate_snapshot_for(...)`

This is deliberately named a **candidate**, not a tradition/culture record.

It is owner-scoped.

A candidate requires:
- a qualifying currently supported recurring pattern, and
- real pattern transmission through durable face-to-face conversation.

For one recipient, the minimum social evidence is either:
- the recipient currently has the pattern + at least one other current pattern-holder transmitted it, or
- at least two distinct current pattern-holders transmitted the same pattern to the recipient.

If source actors later cease to have current support, the candidate can disappear while the old transmission remains remembered.

This preserves:
- history
- change
- disagreement
- perspective

It prevents:
- one private habit becoming culture
- a single conversation creating culture
- an omniscient global culture registry

## 5. Safe Aggregate Read Model

Runtime:
- `history_patterns_snapshot_for(citizen_id, ...)`
- HTTP: `GET /api/memory/patterns/{citizen_id}`

Returns only that citizen's:
- recurring pattern evidence
- place-meaning evidence
- custom candidates

Semantics explicitly state:
- source-backed
- soft/revisable history
- citizen-scoped place meaning
- repetition + transmission required for customs
- no global culture score
- no preference/identity labels

The endpoint is not a Skills page, personality API, or culture leaderboard.

## 6. Downstream Authority

### Simulation

May consume only source-backed, currently supported pattern evidence as a **soft choice influence among already legal actions**.

Memory does not authorize:
- actions
- materials
- tools
- knowledge
- competence
- outcomes

A recurring pattern must never override:
- survival/energy
- maintenance
- safety
- active jobs
- physical legality
- real resource constraints

### Communication

May discuss:
- source-backed repeated personal behavior
- personal place significance
- pattern claims actually transmitted

Communication must preserve perspective.

Communication is the correct owner for deciding whether a future real conversation contains a pattern transmission worth passing to `record_pattern_transmission(...)`.

### Assets

May render:
- source trail
- times
- literal counts
- source summaries
- remembered counterparties
- candidate provenance

Assets must not render:
- habit badges
- favorite-place badges
- tradition badges
- culture score
- personality adjective
- ranking/leaderboard

Rule:

> **Show the trail, not the title.**

## 7. Stage Boundary

Stage 3 does **not** implement the v1.0 developmental ladder:

- comparison
- inquiry
- general preference formation

A recurring contextual pattern is not a generalized preference.

No Stage 3 component should infer:
- “Bex prefers surveying”
- “Iri loves Seed Site”
- “Cato is traditional”
- “Vale is a mentor”

Those require later evidence/architecture, if ever justified.

## 8. Regression Requirements

Preserve:
- all v0.4-v0.8.7 regressions
- all v0.9 Stage 1 smokes
- all v0.9 Stage 2 smokes
- `tests/smoke_v090_memory_stage3.py`

Stage 3 Memory smoke verifies:
- 3-event source threshold
- maintenance repetition exclusion
- place evidence remains citizen-scoped and non-favorite
- transcript-grounded social transmission
- bystanders inherit nothing
- custom candidate requires repetition + transmission
- later contrary history weakens current support
- deleting canonical practice evidence changes pattern justification
- UI-safe Memory hides recall/reinforcement internals
- no global score/rank/preference identity is emitted

No `update.json` publication is authorized by this contract.
