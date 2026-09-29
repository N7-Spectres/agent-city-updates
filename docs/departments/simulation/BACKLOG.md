# World & Simulation — Backlog

## v0.9 Stage 2 Integration

Implemented on `simulation/v0.9-competence-stage2`:

- on-demand family-specific competence derivation from practice events
- bounded duration-only physical effect
- failed-attempt partial experience
- job audit fields for competence/guidance
- real two-citizen guided-practice session
- one-use learner support on next real matching task
- autonomous guided-practice legal action
- score-free competence read endpoint
- full regression smoke coverage

Integration remaining:

1. Memory consumes `guided_practice_sessions.id` and competence source contract without turning it into identity
2. Communication consumes guided-practice event + safe competence evidence for questions/self-assessment/recognition
3. Assets consumes safe read model and avoids proficiency meters/titles
4. coordinator merges Stage 2 departments on `release-v0.9.0-stage1-integration`
5. run full regression plus all Stage 2 focused smokes

## v0.9 Stage 2 Follow-On Questions

- should Memory retain every guided session or only meaningful/first/repeated milestones?
- should Communication expose objective duration reduction at all, or only practice trail?
- should guided-practice support expire after long simulated time, or remain one-use until consumed?
- should construction competence later distinguish planning/staging from hands-on construction?
- should future tool/material diversity justify narrower competence evidence families?

## v0.9 Stage 3

Habits / place meaning / social customs remain next only after Stage 2 integration is green.

- repeated-action pattern detection
- citizen-specific place meaning
- recurring cooperation
- socially transmitted customs
- no authored routines
- no culture inferred from one private habit

## Existing Physical Backlog

- generated resource lifecycle
- larger coordinate-native travel
- project-material transport
- cooperative multi-citizen jobs
- equipment transfer/shared caches
- active shared-activity cancellation/interruption
- global tangent-frame/lat-lon mapping


## v0.9 Stage 2 Integration Gate

Before new World & Simulation feature work:

1. Memory finishes Stage 2 source-backed guided-practice/competence retention.
2. Communication consumes Simulation + Memory for competence-safe dialogue/question/recognition behavior.
3. Assets consumes the final safe Stage 2 read models.
4. Coordinator integrates Simulation + Memory + Communication + Assets on the v0.9 Stage 1 integrated base.
5. Run the complete v0.4-v0.8.7 regression matrix, all four v0.9 Stage 1 smokes, and all Stage 2 department smokes.
6. Any merge conflict affecting competence families, evidence weighting, duration caps, guided-practice lifecycle, one-use consumption, physical bottleneck dominance, or source identity returns to World & Simulation for review.

Until that gate is complete, World & Simulation Stage 2 is feature-complete and stopped in REVIEW.


## v0.9 Stage 3 — Simulation Complete / Integration Pending

Implemented on `simulation/v0.9-habits-stage3`:

- Simulation-owned voluntary-choice classification
- deterministic runtime context key
- source tagging on canonical jobs
- post-commit Memory retention
- source-backed recurring-pattern planner context
- current-location place-continuity context
- owner-perspective social-pattern context
- no action legality or physical-effect changes
- `tests/smoke_v090_simulation_stage3.py`

Validation:
- branch head `fb17d3a2fb0776c490cdd4805feae8ab97c763ac`
- CI `36642152013` PASS
- complete v0.4-v0.8.7 regression matrix
- all Stage 1 and Stage 2 smokes
- Memory Stage 3 smoke
- Simulation Stage 3 smoke

Remaining Stage 3 sequence:

1. Communication consumes canonical Memory + Simulation Stage 3 contracts.
2. Assets audits/implements only after final safe Communication/read-model contract.
3. Coordinator assembles all Stage 3 departments on the definitive Stage 2 line.
4. Run the full matrix including all Stage 3 smokes.
5. Review v0.9.0 release readiness only after green integration.

World & Simulation should remain stopped unless merge feedback or a new physical Stage 3 issue is routed.
