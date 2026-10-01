# Agent City — Project State

_Last updated: 2026-10-01_

## Current Release

**v0.9.20 — Desktop Launcher Phase 1**

Agent City is a local-first autonomous mechanical civilization simulation. Six equal mechanical citizens live at Seed Site and act independently through validated simulation actions.

Core law:

> **The AI may decide intent. The simulation decides reality.**

Information law:

> **A citizen only knows what information could actually have reached them.**

Human users such as N7 are **visitors**, not gods, rulers, or omniscient operators.

## v0.9.20 Published Patch — Desktop Launcher Phase 1

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.20`
- exact green head: `a05361177139885a9410bad1273a1b270984cecc`
- full CI: `36867429553` — PASS
- published updater: `v0.9.20`

Delivered:
- hidden Windows launcher via `pythonw.exe`
- one-click desktop shortcut setup helper
- duplicate-server detection
- readiness wait before browser open
- automatic browser open to local Agent City
- local launcher/server logs under `data/`
- reserved Assets icon path `static/assets/app/agent-city.ico`
- no auto-update supervision, tray controls, or launch-at-startup yet

Roadmap:
- `docs/AGENT_CITY_DESKTOP_LAUNCHER_ROADMAP.md`

## v0.9.19 Published Patch — Iri Backdrop Box Fix

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.19`
- exact green head: `d25df836d59d00ea4a9e48c4434e53272517803a`
- full CI: `36852571411` — PASS
- published updater: `v0.9.19`

Delivered:
- removed Iri's visible rectangular source matte in Local
- strengthened backdrop cleanup from simple corner-color matching to border-connected flood removal
- added luma/color-distance backdrop criteria and 8-neighbor connectivity
- crops the cleaned sprite to its remaining alpha bounds
- preserves enclosed dark visor / joint detail
- keeps Iri's v0.9.18 scale, travel, selection, and layering behavior
- Cato and Aris unchanged
- Region and Planet remain body-free
- no Simulation authority changes

Validation:
- complete historical regression matrix
- updated v0.9.18 Iri smoke
- new `tests/smoke_v0919_iri_backdrop_fix.py`
- JavaScript syntax checks

## v0.9.18 Published Patch — Iri Local World Body

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.18`
- exact green head: `d30231229af9c157e8fe98a3b35bfaab962e865b`
- full CI: `36807758825` — PASS
- published updater: `v0.9.18`
- `update.json` downloads the exact green v0.9.18 runtime

Delivered:
- Iri is the third Local citizen promoted from a circular token to a full-body presentation
- slender researcher / analyst silhouette with pearl, lilac, and cyan presentation language
- relative presentation scale `0.848` from the approved approximately 1.78 m visual cue
- minimum Local zoom-out readability floor `0.50`
- existing Iri repository body source receives connected-border backdrop cleanup at render time
- cleanup preserves internal dark mechanical detail rather than globally color-keying dark pixels
- lilac/cyan ground contact, selection, and travel-only presentation
- v0.9.16 body stacking protection inherited
- same authoritative Simulation position and real route-travel interpolation as Cato and Aris
- Region and Planet remain free of citizen body markers
- Bex, Noma, and Vale remain token-based pending separate reviewed rollouts

Truth boundary:
- Iri's height/scale values and sensor-halo motif are presentation canon only
- concept equipment does not become inventory or capability
- no physical dimension, coordinate, collision body, locomotion, equipment, cargo, or capability is created by Assets
- Simulation remains authoritative

Validation:
- complete historical regression matrix through v0.9.17
- JavaScript syntax checks
- `tests/smoke_v0918_iri_world_body.py`
- durable handoff: `docs/departments/assets/IRI_PREBLENDER_WORLD_BODY.md`

## v0.9.17 Published Patch — Correct Aris Runtime Sprite

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.17`
- exact green head: `0d9f384c614f192da4423c3907a851ac8b0a2b9c`
- full CI: `36771435841` — PASS
- published updater: `v0.9.17`
- verified Aris runtime blob: `f8811d359b1a232b0f27ce41d87163d5ac4cc57f`
- verified file size: `14,262 bytes`

Delivered:
- replaced the incorrect PNG bytes previously shipped for Aris
- live runtime now uses the exact transparent sprite validated visually
- added a dedicated release smoke that hashes the binary and verifies the exact Git blob
- v0.9.16 body-layering behavior remains intact
- no Simulation authority changes

## v0.9.15 Published Patch — Aris Transparent PNG Body

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.15`
- exact green head: `2edf2cd5fcd828973fd0f636e2d5119abe3d94e0`
- full CI: `36755833871` — PASS
- published updater: `v0.9.15`
- `update.json` downloads the exact green v0.9.15 runtime

Delivered:
- Aris's Local full-body asset is now a true transparent RGBA PNG
- rectangular matte/background artifact removed
- existing Aris relative scale and zoom-out readability floor preserved
- existing authoritative Local position and real route-travel interpolation preserved
- Cato remains unchanged
- Region / Planet continue to omit citizen body markers

Validation:
- complete regression matrix through v0.9.14
- Aris focused smoke now verifies PNG signature and RGBA color type
- no Simulation authority changes

## v0.9.14 Published Patch — Aris Local World Body

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.14`
- exact green head: `9c1b51e419a030434ecf1271f80cb5a127216701`
- full CI: `36752065690` — PASS
- published updater: `v0.9.14`
- `update.json` downloads the exact green v0.9.14 runtime

Delivered:
- Aris is the second Local citizen promoted from a circular token to a full-body presentation
- approved Aris concept reference is preserved under his citizen asset tree
- Aris uses the same authoritative Simulation position and real route-travel interpolation as Cato
- leaner relative presentation scale preserves his approximately 1.85 m visual identity against Cato's heavier/taller silhouette
- minimum Local zoom-out readability floor keeps Aris identifiable at the widest Local camera distance
- Aris receives cyan ground-contact, hover/selection, and travel-only presentation treatment
- Region and Planet continue to omit citizen body markers
- Bex, Iri, Noma, and Vale remain token-based pending separate one-at-a-time rollouts

