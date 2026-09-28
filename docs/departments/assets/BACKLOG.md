# Assets & Interface — Backlog

## Ready for Next Session — v0.7 Maintenance Contract

Simulation contract is ready on `simulation/v0.7-maintenance` @ `54f5d838f674d0b278a51382f3a880cc0738b417`.

Next implementation:
- Citizens: battery health/state, usable capacity, replacement/service due, joint wear, chassis service state
- Equipment: condition/state/operational/service due + **effective** cargo/extraction capability
- Structures: condition/state/operational/service due/efficiency/charging
- Records: bounded `maintenance_events[]` history
- Home: meaningful service/degradation alerts only
- Recent Activity: omit tiny wear churn and Communication `diagnostic` rows from normal citizen activity
- preserve Memory's rule that physical maintenance state is not automatically remembered social knowledge

## Review / Validation — v0.7 Branch

- run `tests/smoke_v070_assets.py` on integrated/runtime-capable branch

- runtime-test draft PR #7 / `assets/v0.7-home-avatars`
- verify three desktop Home columns stay approximately aligned in height
- verify citizen rail scrolls independently
- verify citizen search/filter with empty and matching results
- verify long chat scrolls internally and input/actions stay anchored
- verify Recent Activity shows at most five meaningful items
- verify real stored conversations use stored summaries
- verify failed talk attempts remain events only
- verify View all history opens Records → History
- verify avatar fallback is consistent across Home/directory/map/Citizens
- verify travel/charge/talk/work/idle animation follows active job state
- verify reduced-motion disables avatar animation
- verify responsive behavior below desktop

## Completed in v0.7 Independent Slice

- full-height desktop citizen rail
- internal citizen scrolling
- citizen search/filter
- full-height desktop Visit rail
- compact Recent Activity
- View all history action
- stored-conversation-only summary logic
- lightweight 2D avatar framework
- full-body fallback identity slot
- matching Home/directory/map tokens
- state-driven CSS animation
- reduced-motion support

## Later

- unique citizen full-body/token art
- authoritative equipment overlays on avatars
- richer map/work-site visuals
- richer location scene assets
- planet/globe representation

## Current Blocker

_None._ The Simulation maintenance contract is ready.

The remaining v0.7 Assets work is implementation on PR #7 in the next session.
