# Assets & Interface — Backlog

## Review / Release — v0.8.1

Assets implementation is complete.

Review surface:

- branch `assets/v0.8.1-citizen-visuals-map`
- head `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- base `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- PR #19 — ready for review
- full regression `36467360376` — PASS
- 16 commits ahead / 0 behind official hotfix base

Coordinator release checklist:

- merge/review PR #19
- visually verify Home head tokens
- visually verify Citizens full-body renders
- verify Cato retains heavy silhouette
- verify Iri retains slim silhouette
- verify zoom + / − / Region controls
- click Seed Site and other locations to confirm viewport focus
- confirm location hover/focus has no visible rectangle
- confirm keyboard focus highlights dot/label
- confirm dense Seed Site cluster improves as zoom increases
- confirm no optional gear appears from the art
- bump VERSION to v0.8.1
- run one definitive full release matrix
- publish only after green final run

## Completed — v0.8.1 Assets

- six approved full-body WebP assets
- six approved head/token WebP assets
- all six runtime visual profiles wired
- full-body contain rendering
- token cover rendering
- equipment-layer separation preserved
- expression-frame slots deliberately left null
- map zoom-in control
- map zoom-out control
- map Region reset
- zoom indicator
- presentation-only focused location viewport
- zoom-aware cluster separation
- visible node rectangle removed
- invisible generous node hit target preserved
- keyboard focus preserved
- reduced-motion preserved
- dedicated `tests/smoke_v081_assets.py`
- complete v0.4-v0.8.1 branch regression pass

## Later Citizen Visual Work

When separately approved assets exist:

- neutral expression frame
- blink frame
- happy `^ ^` frame
- focused frame
- curious frame
- optional richer bust crops
- transparent/higher-resolution archival masters if desired
- physically validated equipment overlays
- eventual 3D translation preserving the same silhouettes

Do not synthesize these into runtime canon without an approved source.

## Current Blockers

_None._

Next owner:
**Coordinator / v0.8.1 Release**


## Session Closed — v0.8.1

No open Assets implementation task remains in this session.

Resume only for:
- coordinator review feedback on PR #19,
- a visual regression found during final release validation,
- or a new milestone/work packet.

Current next owner:
**Coordinator / v0.8.1 Release**


## Compact status-bar rule

For the next character-sheet / Home-state polish pass:

- preserve the current compact Home citizen-card dimensions; do not make those cards taller or visually busier
- if Energy / Integrity move from plain percentages to bars, use **micro-bars**: thin, short, inline with the icon/value rather than full-width progress components
- keep the numeric percentage visible for precision
- use the same authoritative live values on Home and Citizen sheet
- clearly separate current charge/energy from long-term battery health/capacity
- character-sheet maintenance bars may be slightly wider because the sheet has more space, but should still remain visually quiet
- avoid stacking multiple large colored bars in one card
- prefer one small visual cue per metric over decorative gauges


## v0.9 Continuity UI — Audit Complete

Master audit:
`docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`

### Ready after coordinator Stage 1 integration

Citizens → Continuity first slice:

1. **Plans**
   - open/paused plans
   - next step
   - unresolved question
   - transition history

2. **Recorded Practice**
   - factual Simulation events
   - literal activity counts/grouping
   - completed/failed rows
   - no skill/proficiency UI

### Waiting on Memory UI projection

Relevant Memories / Why this plan exists.

Assets request is in Memory INBOX.

Need bounded owner-scoped display records with:
- memory event ID
- source type/ID/role
- event kind
- time
- summary
- verification/status
- pinned-by-plan
- safe display facets

Must omit:
- recall score
- reinforcement count
- hidden salience/importance ranking
- global aggregation

### Waiting on final Communication compatibility

Self-reflection and recognition presentation should bind only after Communication consumes Memory's recall-bound practice interface and stops exposing reinforcement count in natural-language evidence.

Do not bind production UI to the pre-patch continuity-language contract.

### Future Stage 2/3 UI dependencies

Do not implement until explicit safe read models exist:
- observer-specific recognition projection
- citizen-specific place-meaning projection
- habit projection
- custom/tradition projection

### Non-goals

- no Skills page
- no reputation page
- no class/specialization labels
- no XP
- no level bars
- no favorite-place badges
- no friend/trust badges
- no tradition slots
- no raw-event-count inference of continuity

## Current v0.9 Assets Blockers

Runtime implementation is waiting on:
1. coordinator combined v0.9 Stage 1 integration base
2. Memory UI-safe remembered-event projection
3. final Communication recall-bound compatibility for self-reflection/recognition

The design audit itself is complete.


## Session Closed — v0.9 Continuity Audit

No additional Assets work is authorized in this session.

Completed:
- doctrine review
- Simulation continuity read-model audit
- Memory recall/privacy audit
- Communication recognition/self-assessment audit
- proposed Citizens/Records continuity surfaces
- evidence vs perspective vs interpretation visual grammar
- explicit Stage 1 / future-stage UI gates
- Memory UI-safe projection request
- coordinator handoff

Resume only when:
- the coordinator supplies the combined v0.9 Stage 1 base,
- Memory returns the UI-safe recalled-event projection,
- Communication's final recall-bound compatibility is integrated,
- or a new Assets work packet arrives.


## v0.9 Stage 2 UI — Audit Complete

Master audit:
`docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`

### Runtime implementation once assembled base exists

Extend the existing Stage 1 Citizens → Continuity UI.

Evidence / Record:
- keep Ongoing Plans
- keep Recorded Practice
- add per-family completed/failed factual summary
- add measured work-effect text only when `duration_reduction_percent > 0`
- add Guided Practice History