Truth boundary:
- Aris's height/scale values are presentation canon only
- no physical dimension, coordinate, collision body, locomotion, equipment, cargo, or capability is created by Assets
- Simulation remains the sole authority over physical reality

Validation:
- complete regression matrix through v0.9.13
- JavaScript syntax checks
- `tests/smoke_v0914_aris_world_body.py`
- historical route-motion and Cato tests preserved as behavioral invariants
- durable handoff: `docs/departments/assets/ARIS_PREBLENDER_WORLD_BODY.md`

## v0.9.13 Published Patch — Cato Grounding Polish

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.13`
- exact green head: `25db296bec37d436dae8b4d76c3a8138caa6c77e`
- full CI: `36715953570` — PASS
- published updater: `v0.9.13`
- `update.json` downloads the exact green v0.9.13 runtime

Delivered:
- Cato's full-body Local presentation has a slightly stronger heavy silhouette
- foot-line anchoring tightened to improve ground contact
- subtle ground-contact ring added beneath the body
- hover/selection treatment now reinforces the ground contact as well as the sprite
- travel-only bob reduced to better match Cato's heavy presentation
- travel shadow compresses in sync with the visual bob
- reduced-motion keeps both body and ground shadow static

Truth boundary:
- all v0.9.13 size/anchor values are presentation measurements only
- no physical height, width, mass, collision body, locomotion model, position, travel, equipment, or capability was added by Assets
- Simulation remains authoritative for physical reality

Validation:
- complete regression matrix through v0.9.12
- Planet Lab JavaScript syntax
- `tests/smoke_v0913_cato_grounding.py`
- v0.9.12 body smoke updated to preserve the foot-anchor invariant without freezing one CSS tuning percentage

## v0.9.12 Published Patch — Cato Pre-Blender World Body

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.12`
- exact green head: `e40870e2550a9b211eee77308661be701368ae68`
- full CI: `36711965473` — PASS
- published updater: `v0.9.12`
- `update.json` downloads the exact green v0.9.12 runtime

Delivered:
- Cato is the first Local-map citizen rendered as a full body rather than a circular token
- transparent equipment-free Cato body asset at `static/assets/citizens/cato/world/front.webp`
- body is foot-anchored to Cato's authoritative Local position
- existing authoritative route interpolation carries the body during real travel jobs
- camera-depth scaling applies to the body
- body-shaped hover/selection treatment
- subtle travel bob only while a real travel job exists
- shared-point presentation spacing widens when the larger body is present
- empty `.world-equipment-layer` reserved for future validated gear
- future presentation slot reserved for `static/assets/citizens/cato/world/model.glb`
- other citizens remain token-based

Truth boundary:
- v0.9.12 is a 2.5D pre-Blender presentation pilot, not a real rigged model
- no concept-art cargo harness, hook, crate, or other prop becomes inventory/equipment
- no physical position, facing, travel, cargo, equipment, or capability is created by Assets

Validation:
- complete regression matrix through v0.9.11
- Planet Lab JavaScript syntax
- `tests/smoke_v0912_cato_world_body.py`
- durable handoff: `docs/departments/assets/CATO_PREBLENDER_WORLD_BODY.md`

## v0.9.11 Published Patch — Authoritative GitHub Update Feed

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.11`
- exact green head: `1b4398b5642fe4d0b821bf58e773c1626c26dc58`
- full CI: `36666508423` — PASS
- published updater: `v0.9.11`
- `update.json` downloads the exact green v0.9.11 runtime

Delivered:
- GitHub raw update feeds are translated internally to GitHub repository-contents API requests
- branch/ref/file resolution now comes from repository state rather than raw CDN freshness
- GitHub API request uses raw-file Accept header
- stable user-saved feed URL remains unchanged
- cache-busted raw request remains as fallback for API failure/rate limiting and for non-GitHub feeds
- all v0.9.10 3D world-space cluster behavior remains intact

Validation:
- complete regression matrix through v0.9.10
- `tests/smoke_v0911_github_update_feed.py`

## v0.9.10 Published Patch — World-Space Local Token Clusters

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.10`
- exact green head: `158751b3c0e95b0d0c8e997219e7148b2c8044d2`
- full CI: `36665747233` — PASS
- published updater: `v0.9.10`
- `update.json` downloads the exact green v0.9.10 runtime

Delivered:
- co-located citizen/visitor fan-out moved from post-projection screen pixels into Local 3D world space
- cluster presentation now naturally follows camera orbit, tilt, and zoom
- final screen positions are direct camera projections of world-space marker positions
- v0.9.9 smooth authoritative travel remains intact
- perspective-scaled marker size remains intact
- physical Simulation coordinates remain untouched
- no frontend movement authority added

Validation:
- complete regression matrix through v0.9.9
- Planet Lab JavaScript syntax
- `tests/smoke_v0910_worldspace_cluster.py`

## v0.9.9 Published Patch — 3D Route Motion + Perspective

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.9`
- exact green head: `d942d38ea0f82d056a6494a2f7be64041974d5c8`
- full CI: `36664664989` — PASS
- published updater: `v0.9.9`
- `update.json` downloads the exact green v0.9.9 runtime

Delivered:
- citizens with real `travel` jobs move continuously along the authoritative route in Local 3D
- motion derives from real job `start_minute` / `end_minute`
- visual progress uses Simulation's actual `time_ratio`
- pausing Agent City freezes visual travel
- marker size responds to camera depth
- shared-point citizen fan-out scales with perspective
- visitor/citizen tokens feel less like fixed HUD stickers
- selected-citizen focus follows rendered travel position
- no coordinate writes
- no invented travel or destination

Validation:
- complete regression matrix through v0.9.8
- Planet Lab JavaScript syntax
- `tests/smoke_v099_3d_route_motion.py`

## v0.9.8 Published Patch — Fresh Update Checks

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.8`
- exact green head: `2d0d01c51db30e495360fe04b9c23b115c9ec3c0`
- full CI: `36663881198` — PASS
- published updater: `v0.9.8`
- `update.json` downloads the exact green v0.9.8 runtime

