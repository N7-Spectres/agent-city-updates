# Assets & Interface — State

_Last updated: 2026-09-30_
_Current published release: v0.9.6 @ `8407870349a4331c19bc9b36554e45dd151733ba`_
_Current Assets activity: Home 3D World / RTS-style local world foundation_
_Current runtime branch: `release-v0.9.6` @ `8407870349a4331c19bc9b36554e45dd151733ba`_
_Current review surface: published updater v0.9.6_
_Current status: DONE / PUBLISHED_

## Mission

Make Agent City visually understandable and alive while never allowing presentation, animation, or generated assets to invent physical reality, hidden knowledge, equipment, quantity, capability, or spatial truth.

> **Simulation defines reality. Assets renders reality.**

## v0.8.1 Citizen Visual Assets + Map Readability — Complete

Assets & Interface completed the requested v0.8.1 visual hotfix.

Status:
**REVIEW**

### Citizen runtime art

Approved runtime-ready art is now committed for all six founding citizens:

- Aris
- Bex
- Cato
- Iri
- Noma
- Vale

Per citizen:
- equipment-free base-body full render
- matching head/token render

Runtime files:

`static/assets/citizens/<citizen>/full.webp`
`static/assets/citizens/<citizen>/token.webp`

Web sizing:
- full body: 200×300 WebP
- token: 96×96 WebP

The existing `CITIZEN_VISUAL_PROFILES` now points:
- `full` → approved full-body file
- `bust` → approved token file
- `token` → approved token file

The explicit semantic expression slots remain unfilled:
- neutral
- blink
- happy
- focused
- curious

A static token image is not treated as a semantic expression frame.

Optional equipment remains separate. All six `equipment_layers` stay empty.

Concept-art props still do not create:
- backpacks
- tools
- scanners
- medical gear
- cargo rigs
- capability
- inventory

Cato retains the intentionally heavy logistics silhouette.
Iri retains the slimmer/elegant construction silhouette.

### Character sheet rendering

Approved full-body art uses:
`object-fit: contain`

Small Home/directory/map tokens use:
`object-fit: cover`

The Citizens identity-slot copy now describes approved base-body identity rather than a placeholder.

### Map zoom/readability hotfix

Home now has explicit map controls:

- zoom out
- zoom level
- zoom in
- Region reset

State is presentation-only:

- `mapZoomLevel`
- `mapCenterOverride`

Zoom/focus changes only viewport center and scale.

It never writes:
- citizen x/y
- visitor x/y
- location x/y
- Simulation jobs
- observations
- any API physical state

Location-node click behavior:
- selects/focuses the location normally
- centers the viewport on that location's authoritative x/y
- moves to a closer presentation zoom
- never changes the location itself

### Location-node rectangle fix

The existing generous location-button hit target remains:

- width: 132 px
- minimum height: 56 px

But hover/focus no longer paints that rectangle.

Visual feedback is now only on:
- node dot
- node label

Keyboard `:focus-visible` remains obvious.

The node hit target explicitly preserves its center transform on hover/focus so the global button-hover rule cannot shift the location.

### Cluster readability

Citizen pixel separation grows modestly with presentation zoom, improving dense Seed Site readability without changing physical meter coordinates.

### Reduced motion

Zoom is an immediate presentation transform.

Node focus transitions and existing map movement smoothing continue to obey `prefers-reduced-motion`.

## Authority / Privacy Preserved

v0.8.1 does not change Simulation, Communication, or Memory semantics.

Assets still does not consume/expose:

- `planet_seed`
- hidden `generated_deposits`
- hidden body centers/axes/orientation
- hidden richness
- undiscovered procedural resources

The hotfix does not modify `update.json`.

## Validation

Dedicated hotfix test:
`tests/smoke_v081_assets.py`

Final static audit at branch head:

- 77 HTML IDs
- 73 JavaScript DOM refs
- zero missing refs
- zero duplicate IDs
- JavaScript parses
- all 12 runtime WebPs present
- all six full/token profile paths wired
- all six equipment-layer sets empty
- all five expression slots remain null for all six citizens
- hidden-world identifiers absent from Assets JS
- map zoom controls present
- node rectangular surface absent

### Full regression

