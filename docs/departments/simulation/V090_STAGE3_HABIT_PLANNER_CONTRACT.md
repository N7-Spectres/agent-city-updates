# v0.9 Stage 3 — Simulation Habit/Place/Custom Planner Contract

_Status: ready for downstream consumption_  
_Runtime branch: `simulation/v0.9-habits-stage3`_  
_Final clean head: `fb17d3a2fb0776c490cdd4805feae8ab97c763ac`_  
_Validation: GitHub Actions `36642152013` — PASS_

## Authority Boundary

Stage 3 historical patterns are context, not physics.

Simulation continues to own:
- physical legality,
- energy/safety/maintenance constraints,
- action start/completion,
- job outcomes,
- plan attachment,
- and the classification of whether an autonomous decision was sufficiently open/voluntary to become recurring-pattern evidence.

Memory continues to own:
- source-backed repeated-choice evidence,
- habit-candidate derivation,
- place continuity,
- owner-perspective social-pattern/custom evidence.

The planner may consider historical pattern evidence only after Simulation has already produced the legal autonomous action set.

## Voluntary Choice Provenance

New additive `jobs` fields:

- `voluntary_choice_eligible INTEGER NOT NULL DEFAULT 0`
- `voluntary_choice_context TEXT`
- `voluntary_choice_location_id TEXT`

An autonomous job is tagged as voluntary Stage 3 evidence only when all are true:

1. it was started by the autonomous planner path,
2. the planner had at least two legal autonomous actions,
3. the decision occurred during the normal active cycle,
4. the citizen supplied an intent reason,
5. the physical action is in the narrow voluntary-pattern allowlist,
6. the job is not attached to a persistent plan.

Current allowlist:
- `survey`
- `extract`
- `experiment`
- `fabricate`
- `plan_project`
- `construct`
- `talk`

Movement, travel, recharge, maintenance, cargo handling, waiting, guided-practice mechanics, and plan-bound jobs do not become voluntary habit evidence through this path.

## Deterministic Context Key

Simulation constructs the context key only from runtime facts:

`location:<location_id>|phase:<daily_phase>|open_choice`

No LLM-authored personality, preference, role, profession, or motive text enters the key.

## Retention Timing

A job tagged at start does not immediately become Memory evidence.

After the authoritative physical transaction completes successfully and commits, Simulation calls:

`record_voluntary_choice_evidence(...)`

using the canonical `jobs.id`, action, stored deterministic context, and stored location.

If Memory retention fails, the physical job result remains authoritative and a diagnostic history entry is written. Memory failure never rolls back physical reality.

## Planner Consumption

Planner context may consume:

- `habit_candidates_for(...)`
- `place_continuity_for(...)`
- `custom_candidates_for(...)`

Recurring-choice evidence is shown to the model only when:

- its context key exactly matches the citizen's current deterministic context, and
- its action is currently present in Simulation's already-legal autonomous action set.

The planner receives candidate state:
- `current`
- `mixed`
- `fading`

and explicit language that the evidence is historical, revisable, non-binding, and not a preference or identity.

Place continuity is personal retained history, not physical truth or a favorite-place claim.

Social custom candidates are owner-perspective source-backed evidence, not universal tradition or obligation.

## Non-Effects

Stage 3 patterns do not:

- add/remove/reorder legal actions,
- create a physical capability,
- change duration/material/energy costs,
- create competence,
- override recharge/safety/maintenance,
- override tools/materials/world state,
- override or create plans,
- prevent a new action,
- assign a profession/role/personality/preference,
- create culture/tradition truth.

## Regression Contract

Preserve:

- `tests/smoke_v090_memory_stage3.py`
- `tests/smoke_v090_simulation_stage3.py`

Simulation Stage 3 smoke verifies:

- Memory pattern evidence leaves `possible_actions` unchanged,
- matching source-backed pattern evidence enters planner context,
- place continuity enters planner context without favorite-place semantics,
- forced/maintenance/travel actions fail voluntary classification,
- one-option situations fail voluntary classification,
- a real autonomous successful job is tagged at start and retained only after completion,
- plan-attached work does not become free recurring-choice evidence.

No `update.json` or publication metadata change is authorized by this contract.
