# World & Simulation — State

_Last updated: 2026-09-29_
_Current published release: v0.8.7_
_Integrated v0.9 Stage 1 base: `release-v0.9.0-stage1-integration` @ `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`_
_Active branch: `simulation/v0.9-competence-stage2`_
_Final branch head: `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`_

## Mission

Own physical truth, plan/practice identity, and any objective physical competence effect.

> **The AI may decide intent. The simulation decides reality.**

> **Persistent behavior must have a traceable history.**

## v0.9 Stage 2 — Bounded Practice-Derived Competence

Implemented in:

- `agent_city/competence.py`

Competence is **derived on demand** from canonical `practice_events`.

There is no persisted XP, level, class, profession, rank, title, specialization, or universal reputation score.

### Activity Families

Physical competence is deliberately narrow:

- surveying → `survey`
- extraction → `extract`
- experimentation → `experiment`
- fabrication → `fabricate`
- construction → `construct`
- maintenance → chassis/battery/equipment/structure service

Practice in one family does not improve another family.

Travel, talk, waiting, proximity, agreement, UI activity, and guided-practice conversation do not create competence in these families.

### Evidence Weights

Each canonical practice event contributes only within its family:

- successful / discovery / verified completed work: 1.00
- legacy completed work with less detailed outcome: 0.75
- inconclusive / no-yield completed work: 0.50
- failed physical attempt: 0.25

Failures therefore provide limited experience but never create a permanent weakness.

### Bounded Physical Effect

Objective effect is job-duration only.

Practice-derived duration benefit:

`min(8%, 2% × log2(1 + weighted evidence))`

Examples:
- 0 evidence → 0%
- 1 successful practice → 2%
- 3 → 4%
- 7 → 6%
- 15+ approaches the 8% cap

The effect does **not**:
- reduce material cost
- reduce energy cost
- create knowledge
- bypass tools
- bypass location/route legality
- guarantee success
- create a new legal action
- create authority over another citizen

Unfamiliar work remains legally attemptable whenever ordinary Simulation rules allow it.

### Maintenance/Equipment Dominance

Competence is subordinate to physical bottlenecks.

For fabrication and experimentation:
- if the Basic Workbench condition/efficiency is below 90%, practice/guidance duration benefits are suppressed
- the degraded machine remains the bottleneck

This preserves v0.7 maintenance consequences.

Equipment condition, materials, energy, world state, and structure availability remain authoritative.

### Job Audit Fields

Relevant jobs now persist:

- `competence_family`
- `competence_duration_multiplier`
- `guidance_session_id`

This makes every physical duration difference reconstructable.

## Real Guided Practice

New durable table:

- `guided_practice_sessions`

Fields include:

- stable session `id`
- physical `job_id`
- `teacher_id`
- `learner_id`
- `activity_family`
- lifecycle `status`
- started/completed minute
- optional source conversation ID
- teacher/learner practice counts at start
- `consumed_by_job_id`
- summary

### Physical Requirements

Guided practice requires:

- two different citizens
- both physically co-present within ~2 m
- both free
- both with enough energy
- supported competence family
- guide has at least some real relevant practice evidence
- guide has more relevant evidence than learner

This relative evidence rule does not create an "expert" or "teacher" identity.

If a source citizen conversation ID is supplied, Simulation verifies that conversation belongs to those two citizens.

### Guided Practice Lifecycle

A guided-practice session is a real timed Simulation job:

- duration: 45 simulated minutes
- both citizens become physically occupied by the same job
- each pays 1% energy
- completion creates a durable completed session

The guided session itself does **not** create a `practice_events` row.

Talking/explaining alone therefore does not create competence.

### One-Use Learner Support

A completed guided-practice session creates a one-use matching-task support condition.

On the learner's **next real job in the same activity family**:

- guidance duration multiplier = 0.96
- practice-derived competence and guidance combine
- total combined benefit is capped at 10%
- session records `consumed_by_job_id`

Only the learner's completed/failed real task creates normal canonical practice evidence.

After use, the guidance session cannot apply again.

### Autonomous Guided Practice

When two free co-located citizens are close enough, Simulation may offer a `guided_practice` legal action if one has more real evidence in a family than the other.

At most the strongest current evidence-gap family is offered per learner.

New guided sessions are filtered out of quiet/wind-down work periods.

## Safe Read Model

New read-only endpoint:

`GET /api/competence/{citizen_id}`

It exposes factual source-backed fields only:

Per family:
- family name
- practice count
- completed count
- failed count
- objective duration multiplier
- duration reduction percentage
- source `practice_event_id` list

Also:
- guided-practice session history

Explicit semantics:
- derived from practice events
- no XP/levels
- no class/expertise label
- bounded physical duration effect only

The endpoint intentionally does **not** expose the internal weighted-evidence accumulator as a user-facing score.

Ordinary `/api/state` additionally includes factual `guided_practice_sessions[]` history.

## Recency / Tool / Material Policy

Stage 2 objective competence does not decay with recency.

Reason:
- Memory owns recall aging and confidence/perspective
- actual past physical practice remains historical physical evidence

Tool/material/environment differences do not create separate hidden subskills in Stage 2.

Instead:
- equipment/material/environment continue to affect the real job through existing physical systems
- competence stays family-level and modest
- future evidence may justify narrower variants if the world becomes meaningfully more diverse

## Validation

Final runtime code passed GitHub Actions:

`36618030044` — PASS

Passed:
- Python compilation
- JavaScript syntax
- full v0.4–v0.8.7 regression matrix
- all four v0.9 Stage 1 smokes
- `tests/smoke_v090_simulation_stage2.py`

The first Stage 2 run correctly exposed that familiarity was partially masking a 50%-condition workbench. The final rule was tightened so severe machinery degradation dominates competence.

The branch head after restoring release-only CI is:
`667f4659aeef9a9658d7e08f4ba7c54e267a38f9`

## Status

World & Simulation v0.9 Stage 2 competence/guided-practice substrate is ready for Memory, Communication, Assets, and coordinator integration.

No `update.json` or release metadata was changed.


## v0.9 Stage 2 Session Close

World & Simulation Stage 2 work for this session is complete.

Authoritative implementation:
- branch: `simulation/v0.9-competence-stage2`
- head: `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- integrated Stage 1 base: `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- final runtime validation: GitHub Actions `36618030044`

Handoffs delivered:
- Memory: canonical competence/guided-practice source IDs and retention boundary
- Communication: physical guided-practice lifecycle and competence-safe language boundary
- Assets: score-free competence/read-model contract
- COORDINATION: Simulation is in REVIEW; Memory is the next active Stage 2 dependency

No additional World & Simulation Stage 2 implementation is pending.

Resume only for:
- coordinator integration conflicts,
- a new Simulation inbox request,
- or authorized v0.9 Stage 3 physical work.

No release metadata or `update.json` was changed.