GitHub Actions:
**`36467360376` — PASS**

Passed:

- Python compile
- JavaScript syntax
- all v0.4 regressions
- all v0.5 smoke suites
- all v0.6 smoke suites
- all v0.7 smoke suites
- all four v0.8 Stage 1 smokes
- all four v0.8 Stage 2 smokes
- v0.8.1 citizen-art/map hotfix smoke

The temporary PR-only workflow used for that validation was removed afterward.

### Official v0.8.1 base alignment

Coordinator added a workflow-only CI-noise commit after v0.8.0 publication.

Assets aligned with it before handoff:

- base: `release-v0.8.1`
- base commit: `c55eb76b89b35a660275ac97f095dcc4f511683e`
- branch: 16 ahead / 0 behind
- merge base: `c55eb76b89b35a660275ac97f095dcc4f511683e`
- release-smoke workflow content matches the base exactly
- runtime/art code was unchanged by this ancestry alignment

Per the coordinator's v0.8.1 CI policy, the definitive release matrix should run once at the final VERSION bump.

## Next Owner

**Coordinator / v0.8.1 Release**

Coordinator should:

1. review/merge PR #19 into `release-v0.8.1`
2. perform any desired manual visual check
3. bump VERSION to v0.8.1
4. let the definitive release workflow run once
5. publish/update release metadata only after that green run

No remaining Assets-owned blocker exists.


## Work Session Closure — v0.8.1

This Assets & Interface work session is closed.

Final handoff state:
- status: **REVIEW**
- branch: `assets/v0.8.1-citizen-visuals-map`
- head: `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- base: `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- PR #19: ready for review and mergeable
- full branch regression: `36467360376` — PASS
- Assets INBOX: empty
- remaining Assets blockers: none
- next owner: **Coordinator / v0.8.1 Release**

Do not resume implementation from this chat history. Future Assets work should begin from the repository handoff files and only continue if coordinator review feedback or a new milestone arrives.


## v0.9 Continuity UI Audit

Design/read-model audit complete:
`docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`

No v0.9 runtime UI code has been implemented yet.

Core rule:

> **Show the trail, not the title.**

Continuity UI must keep separate:
1. objective evidence/history
2. citizen-scoped remembered perspective
3. citizen interpretation/self-assessment
4. later repeated patterns such as habits/customs

Recommended Stage 1 Citizens → Continuity surfaces:
- Ongoing Plans
- Plan History
- Relevant Memories
- Recorded Practice
- attributed Self-Reflection only after the final integrated interpretation contract is safe

Hard exclusions:
- no XP/levels/skill bars
- no class/specialization/expert labels
- no universal reputation
- no hidden recall score or reinforcement count
- no friend/favorite-place/tradition badges inferred from raw history

### Safe dependencies

Simulation:
- `simulation/v0.9-continuity-stage1` @ `6b027708512671d8c851723fb900cfa1e0fcac73`
- CI `36603570434` PASS
- `GET /api/continuity/{citizen_id}`
- safe plan + objective practice history

Memory:
- `memory/v0.9-causal-memory-stage1`
- recall-bound practice surface is internally safe
- Assets requested a UI-safe remembered-event projection in Memory INBOX
- ordinary UI must not receive recall score/reinforcement count

Communication:
- continuity-language contract exists
- production binding waits for the coordinator's final recall-bound compatibility patch

### Runtime gate

Do not start continuity UI implementation until the coordinator hands off the combined v0.9 Stage 1 integration base.

Objective plans/practice can then use Simulation's safe endpoint.

Remembered-perspective/self-reflection UI additionally waits for final Memory/Communication safe projections.

Status:
**REVIEW / WAITING FOR RUNTIME CONTRACT INTEGRATION**

No `update.json` change is authorized.


## Work Session Closure — v0.9 Continuity UI Audit

This Assets & Interface work session is closed.

Final handoff:
- current published release: `v0.8.7`
- Assets deliverable: `docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`
- audit status: **REVIEW**
- runtime UI status: **WAITING FOR INTEGRATED SAFE CONTRACTS**
- runtime branch: none
- code changes: none
- Memory dependency request: routed to Memory INBOX
- immediate Assets inbox work: none
- `update.json`: unchanged