Delivered:
- every manifest check now adds a unique cache-busting query parameter
- manifest requests send `Cache-Control: no-cache, no-store, max-age=0`
- manifest requests send `Pragma: no-cache`
- saved user feed URL remains stable; freshness is applied only to outbound requests
- includes v0.9.7 wider Local 3D marker spread

Validation:
- complete regression matrix through v0.9.7
- `tests/smoke_v098_update_cache.py`

## v0.9.7 Published Patch — Wider Local Marker Spread

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.7`
- exact green head: `c783ff6875136de1edd5852676246ef69a442fd0`
- full CI: `36663515487` — PASS
- published updater: `v0.9.7`
- `update.json` downloads the exact green v0.9.7 runtime

Delivered:
- co-located citizen tokens fan out into a wider screen-space ring in Local 3D
- shared authoritative meter coordinates remain untouched
- visitor marker is offset farther below crowded citizen clusters
- tokens leave the fan-out automatically when authoritative citizen coordinates diverge
- hover/focus readability improved for spread tokens
- no frontend movement authority added
- no Simulation state writes

Validation:
- complete regression matrix through v0.9.6
- Planet Lab JavaScript syntax
- Home 3D integration smoke
- `tests/smoke_v097_local_marker_spread.py`

## v0.9.6 Published Patch — Home 3D World

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.6`
- exact green head: `8407870349a4331c19bc9b36554e45dd151733ba`
- full CI: `36662871853` — PASS
- published updater: `v0.9.6`
- `update.json` downloads the exact green v0.9.6 runtime

Delivered:
- Home **World View** is now 3D-first rather than a separate-lab-only experience
- embedded Planet Lab opens in **Local** mode by default
- Local / Region / Planet remain available inside the Home world panel
- Local mode continues to use authoritative Simulation `x_m / y_m`
- click-selecting a citizen in embedded 3D hands selection back to Home's visit interface
- local renderer mirrors simulation-time Dawn / Day / Dusk / Night visual phases
- previous 2D region map remains available through an explicit **2D fallback** control
- full-screen Planet view remains available from main navigation
- embedded/full-screen 3D remains read-only and performs no physical state writes

Validation:
- complete regression matrix through v0.9.4
- Planet Lab smoke
- Planet Lab JavaScript syntax check
- `tests/smoke_v096_home_world3d.py`

## v0.9.5 Published Patch — Planet Lab

**Status: published from the fully regression-tested release line**

- branch: `release-v0.9.5`
- exact green head: `3a5b226cda19775f080b726d79e79c72c016c0c1`
- full CI: `36661886711` — PASS
- published updater: `v0.9.5`
- `update.json` downloads the exact green v0.9.5 runtime

Delivered:
- official `/planet-lab` route
- main navigation entry: **3D Planet Lab**
- dependency-free browser WebGL prototype
- click/drag orbit camera
- mouse-wheel zoom
- Planet / Region / Local view modes
- keyboard mode switching and camera reset/focus
- clickable known-location markers
- Local mode uses authoritative Simulation `x_m / y_m`
- Local mode shows real citizen positions using approved citizen head-token art
- safe structure, route, and visitor placement from existing read state
- simulated time influences globe lighting presentation
- no external 3D runtime or CDN dependency
- no Simulation write actions from Planet Lab
- no hidden planet seed / generated deposit geometry / richness exposure

Truth boundary:
- Local mode is the physically meaningful meter-space view.
- Planet/Region mode is a clearly labelled presentation shell built from the existing local tangent frame.
- v0.9.5 does not claim global latitude/longitude or full planet terrain truth.

Validation:
- complete regression matrix through v0.9.4
- `tests/smoke_planet_lab.py`
- Python compile and JavaScript syntax checks

## v0.9.4 Published Patch — Zero-Energy Charger Recovery

**Status: published from the fully regression-tested patch line**

- branch: `release-v0.9.4`
- exact green head: `ed73598148e0f23b64834e9f716f3fab6ba2364e`
- full CI: `36657268659` — PASS
- published updater: `v0.9.4`
- publication manifest commit on `main`: `ee51c23a7ece7d787e30b9871ae2a38c3c6a5393`
- `update.json` downloads the exact green v0.9.4 runtime

Delivered:
- detects idle citizens at absolute 0% energy who are stranded outside a charger's 5 m radius while already inside the same location as an operational charger
- recovery is Simulation-owned diagnostic/admin correction, not a visitor action or fictional citizen action
- recovery grants no energy and creates no job
- only the citizen's local coordinate is aligned to the nearest operational charger at that same location
- the citizen is made planner-eligible so the existing critical-energy autonomy rule resumes ordinary charging
- citizens at other locations are never teleported to a charger
- recovery runs once at startup and during world ticks, then becomes a no-op once the citizen is within real charger range
- every correction is recorded in settlement history as a diagnostic admin recovery

Observed target case:
- Bex was observed at Seed Site with 0% energy after earlier social-drain behavior
- v0.9.2 prevents future social starvation
- v0.9.4 repairs the remaining impossible zero-energy local-offset deadlock so the existing save can recover naturally on startup

Validation:
- complete regression matrix through v0.9.3
- `tests/smoke_v094_zero_energy_recovery.py`
- Python compile and JavaScript syntax checks

## v0.9.3 Published Patch — Citizen Sheet Navigation

**Status: published from the fully regression-tested patch line**

- branch: `release-v0.9.3`
- exact green head: `2826784e2bde768e7388535820e217361d234cc9`
- full CI: `36656229586` — PASS
- published updater: `v0.9.3`
- publication manifest commit on `main`: `5131bdb72082650cf6403b6c9437995953186e47`
- `update.json` downloads the exact green v0.9.3 runtime

