# Assets & Interface — Backlog

## Review / Integration — v0.7

Assets implementation is complete.

Coordinator/runtime validation:

- integrate PR #7 with Simulation / Communication / Memory v0.7 branches
- run `tests/smoke_v070_assets.py`
- run the full v0.4-v0.7 regression suite
- verify desktop citizen/world/Visit height alignment
- verify citizen internal scrolling and search/filter
- verify long chat keeps input/actions anchored
- verify Recent Activity stays capped and meaningful
- verify diagnostics are absent from normal Recent Activity
- verify failed talk attempts remain events only
- verify avatar fallback consistency across Home/directory/map/Citizens
- verify reduced-motion behavior
- verify citizen battery/chassis maintenance state against real v0.7 runtime
- verify equipment current capability uses effective modifiers
- verify non-operational/service-due equipment remains visible
- verify structure condition/efficiency/operational state
- verify maintenance-event Records history
- verify Home maintenance alerts use only authoritative state and remain bounded
- verify responsive behavior below desktop

## Completed in v0.7 Assets

- full-height desktop Home rails
- internal citizen/chat scrolling
- citizen search/filter
- compact Recent Activity
- real stored-conversation summary path
- diagnostic filtering
- lightweight 2D avatar framework
- fallback full-body/token identity
- validated-state animations
- reduced-motion support
- citizen battery/chassis maintenance presentation
- equipment condition/effective-capability presentation
- structure condition/efficiency presentation
- bounded maintenance event history
- bounded Home maintenance alerts
- v0.7 Assets smoke test

## Later

- unique citizen full-body/token art
- authoritative equipment overlays on avatars
- richer work-site/map visuals
- richer location scene assets
- planet/globe representation

## Current Blockers

_None within Assets._ PR #7 is ready for coordinator integration.


## Next Owner

**Coordinator / Integration**

No additional Assets implementation is pending before v0.7 assembly. New Assets work should come from integration-test findings or a new routed request.


## v0.8 Home Glanceability

### Restore glanceable citizen job progress

The original v0.3-v0.5 citizen cards showed active-job progress directly in each citizen row:
- elapsed / total simulation minutes
- ETA
- a compact progress bar

This was removed during the v0.6 Home simplification when citizen rows were compressed to name/activity/location/cargo/vitals. The underlying `jobProgress(...)` helper and authoritative start/end simulation minutes still exist.

Restore a compact progress indicator for active jobs in the Home citizen rail, especially travel, extraction, survey, charge, fabrication/construction, experiment, and maintenance jobs.

Requirements:
- progress derives only from authoritative Simulation job start/end/current sim minute
- show remaining/ETA in a compact glanceable form
- keep the citizen rail internally scrollable and population-scalable
- avoid making idle citizen rows taller
- preserve responsive layout and reduced visual clutter
- do not duplicate or contradict the selected-location/visitor travel progress card


## v0.7.1 Chat Keyboard Polish

### Enter-to-send visitor chat
- pressing Enter in the visitor chat input sends the message
- Shift+Enter inserts a newline for multi-line messages
- keep the Talk/send button fully functional
- do not send while an IME composition event is active
- avoid duplicate submission from keydown + form submit
- preserve current chat validation/disabled-state behavior


## Planned v0.8 — Citizen Visual Asset System

Master design:
`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

### Base assets
- clean equipment-free full body for Aris / Bex / Cato / Iri / Noma / Vale
- consistent transparent canvas / body anchors
- bust reference
- head token reference
- strong accent identity
- preserve shared cream/black/visor mechanical species language

### Visor expressions
- neutral
- blink
- happy `^ ^`
- focused
- curious / soft variant
- randomized blink timing
- citizen-specific expression bias

### Home / map
- replace letter circles with real head tokens
- periodic blink
- occasional safe idle expression
- validated travel/talk/work/charge cues
- keep motion compositor-friendly

### Citizens page
- full-body base asset
- lazy-loaded selected citizen
- validated equipment overlays
- physical maintenance/configuration remains state-driven

### Modular gear
- define rear / body / chest-waist / held / foreground layers
- shared canvas/anchor convention
- future attachment points
- do not infer attachment from concept art

### Canonical silhouette notes
- Aris: lean prospecting/extraction field identity
- Bex: compact fabricator
- Cato: heavy logistics/hauling chassis; do not slim
- Iri: especially slim/elegant construction precision chassis
- Noma: broad research/experimentation identity, not ecology-only
- Vale: generalist/cooperation/support, not dedicated medic

### Performance
- 64–96 px Home/map tokens
- lazy-load bust/full-body assets
- lazy-load equipment overlays
- prefer transform/opacity/sprite swaps
- reduced-motion support
- avoid expensive continuous blur/filter effects

### Future dependency
Before authoritative equipment overlays are complete, Assets may need Simulation to expose stable:
- equipped/attached equipment IDs
- owner/location
- optional body attachment slot semantics

Do not request or implement this dependency until v0.8 is formally activated by the coordinator.