Next owner sequence:
1. Communication completes the recall-bound compatibility patch.
2. Coordinator assembles and validates the combined v0.9 Stage 1 base.
3. Memory supplies the UI-safe recalled-event projection.
4. Coordinator reactivates Assets for runtime continuity UI implementation.

Do not infer v0.9 runtime UI work from this chat after closure. Resume from repository handoffs only.


## v0.9 Stage 2 Competence + Guided-Practice UI Audit

Presentation/read-model audit complete:
`docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`

No Stage 2 runtime UI code has been implemented yet.

### Recommendation

Keep **Recorded Practice** as the primary competence-facing surface.

Literal event counts/history remain the safest explanation of accumulated experience.

If Simulation reports a non-zero bounded duration effect, show it only as compact factual text inside the existing Evidence / Record layer, for example:

> Comparable extraction tasks are currently 4.25% shorter from prior practice.

Do not visualize this as:
- proficiency bar
- mastery gauge
- ring
- stars
- tier
- rank

The 8% Simulation cap is an engineering safety bound, not a "100% mastery" endpoint.

### Guided practice

Show guided-practice sessions as factual event history.

Teacher / learner are event-local roles only.

Do not create:
- mentor
- trainer
- apprentice
- expert
- specialist
- permanent teacher/learner identity

A guided session itself does not create competence.

### Final safe contract split

Simulation:
- `GET /api/competence/{citizen_id}`
- objective practice counts
- completed/failed counts
- bounded duration reduction
- source practice event IDs
- guided-practice session history

Memory:
- `GET /api/memory/continuity/{citizen_id}`
- bounded remembered practice/guided-practice perspective
- source role / counterparty / verification / safe competence family
- no recall score
- no reinforcement count

Communication:
- attributed self-assessment / interpretation language
- asking for help without hidden expertise lookup
- no permanent mentor/expert labels

### Runtime gate

Assets checked repository branches on 2026-09-29.

Available:
- `release-v0.9.0-stage1-integration`
- Simulation Stage 2 branch
- Memory Stage 2 branch
- Communication Stage 2 branch

Not available:
- a coordinator-assembled v0.9 Stage 2 integration base

Assets must not merge Simulation/Memory/Communication branches itself.

Required order:

1. Coordinator assembles Simulation + Memory + Communication Stage 2 onto the green Stage 1 integration line.
2. Coordinator hands Assets that assembled Stage 2 base.
3. Assets implements the final continuity/competence/guided-practice UI.
4. Coordinator performs the final full integration/regression pass.

Current status:
**REVIEW / WAITING FOR COORDINATOR-ASSEMBLED STAGE 2 BASE**


## Work Session Closure — v0.9 Stage 2 UI Audit

This Assets & Interface work session is closed.

Final state:
- published runtime remains `v0.8.7`
- Stage 1 integrated base remains `release-v0.9.0-stage1-integration@de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- Stage 2 presentation audit is complete
- durable audit: `docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`
- runtime Assets Stage 2 code: not started
- Simulation Stage 2 contract: ready
- Memory Stage 2 contract: ready
- Communication Stage 2 contract: ready
- blocking dependency: coordinator-assembled upstream Stage 2 integration base
- Assets status: **REVIEW / WAITING**
- `update.json`: unchanged

Next owner:
**Coordinator / v0.9 Stage 2 Integration**

Required next sequence:
1. assemble Simulation + Memory + Communication Stage 2 onto the green Stage 1 integration base
2. validate that upstream combined base
3. hand the assembled base to Assets
4. Assets implements final citizen-sheet Stage 2 UI
5. coordinator runs the final combined regression matrix

Do not infer additional Assets runtime work from this chat after closure.


## v0.9 Stage 2 Runtime UI — Complete

Assets implemented the final Stage 2 citizen-sheet UI on the coordinator-assembled green base.

Base:
- `release-v0.9.0-stage2-integration`
- `ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- upstream combined CI `36633452433` PASS