Delivered:
- citizen sheet now prioritizes an at-a-glance profile dashboard
- stable overview contains:
  - physical state
  - current energy / integrity
  - long-term battery/joint maintenance
  - current work
  - cargo
  - equipped gear
  - projects
  - active persistent plan summary
- deep information moved to a right-side on-demand navigator:
  - Continuity
  - Memories
  - Experience
  - Patterns & Places
  - Social
  - Knowledge
- each detail button exposes a quiet count without inventing rank/importance
- selected detail view persists across normal auto-refresh and page reload
- desktop deep-detail panel is sticky and internally scrollable, preventing the full character page from becoming an archive-length scroll
- smaller screens collapse to one column and use horizontally scrollable detail controls
- Stage 1 Evidence / Record, Remembered Perspective, and Citizen Interpretation semantics remain explicit
- Stage 2 competence/guided-practice evidence remains unchanged
- Stage 3 recurring-choice/place/social-pattern truth boundaries remain unchanged

Validation:
- complete regression matrix through v0.9.2
- `tests/smoke_v093_citizen_sheet_navigation.py`
- historical Stage 1 Assets/UI smoke updated only for the new presentation path, not weakened
- Python compile and JavaScript syntax checks

## v0.9.2 Published Patch — Conversation Polish + Social-Energy Protection

**Status: published from the fully regression-tested patch line**

- branch: `release-v0.9.2`
- exact green head: `ea4a838fa10a557ac6d3f032a55e1dc94a84012f`
- full CI: `36654523357` — PASS
- published updater: `v0.9.2`
- publication manifest commit on `main`: `0f3bbd0bc7682e5345eb04a086b0adbfbb771f6d`
- `update.json` downloads the exact green v0.9.2 runtime

Delivered:

**Natural citizen-conversation summaries**
- summary prompts now use citizen names rather than backend participant-role labels
- user-facing summaries explicitly forbid schema/process wording such as:
  - initiator
  - target citizen / conversation target
  - source job
  - action target
  - proposal state
- a defensive normalization pass converts role leakage to citizen names before persistence
- claim-safe summary rules from v0.8.4 remain unchanged

**Critical-energy social protection**
- autonomous planning no longer selects a citizen below the critical recharge threshold as a talk or guided-practice target
- a start-time autonomous recheck closes the race where the target becomes critical after action enumeration
- physical talk remains legal in `possible_actions()`; this is an autonomy/survival priority, not invented physical impossibility
- being selected as somebody else's talk target no longer resets the listener's `last_planned_minute`
- once the conversation ends, an overdue low-energy citizen can immediately regain planner priority and choose charging

Observed diagnostic context:
- a user-observed Bex state at Seed Site showed 1% energy despite no remembered travel
- repository review confirmed a real starvation path: repeated incoming talks cost 1% energy to both participants and previously reset the listener's planner clock
- this mechanism can explain stationary energy drain, but the exact historical cause of that specific local-save state is not asserted without inspecting that save's event history

Validation:
- complete prior regression matrix through v0.9.1
- `tests/smoke_v092_natural_summaries.py`
- `tests/smoke_v092_social_energy.py`
- Python compile and JavaScript syntax checks

## v0.9.1 Published Patch — History Records Polish

**Status: published from the fully regression-tested patch line**

- branch: `release-v0.9.1`
- exact green head: `371911bd9b337924ba1b960cb794caccd991c150`
- full CI: `36652854090` — PASS
- published updater: `v0.9.1`
- publication manifest commit on `main`: `d4a9d46c32cd967d5cd3b95dd5f83e1b43c8a0d8`
- `update.json` downloads the exact green v0.9.1 runtime

Delivered:
- Records → History now uses a desktop two-column layout:
  - Recent Citizen Conversations on the left
  - Settlement Chronology on the right
- conversations are paginated at 8 per page
- chronology is paginated at 12 per page
- pagination is backed by bounded database queries rather than an unbounded browser archive
- expanded “Read exchange” rows remain open across the 4-second state refresh
- selected conversation/chronology pages remain stable across refresh
- narrow screens stack the two History columns
- Home recent activity remains lightweight and unchanged

Validation:
- complete prior regression matrix through v0.9.0
- new `tests/smoke_v091_history_records.py`
- Python compile and JavaScript syntax checks

## v0.9.0 Published Release — Civilization Continuity

**Status: published from the definitive green runtime**

- release branch: `release-v0.9.0`
- exact green runtime head: `10e866fd693af7b8ba24d34331a19dde281ee670`
- definitive full CI: `36649456577` — PASS
- published updater: `v0.9.0`
- publication manifest commit on `main`: `7c080eda9678ad6f5a6368a9af101f4460af29c0`
- `update.json` package points directly to the exact green runtime commit

v0.9 now includes the complete three-stage continuity architecture:

**Stage 1 — Causal Memory + Persistent Plans**
- durable source-linked Memory with bounded active recall
- persistent citizen plans and plan transitions
- physical practice-event archive
- perspective-safe self-assessment/recognition foundations
- Continuity UI with Evidence / Remembered Perspective / Citizen Interpretation separation

**Stage 2 — Practice, Competence, Teaching, Recognition**
- family-bounded competence derived from real practice
- bounded duration-only physical effects
- real guided-practice sessions
- one-use learner support on later matching real work
- competence-safe dialogue and UI
- no XP, levels, classes, ranks, or universal reputation

**Stage 3 — Habits, Place Meaning, Social Customs**
- source-backed recurring voluntary-choice evidence
- current / mixed / fading historical pattern states
- citizen-specific place continuity
- socially transmitted recurring-pattern evidence
- soft planner context only after actions are already legal
- grounded face-to-face pattern transmission
- evidence-first continuity UI
- no habit/favorite-place/tradition badges, culture score, authored routine, or general preference system

