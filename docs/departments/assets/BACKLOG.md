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