Assets branch:
- `assets/v0.9-stage2-continuity-ui`
- head `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- 7 ahead / 0 behind base
- PR #26 ready and mergeable

Delivered:

### Evidence / Record
- consumes `GET /api/competence/{citizen_id}`
- per-family factual practice count
- completed count
- failed count
- non-zero `duration_reduction_percent` shown as compact measured-work text
- no frontend competence math
- no bars/gauges/tiers/ranks

### Guided Practice History
- factual event rows from `guided_practice_sessions[]`
- guide side: "Guided <counterpart>"
- learner side: "Practiced with <counterpart>"
- teacher/learner remain event-local roles
- historical legality snapshot counts are not surfaced

### Remembered Perspective
- continues to use `GET /api/memory/continuity/{citizen_id}`
- may display safe source role, counterparty, and competence-family context
- no recall score
- no reinforcement count

### Citizen Interpretation
- remains explicitly Communication-owned and attributed
- Assets does not synthesize self-assessment text from practice counts or measured effects

### Home
- no competence badges, counts, skill icons, or guidance clutter added

## Validation

Static final audit:
- 77 HTML IDs
- 73 JS DOM refs
- zero missing refs
- zero duplicate IDs
- JavaScript parses
- no frontend competence math
- final changed files:
  - `static/app.js`
  - `static/styles.css`
  - `tests/smoke_v090_assets_stage2.py`

Full branch regression:
- GitHub Actions `36634754010` — PASS
- Python compile
- JavaScript syntax
- complete v0.4→v0.8.7 regression matrix
- all four v0.9 Stage 1 smokes
- v0.9 Stage 2 Simulation smoke
- v0.9 Stage 2 Memory smoke
- v0.9 Stage 2 Communication smoke
- v0.9 Stage 2 Assets smoke

Temporary validation workflow removed after the green run.

## Next Owner

**Coordinator / v0.9 Stage 2 Final Integration**

Coordinator should merge PR #26 into the assembled Stage 2 line and rerun the complete matrix including `tests/smoke_v090_assets_stage2.py`.

No `update.json` or release metadata was changed by Assets.


## Work Session Closure — v0.9 Stage 2 Runtime UI

This Assets & Interface work session is closed.

Final handoff state:
- status: **REVIEW**
- branch: `assets/v0.9-stage2-continuity-ui`
- head: `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- base: `release-v0.9.0-stage2-integration@ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- PR #26: ready for review and mergeable
- full branch regression: `36634754010` — PASS
- Assets INBOX: empty
- remaining Assets blockers: none
- `update.json`: unchanged

Next owner:
**Coordinator / v0.9 Stage 2 Final Integration**

Coordinator can continue without this chat by using:
- this STATE file
- Assets DECISIONS/BACKLOG/OUTBOX
- PR #26
- `tests/smoke_v090_assets_stage2.py`
- `docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`

Do not infer additional implementation work from this chat after closure.


## v0.9.6 Home 3D World — Published

Status:
**DONE / PUBLISHED**

Release:
- branch: `release-v0.9.6`
- exact green runtime: `8407870349a4331c19bc9b36554e45dd151733ba`
- full CI: `36662871853` — PASS
- updater: v0.9.6

Delivered:
- Home World View now defaults to embedded 3D **Local** mode
- Local / Region / Planet controls remain available inside the Home world panel
- 3D citizen selection hands the citizen ID back to Home and opens the existing visit-selection flow
- Local 3D uses authoritative Simulation meter coordinates only
- local renderer mirrors Simulation-time Dawn / Day / Dusk / Night presentation phases
- old 2D region map remains available as an explicit fallback
- full-screen Planet view remains available from main navigation
- 3D renderer is read-only and performs no physical writes

Truth boundaries preserved:
- Simulation still decides reality
- local x/y is physically meaningful
- Planet/Region remain presentation shells until global geodesy exists
- no hidden planet seed, generated deposit bodies, richness, or undiscovered resource truth is exposed
- visitors gain no RTS-style command authority over citizens

Validation:
- Planet Lab JavaScript syntax check
- existing Planet Lab smoke
- `tests/smoke_v096_home_world3d.py`
- complete release regression matrix

Next visual direction:
- treat Home as an RTS-style **living-world viewer**, not an RTS command interface
- improve local camera feel, live movement interpolation, structure geometry, terrain readability, and day/night presentation without moving physical authority into Assets