Final validation includes:
- complete v0.4 through v0.8.7 regression matrix
- all four v0.9 Stage 1 smokes
- all four v0.9 Stage 2 smokes
- all four v0.9 Stage 3 smokes
- Python compilation and JavaScript syntax validation

v0.9 remains governed by:

> **Persistent behavior must have a traceable history.**

The next developmental milestone remains v1.0, but no v1.0 comparison/inquiry/general-preference machinery is included in v0.9.0.

## v0.9 Stage 1 Integrated Baseline

**Status: historical Stage 1 baseline incorporated into published v0.9.0**

- branch: `release-v0.9.0-stage1-integration`
- immutable green head: `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- combined CI: `36615685005` — PASS
- VERSION on integration branch: `0.9.0` for test/release-line preparation only
- publication later advanced `update.json` to the final v0.9.0 runtime

Integrated:
- Memory causal archive / bounded active recall
- persistent citizen plans + plan lifecycle/source links
- canonical physical practice events
- recall-bound self-assessment/teaching language
- perspective-safe recognition without global reputation
- UI-safe remembered-event projection
- citizen-sheet Continuity UI:
  - Ongoing plans
  - Why this exists
  - Plan history
  - Recorded practice
  - Relevant memories
  - explicitly separated Citizen Interpretation layer
- all v0.4 through v0.8.7 regressions remain green
- all four v0.9 Stage 1 smokes pass together

Integration corrections discovered by combined CI:
- standalone Simulation smoke expected fallback Memory wording; integrated assertion now verifies source-linked causal recall
- Communication isolated test doubles were expanded to match the real integrated Continuity/Memory interfaces
- no runtime authority rules were weakened to make tests pass

Stage 1 does **not** yet add:
- competence modifiers
- teaching skill transfer
- habits/routines
- place attachment
- customs/culture
- authored roles/classes/reputation

## v0.9 Stage 2 Upstream Integrated Baseline

**Status: historical Stage 2 upstream baseline incorporated into published v0.9.0**

- branch: `release-v0.9.0-stage2-integration`
- green head: `ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- combined CI: `36633452433` — PASS
- publication later advanced `update.json` to the final v0.9.0 runtime

Integrated Stage 2 upstream systems:
- family-bounded practice-derived competence
- duration-only bounded physical competence effects
- failed-attempt experience weighting
- degraded-workbench bottleneck dominance
- real two-citizen guided-practice sessions
- one-use learner guidance support on the next matching real task
- Memory retention/recall for guided-practice experience
- teacher/learner role memories remain event-local
- self-only measured competence language
- perspective-safe guided-practice/question/recognition language
- no global reputation, XP, levels, classes, mentor/expert titles, or conversation-only skill transfer

Combined integration correction:
- Communication's isolated Stage 2 competence test double was expanded to supply the integrated `guided_practice_snapshot(...)` interface.
- runtime semantics were unchanged.

Next:
- Assets implements the audited Stage 2 citizen-sheet UI on this exact base.
- Coordinator then runs the final Stage 2 matrix including the Assets smoke before Stage 3 begins.

## v0.9 Stage 2 Fully Integrated Baseline

**Status: complete and incorporated into published v0.9.0**

- branch: `release-v0.9.0-stage2-integration`
- immutable green head: `f680275a78b9da71a43f3c79217f292796b7843d`
- definitive combined CI: `36637062562` — PASS
- `update.json` remains on published v0.8.7

Integrated:
- family-bounded practice-derived competence
- bounded duration-only competence effects
- failed-attempt experience weighting
- severe machinery degradation remains the dominant bottleneck
- real two-citizen guided-practice sessions
- one-use learner support on the next matching real task
- guided-practice Memory with event-local teacher/learner roles
- active-recall teaching/self-assessment boundaries
- self-only measured competence language
- perspective-safe recognition/questions
- citizen-sheet factual competence history
- compact measured-work effect text
- guided-practice history
- remembered guided-practice perspective
- no XP, levels, classes, ranks, expert/mentor/trainer badges, global reputation, or conversation-only skill transfer

Validation:
- complete v0.4-v0.8.7 regression matrix
- all four v0.9 Stage 1 smokes
- Simulation Stage 2 smoke
- Memory Stage 2 smoke
- Communication Stage 2 smoke
- Assets Stage 2 smoke

Stage 2 integration corrections were test-harness compatibility only; runtime authority rules were not weakened.

Stage 3 is now the only remaining v0.9 implementation stage.

## Next Major Milestone — v0.9 Civilization Continuity

The v0.9 architecture doctrine is now locked in:

- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

Core continuity law:

> **Persistent behavior must have a traceable history.**

v0.9 is explicitly not an RPG-class layer or generated biography system.

Locked direction:
- Memory is causal infrastructure, not flavor text.
- persistent plans must survive across unrelated actions and remain revisable/abandonable.
- practice may create differentiated competence only from real completed actions.
- no behavior-causing miner / engineer / researcher / builder identity labels.
- self-assessment must be grounded in personal history.
- recognition must emerge through citizen-specific perspective rather than a universal reputation score.
- places may accumulate different meanings for different citizens.
- visitor continuity must come from real source-linked encounters.
- habits require repeated behavior.
- customs/culture require repetition plus social transmission.
- bounded active recall and durable archive are separate concepts.

Planned stage order:
1. **Stage 1 — Causal Memory + Persistent Plans**
2. **Stage 2 — Practice, Competence, Teaching, Recognition**
3. **Stage 3 — Habits, Place Meaning, Social Customs**

Memory & Social is the first Stage 1 dependency. Simulation may audit persistent-plan/event requirements in parallel, but implementation contracts must preserve Memory provenance/retrieval boundaries.


## Recent Visual Foundation

**v0.8.1 — Citizen Visual Assets + Map Readability**

Shipped visual follow-up to v0.8.0.

Release:
- branch: `release-v0.8.1`
- immutable runtime commit: `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`
- final CI: `36468997929` — PASS

