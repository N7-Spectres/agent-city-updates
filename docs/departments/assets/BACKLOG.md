# Assets & Interface — Backlog

## Waiting — v0.7 Maintenance Contract

- consume final Simulation equipment condition/wear/service fields
- consume structure condition/wear/service fields
- consume battery / power-storage health if exposed
- use Simulation-owned degraded / maintenance-needed / failed semantics
- add meaningful condition presentation to Citizens and Records
- add Home alerts only for meaningful degradation
- never render every wear tick as Recent Activity
- never infer visible damage from a percentage alone

Assets request is recorded in `docs/departments/simulation/INBOX.md`.

## Review / Validation — v0.7 Branch

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

Assets is waiting on World & Simulation's v0.7 maintenance/condition state contract.