Remembered Perspective:
- continue `GET /api/memory/continuity/{citizen_id}`
- allow guided-practice memories to appear naturally
- show source role/counterparty when useful
- keep internal recall/reinforcement hidden

Citizen Interpretation:
- consume final Communication-safe attributed language only
- do not derive self-assessment from counts/effects in JavaScript

### Explicit Stage 2 non-goals

- no Skills tab
- no XP/proficiency bars
- no 8%-cap-as-mastery-scale
- no expertise tiers
- no mentor/trainer badges
- no competence leaderboard
- no cross-citizen heatmap
- no frontend-derived competence
- no guidance "buff" icon

### Current blocker

There is no coordinator-assembled Stage 2 base branch yet.

Assets must not merge:
- `simulation/v0.9-competence-stage2`
- `memory/v0.9-experience-stage2`
- `communication/v0.9-guided-practice-stage2`

inside the Assets department branch.

Coordinator must first assemble those upstream branches onto:
`release-v0.9.0-stage1-integration`

Then hand the resulting base to Assets.

## Current v0.9 Assets Status

Audit: **complete**

Runtime Stage 2 UI: **waiting on coordinator-assembled Stage 2 base**


## Session Closed — v0.9 Stage 2 UI Audit

No further Assets work is authorized in this session.

Completed:
- audited Simulation Stage 2 competence read model
- audited Memory Stage 2 remembered guided-practice surface
- audited Communication Stage 2 interpretation/language contract
- decided literal practice history remains primary
- decided measured duration effect is text-only
- defined guided-practice event presentation
- prohibited mentor/expert/rank/proficiency UI
- identified coordinator-assembly dependency
- corrected COORDINATION sequencing so upstream Stage 2 is assembled before Assets implementation

Resume only when the coordinator provides the assembled Stage 2 base or routes explicit review feedback/new work.


## Review / Integration — v0.9 Stage 2 Assets

Implementation complete.

Review surface:
- branch `assets/v0.9-stage2-continuity-ui`
- head `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- base `release-v0.9.0-stage2-integration@ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- PR #26 — ready for review
- full regression `36634754010` — PASS
- 7 ahead / 0 behind

Coordinator review checklist:
- measured work effect appears only when non-zero
- effect is compact text, never a bar/gauge
- practice counts remain literal history
- failed/completed counts remain factual
- guided-practice rows use event-local role wording
- no mentor/trainer/expert identity appears
- Memory role/counterparty chips come only from safe projection
- Stage 1 continuity layers remain intact
- Home receives no competence clutter
- Interpretation layer does not synthesize citizen beliefs from counts
- `tests/smoke_v090_assets_stage2.py` remains in final matrix

## Completed — v0.9 Stage 2 Assets

- competence endpoint integrated into continuity cache
- factual per-family practice rows
- measured duration effect text
- guided-practice history
- source-role/counterparty/family remembered context
- quiet Stage 2 continuity styling
- Stage 2 Assets smoke
- full v0.4→v0.9 Stage 2 branch regression

## Current Blockers

_None for Assets._

Next owner:
**Coordinator / v0.9 Stage 2 Final Integration**


## Session Closed — v0.9 Stage 2 Runtime UI

No open Assets implementation task remains in this session.

Completed:
- competence read-model integration
- factual per-family practice summary
- compact measured duration-effect presentation
- guided-practice event history
- safe remembered role/counterparty/family context
- conservative Communication-owned interpretation boundary
- focused Stage 2 Assets smoke
- full v0.4→v0.9 Stage 2 regression

Resume only for coordinator review feedback, a discovered interface regression, or a new Stage 3 task.

Current next owner:
**Coordinator / v0.9 Stage 2 Final Integration**


## Next 3D World Iteration

Current published base:
- v0.9.6
- `release-v0.9.6@8407870349a4331c19bc9b36554e45dd151733ba`
- CI `36662871853` PASS

Priority order for the next Assets pass:
1. smoother RTS-style Local camera feel and sensible tilt/zoom limits
2. interpolate citizen presentation between authoritative state refreshes without inventing destinations
3. simple structure geometry anchored to validated structure coordinates
4. stronger local route/path readability
5. richer day/night lighting and settlement-light presentation
6. basic terrain height/readability from future Simulation-approved terrain state
7. keep Planet as pull-back context, not the default Home camera
8. preserve explicit 2D fallback until the 3D Home view is proven stable enough to retire it

Hard constraints:
- no citizen command controls
- no frontend physical state mutation
- no hidden seeded-world data exposure
- no invented global latitude/longitude
- no terrain/resources generated as physical truth by the renderer

## Current Assets Blockers

_None._

Next owner:
**Assets & Interface / next 3D world polish packet**


## Completed — v0.9.7 Marker Spread

- wider shared-point citizen token fan-out
- separate visitor offset below crowded citizen clusters
- no coordinate mutation
- dedicated `tests/smoke_v097_local_marker_spread.py`
- full release regression `36663515487` PASS


## Completed — v0.9.9 3D Route Motion

- smooth visual travel for real route jobs
- authoritative timing and endpoints only
- pause-aware visual motion
- perspective-scaled markers
- perspective-scaled shared-point fan-out
- dedicated `tests/smoke_v099_3d_route_motion.py`
- full release regression `36664664989` PASS


## Completed — v0.9.10 World-Space Cluster Fix

- removed screen-space citizen starburst positioning
- co-located presentation fan-out now lives in Local 3D world space
- direct camera projection owns final screen positions
- smooth route travel and perspective marker scaling preserved
- `tests/smoke_v0910_worldspace_cluster.py`
- full release regression `36665747233` PASS

Release process:
- qualifying future patch/polish candidates auto-publish after exact full green CI under the standing user authorization recorded in Assets DECISIONS