Delivered:
- approved runtime-ready full-body + token WebP art for Aris, Bex, Cato, Iri, Noma, and Vale
- full / bust / token slots wired to those assets
- optional equipment layers remain separate and empty unless runtime equipment later supplies them
- map zoom out / zoom in / Region reset
- click-to-focus presentation centering for locations
- location hit targets remain generous but no longer render the visible rectangular hover/focus surface
- denser citizen clusters become more readable as presentation zoom increases
- Simulation/Communication/Memory semantics unchanged

## Current Milestone

**v0.8.7 — Route Travel Visualization**

Published presentation hotfix:
- branch: `release-v0.8.7`
- immutable runtime commit: `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- final CI: `36595479188` — PASS

Delivered:
- legacy route-travel citizen tokens now interpolate between origin/destination using authoritative job progress
- visual map position corresponds to the same progress fraction shown in the citizen card
- traveling tokens display a compact percentage badge
- travel tooltip/accessibility text includes destination and approximate route distance remaining
- meter-space map no longer pins route travelers to their origin coordinate until arrival
- interpolation remains presentation-only and never writes x/y back to Simulation
- local meter movement and shared-activity movement semantics remain unchanged
- dedicated `tests/smoke_v087_route_tokens.py` regression added

**v0.8.6 — Stranded Citizen Recovery**

Published energy-safety hotfix:
- branch: `release-v0.8.6`
- immutable runtime commit: `a72f96b763671f01c5a8aa0ba41d87f7eb6b9a09`
- final CI: `36591711494` — PASS

Delivered:
- charger-bound travel treats the operational charger itself as the safety destination
- no extra 5% post-arrival return reserve is required when the destination has an operational charger
- citizens must still possess enough current energy to pay the real travel cost
- trips to non-charging destinations retain the normal return-energy safety margin
- a critically low citizen who reaches charging remains governed by v0.8.5 autonomous recharge priority
- no teleportation or position rewrite is needed for the observed Iri 6% Resin Grove case
- dedicated regression reproduces Iri at Resin Grove with 6% energy and verifies successful return followed by charging priority

### Emergency Admin Recovery Rule

When a confirmed software bug creates an impossible/deadlocked civilization state, a minimal admin correction is allowed as a repair mechanism.

Prefer, in order:
1. fix the underlying rule so the existing save can recover naturally,
2. if natural recovery is impossible, apply the smallest direct state correction necessary,
3. record the intervention as diagnostic/admin recovery rather than pretending it was an in-world citizen action.

Admin recovery must not become a routine visitor power, shortcut normal consequences, grant resources/technology, or rewrite legitimate citizen outcomes.

**v0.8.5 — Daily Rhythm & Recharge**

Published autonomy/energy rhythm release:
- branch: `release-v0.8.5`
- immutable runtime commit: `5b2395d7e7643a3d7ac9a82ac68090fc97b5f0b7`
- final CI: `36498819565` — PASS

Delivered:
- 06:00–20:00 normal autonomous active cycle
- 20:00–22:00 wind-down that favors wrapping up, returning, unloading, maintenance, conversation, and recharge over starting major new work
- 22:00–06:00 low-activity/recharge cycle that prevents idle citizens from treating night as another full work shift
- critically low autonomous citizens prioritize a physically legal charger or safe return toward charging
- overnight charging repeats real charge jobs until current Energy reaches true usable battery capacity
- degraded battery health is treated as the full-charge ceiling; no pointless charge cycle is offered at that ceiling
- existing active jobs are allowed to finish normally rather than being cancelled by time-of-day
- `possible_actions()` remains the physical-legality contract; daily rhythm is applied only through the autonomous-planning layer
- charger availability requires both physical proximity and matching named location
- world presentation now reflects dawn / daylight / dusk / night without changing Simulation truth
- all v0.4–v0.8.4 regressions plus `tests/smoke_v085_daily_rhythm.py` pass

The release preserves the authority split:
- Simulation defines physical legality and energy truth
- autonomous planning applies daily rhythm to legal choices
- presentation reflects simulated time but never changes reality

**v0.8.4 — Conversation Summary Truth**

Published Communication hotfix:
- branch: `release-v0.8.4`
- immutable runtime commit: `ff78aab0e85331238eb67c989952a72499d1ed78`
- final CI: `36487822361` — PASS

Delivered:
- citizen-to-citizen summaries remain social records rather than physical evidence
- claim-safe summary verbs favor reported / discussed / compared / planned / agreed
- conversation summaries may not independently upgrade claims into validated / confirmed / verified / proved / demonstrated / established facts
- agreements to inspect, travel, recharge, build, or test remain intentions until Simulation records the physical action/outcome
- a citizen reporting inventory/status is still a report to the listener, not independent verification
- Simulation, Memory, personality, and UI authority remain unchanged


**v0.8.3 — Citizen Personality + Natural Dialogue**

Published behavior/dialogue patch:
- branch: `release-v0.8.3`
- immutable runtime commit: `e4d216b133a18dc4c68e1bba1ceb0457e952efb6`
- final CI: `36478041248` — PASS

Delivered:
- distinct stable personality tendencies and voice guidance for Aris, Bex, Cato, Iri, Noma, and Vale
- personality influences preferences, tone, curiosity, caution, and cooperation without granting authority or extra knowledge
- no default leader/ruler/command weighting
- visitor and citizen-to-citizen dialogue keeps planner/system vocabulary backstage
- natural speech replaces phrases such as "active job queued" / "current intent" / "propose shared action" where ordinary language fits
- planner may use personality as a soft behavioral bias only; Simulation legality, knowledge boundaries, survival constraints, and physical outcomes remain authoritative
- Simulation and Memory semantics unchanged


**v0.8.2 — Live State Readability**

Published UI-only patch:
- branch: `release-v0.8.2`
- immutable runtime commit: `9a11b2bc21ba2338d6b231924036bf6d5935475c`
- final CI: `36473856852` — PASS

Delivered:
- Home citizen cards keep the same compact dimensions
- current Energy and Integrity now use thin inline micro-bars plus exact percentages
- Citizen sheet uses the same authoritative live Energy/Integrity values and matching meters
- long-term battery health/capacity is clearly separated from current charge
- no Simulation, Communication, Memory, or physical-state semantics changed


v0.8.0 — Living World is assembled, fully regression-tested, versioned, and published from immutable runtime commit `a870982ba947fcc5af08ca190de396ae4308b645`.

Final release validation:
- GitHub Actions run `36462126434`
- Python compilation passed
- JavaScript syntax passed
- all v0.4 regressions passed
- all v0.5 smoke suites passed
- all v0.6 smoke suites passed
- all v0.7 smoke suites passed
- all four v0.8 Stage 1 smokes passed
- v0.8 Stage 2 Simulation smoke passed
- v0.8 Stage 2 Communication smoke passed
- v0.8 Stage 2 Memory smoke passed
- v0.8 Stage 2 Assets/UI smoke passed

Major shipped v0.8 changes:

- persistent hidden planet seed
- deterministic meter-scale local world truth derived from seed + coordinate
- spatially coherent terrain/geology/resource generation instead of per-scan rerolls
- stable spatial deposit bodies with repeat-encounter identity
- additive migration of existing named landmarks/deposits into the spatial model
- authoritative local x/y positions for citizens, visitors, structures, projects, and locations
- real local exploration/movement jobs with distance/terrain/energy consequences
- coordinate-aware return-energy reserve
- validated local observations with bounded uncertainty and stable evidence IDs
- explicit visitor-linked shared walk/inspect lifecycle with separate proposal, accept, start, reject, active, and complete states
- Communication grounding for visitor RP, hypotheses, capabilities, and tool use
- bounded spatial Memory for nearby prior observations and completed shared exploration
- continuous meter-space map presentation using only authoritative movement fields
- shared-action proposal/accept/reject/progress UI
- observation uncertainty rings and baseline privacy
- restored citizen job progress bars and Enter-to-send chat
- six-citizen visual-profile framework with removable equipment layers
- presentation-only local AssetQueue scaffold and render-tier contract
- no Blender/3D runtime dependency yet

The release preserves the authority chain:
- conversation/exchange = social source
- Communication proposal = intent/UI projection
- Simulation shared activity = canonical physical shared event
- Simulation job = active physical movement
- spatial observation = validated exploration evidence


The richer provenance layer for individual claims, source reliability, promises, help, and validated cooperation remains future depth. Those features must wait for explicit Communication provenance and Simulation event references rather than being inferred from ordinary conversation.

## Current Emergent Behavior

The citizens are already showing early social behavior originally expected closer to v0.4.0:

- Noma traveled to Resin Grove while Cato was working there
- Noma later initiated conversation with Cato
- Bex initiated conversation with Aris before considering distant travel
- Iri sought Vale because Vale might have useful local information

These are not scripted relationship events. They emerged from local awareness, legal talk actions, and autonomous planning.

## Departments

### Assets & Interface
Path: `docs/departments/assets/`

Owns:
- UI layout
- map readability
- citizen markers / avatars
- animation and visual state
- Control Room layout
- visual assets

### Memory & Social
Path: `docs/departments/memory/`

Owns:
- citizen memory
- relationship history
- visitor memory
- bounded context / retrieval / summarization
- social continuity

### Communication & Perception
Path: `docs/departments/communication/`

Owns:
- face-to-face conversation
- who can perceive whom
- information transfer
- last-known knowledge
- speech/hearing/observation
- future communication systems if citizens actually invent them

### World & Simulation
Path: `docs/departments/simulation/`

Owns:
- jobs and action validation
- movement
- resources
- energy/integrity
- extraction
- fabrication/construction later
- research outcomes later
- world geography and physical truth

## Coordination System

Departments communicate asynchronously through repository files:

- `docs/departments/COORDINATION.md` — shared work board
- each department's `INBOX.md` — incoming requests/dependencies
- each department's `OUTBOX.md` — completed handoffs/results

The main coordinator may route messages between these files.

A department chat should begin by reading its inbox and may usually be resumed with the instruction:

> **Check your inbox and continue.**

The only manual step still required is opening/activating the relevant ChatGPT department conversation; chats cannot directly wake or message one another.

## Handoff Rule

Departments own systems, not reality.

If one department needs another system changed, record the dependency in that department's `BACKLOG.md` or `STATE.md` instead of silently changing another department's rules.

Cross-department changes should preserve these two laws:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

## Development Pace

Use **stable, meaningful milestones**, not a stream of micro-updates.

If citizens begin demonstrating later-stage behavior early, strengthen the systems underneath that behavior instead of suppressing it to preserve the roadmap order.

See also:

- `docs/AGENT_CITY_UI_ROADMAP.md`
- `docs/V100_DEVELOPMENTAL_AUTONOMY_NOTES.md` — future v1.0 scaffolding/autonomy notes; not current v0.9 scope
- `docs/departments/README.md`


## Civilization Autonomy Cutoff

Agent City should eventually reach a deliberate handoff point where development stops providing civilization-specific solutions and instead provides only the underlying world capabilities needed for citizens to invent their own responses.

Core rule:

> **Updates add possibility, not answers.**

Before v1.0, development may add missing substrate such as:
- fabrication and construction
- research and experimentation
- persistent material properties
- energy and maintenance rules
- geography, terrain, atmosphere, weather, and ecology
- tools/equipment as physical objects
- memory, perception, communication provenance, and planning support
- project and settlement-state mechanics

Development should not grant specific downstream solutions merely because a citizen problem appears. Examples that should normally emerge from citizen need, knowledge, materials, and fabrication rather than be directly unlocked by an update include:
- radios or other communication devices
- backpacks, carts, or hauling systems
- roads
- atmospheric processors
- specialized industrial tools
- settlement expansions or outposts

Around v1.0, the intended philosophical transition is:

- before v1.0: build the sandbox and its physical laws
- after v1.0: primarily maintain, visualize, optimize, fix, and deepen the sandbox while the citizens build the civilization

Post-v1.0 updates may still add new physical domains or richer simulation, but should avoid answering a problem the citizens are currently facing for them.

If citizens struggle with a logistical, environmental, or technical problem, prefer allowing them to adapt through existing systems rather than shipping a handcrafted solution.


## Shipped v0.6 Scope

### Research / Discovery

- hidden world-specific material properties
- experiment actions with simulation-determined outcomes
- successful and failed experiments persist as knowledge
- learned processes may become reproducible only after discovery
- no visible predetermined technology tree
- communication technology remains something citizens may eventually invent, not a granted unlock

### Known Truth vs World Truth

Ordinary citizen/visitor-facing views must not expose raw hidden Simulation state.

A location may begin with almost no information beyond what has actually been mapped or observed.

Knowledge sheets fill in only through valid:
- direct observation
- survey
- measurement
- experiment
- physical record
- conversation / information transfer

Unknown resources or properties remain absent rather than appearing as greyed-out secrets.

### UI / Navigation

Home should answer:
> **What is happening right now?**

Home prioritizes:
- map
- citizen quick list
- selected-citizen chat
- compact visitor-location badge
- meaningful live alerts only

Citizens view should answer:
> **What do we know about this citizen?**

Locations view should answer:
> **What do we know about this place?**

Locations should feel like a field notebook that gradually fills in as the civilization learns.

### Character / Location Visuals

Citizen detail pages should reserve a full-body visual identity area and show current physical equipment/configuration when supported by validated state.

Location detail pages should include a simple scene/visual representation now, with room for richer graphics later.

### Known v0.5 bug carried into v0.6

Visitor availability messaging must correctly resolve the other participant in a talk job and distinguish:
- remote location
- visitor traveling
- citizen traveling
- citizen currently busy/talking

Do not display a self-reference such as "Vale is currently speaking with Vale."


## Conversation / Coordinator Continuity

The GitHub documentation is the durable handoff layer for future Agent City coordinator chats.

A new coordinator conversation should begin by reading:
1. `docs/AGENT_CITY_PROJECT_STATE.md`
2. `docs/AGENT_CITY_UI_ROADMAP.md`
3. `docs/departments/COORDINATION.md`
4. the relevant department `STATE.md` / `DECISIONS.md` / `BACKLOG.md` files when planning new work

Important boundary:
- GitHub notes preserve project architecture, decisions, roadmap, release lineage, department contracts, and handoffs.
- The local Agent City SQLite save remains authoritative for the civilization's changing physical state. Do not copy transient citizen positions/cargo/activity into GitHub as if they were current forever.

Recent coordinator decisions already captured in the repository include:
- v0.8.1 Citizen Visual Assets + Map Readability shipped from immutable runtime commit `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`
- v0.8.0 Living World shipped from immutable runtime commit `a870982ba947fcc5af08ca190de396ae4308b645`
- the planned v0.7.1 follow-up scope is folded into v0.8.0; there will not be a separate 0.7.1 release unless a critical hotfix appears
- v0.8 Living World should begin with a persistent planet seed and meter-scale deterministic spatial truth: the hidden world is derived from seed + coordinate, scans reveal rather than reroll reality, and discovered deposits retain stable physical identity/spatial extent
- v0.7.1 visitor roleplay grounding should keep natural face-to-face RP while treating visitor-described physical details as claims/observations until Simulation validates them; chat must not become a hidden world editor
- v0.7.0 Maintenance, Consequences & Home Polish shipped from immutable runtime commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- long-term world generation may use a persistent hierarchical random seed so planets/star systems are deterministic hidden reality rather than handcrafted or rerolled on discovery
- if citizens eventually invent spaceflight, additional seeded planets/moons/stars can be revealed through the same system
- stellar-scale engineering, including a possible Dyson-style swarm, is allowed only as an emergent citizen-built outcome rather than a predetermined unlock
- v0.8 should begin a local asynchronous asset-generation foundation: validated Simulation objects/projects can queue visual work for a local worker/procedural 3D pipeline; visual generation never blocks or defines physical reality
- v0.6.0 Research, Discovery & Knowledge UI shipped
- Home should answer "What is happening right now?"
- Citizens and Locations should hold deeper detail
- Location notebooks reveal only knowledge actually discovered/communicated
- future citizen creation/population growth is possible in principle but must emerge from real research/fabrication/energy/identity systems
- full-body citizen visual/character-sheet direction is desired
- visitor location should remain compact on the map
- future citizen-to-visitor requests/alerts should obey real communication mechanisms
- weather/atmosphere are future world substrate, not arbitrary punishment
- updates should add possibility, not answers

If a future chat needs to resume coordinator work, these repository files should be treated as the persistent source of truth rather than relying on old chat transcript memory alone.


## Shipped v0.7 Scope

### Maintenance / Consequences
- gradual component/equipment/structure wear
- lubrication and repair needs where physically appropriate
- battery health as a long-term condition separate from current charge
- damaged tools/structures can lose capability or become unavailable
- repair/replacement/preventative maintenance are real simulation actions
- maintenance should create occasional decisions, not constant busywork
- no arbitrary RPG debuffs; consequences come from physical condition/state

### Home Polish
- citizen rail roughly matches map height and scrolls internally
- future-ready citizen search/filter
- Visit/chat roughly matches map height on desktop
- chat remains internally scrollable with anchored input
- compact Home Recent Activity, around 5 meaningful events/conversations
- Records remains the full archive

### Avatar First Stage
- full-body 2D/static citizen identity area on Citizens
- smaller matching map/home token
- simple state-driven browser animation only
- no Mixamo or 3D rigging required in v0.7
- visual equipment changes only when backed by validated physical equipment

### Talk Reliability
- investigate repeated valid talk attempts ending without durable exchanges
- preserve the hard invariant that failed generation never creates fake dialogue
- improve reliability and add internal diagnostics for failure causes
