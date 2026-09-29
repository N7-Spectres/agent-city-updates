# World & Simulation — Backlog

## v0.9 Stage 1 Integration

Implemented on `simulation/v0.9-continuity-stage1`:

- canonical citizen-owned plans
- source Memory links
- plan lifecycle transitions
- plan-linked physical jobs
- canonical practice evidence
- historical practice backfill
- bounded safe continuity read model
- planner plan-lifecycle contract
- merge-order-safe Memory facet backfill

Integration remaining:

1. merge Memory `memory/v0.9-causal-memory-stage1` with Simulation Stage 1
2. verify autonomous new-plan creation sees bounded causal Memory candidates
3. run both v0.9 Memory and Simulation smoke tests together
4. Communication consumes plan/practice sources for perspective-safe self-assessment/recognition
5. Assets consumes safe plan/practice read model
6. coordinator performs final Stage 1 integration matrix

## v0.9 Stage 2 — Practice / Competence / Teaching / Recognition

### Bounded competence effects
- derive only from `practice_events`
- distinguish activity families without creating classes
- include successes and failures
- cap physical effects conservatively
- Simulation owns any duration/success/efficiency modifiers
- preserve equipment/material/world constraints
- no competence from talk/proximity

### Self-assessment
- Memory retrieves personal evidence
- Communication phrases beliefs/interpretations
- Simulation metrics remain evidence, not identity
- no hidden "expert" title

### Social recognition
- citizen-specific perspective
- requires legitimate observation/communication history
- no global reputation score
- no automatic authority/leadership weight

### Teaching
- explicit mechanism required
- talking alone does not transfer practice
- teaching event needs teacher/learner, subject, real interaction, and bounded effect
- learner competence still requires later practice where appropriate

## v0.9 Stage 3 — Habits / Place Meaning / Customs

- repeated-action pattern detection
- citizen-specific place meaning
- recurring cooperation
- socially transmitted customs
- no authored routine without evidence
- no culture from one citizen's private habit

## Plan Follow-On Depth

- explicit superseding-plan relationship if useful
- plan interruption reason categories
- plan relevance to longer multi-step construction/research projects
- explainable plan prioritization without opaque priority score
- plan expiration only if citizen explicitly abandons/supersedes/revises it
- safe UI summaries without exposing Memory ranking internals

## Existing Physical Backlog

- generated resource lifecycle
- larger coordinate-native travel
- project-material transport
- cooperative multi-citizen jobs
- equipment transfer/shared caches
- active shared-activity cancellation/interruption
- global tangent-frame/lat-lon mapping

## Open Questions

- what bounded competence effects are meaningful without overwhelming equipment/material physics?
- should failed practice reduce confidence/self-assessment without reducing objective capability?
- what explicit teaching event should exist before any teaching effect is allowed?
- how should plan continuity interact with competing unfinished plans without an opaque hidden priority score?


## v0.9 Stage 1 Integration Gate

Before new Simulation feature work:

1. Coordinator merges `memory/v0.9-causal-memory-stage1` and `simulation/v0.9-continuity-stage1`.
2. Preserve both `agent_city/causal_memory.py` and `agent_city/continuity.py`.
3. Verify autonomous new-plan creation receives bounded causal Memory candidates after merge.
4. Run the complete v0.4-v0.8.7 regression matrix plus:
   - `tests/smoke_v090_memory_stage1.py`
   - `tests/smoke_v090_simulation_stage1.py`
5. Any merge conflict that changes source ownership, plan lifecycle semantics, practice eligibility, or hidden score behavior returns to World & Simulation / Memory for review.

Until that gate is complete, World & Simulation Stage 1 is feature-complete and stopped in REVIEW.
