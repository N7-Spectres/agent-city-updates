# Assets & Interface — State

_Last updated: 2026-09-29_
_Current published release: v0.8.7 @ `be617e6e870ec3f1914d76cdb85107a6efc294d7`_
_Current Assets activity: v0.9 continuity UI/read-model audit_
_Current runtime branch: none; implementation waits for the combined v0.9 Stage 1 integration base_
_Current status: REVIEW / WAITING FOR RUNTIME CONTRACT INTEGRATION_

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
