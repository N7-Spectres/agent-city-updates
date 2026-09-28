# Assets & Interface — Backlog

## Waiting — v0.5 Making & Building Schema

- consume Simulation's final project/tool/equipment/structure state contract when handed off
- add restrained project lifecycle visibility
- show fabricated tools/equipment only when authoritative records exist
- show physical tool/carry modifiers only from explicit Simulation fields
- show constructed structures/sites only after validated Simulation state says they exist
- use stable IDs so project/history/map surfaces can refer to the same physical objects

Schema request is in `docs/departments/simulation/INBOX.md`.

## Review / Validation — v0.5 Branch

- runtime-test draft PR #2 / `assets/v0.5-making-ui`
- verify long visitor conversations stay inside the bounded chat viewport
- verify Previous visits does not push input/actions off the Visit panel
- verify visitor input and Talk button remain usable at wide and narrow widths
- verify History opens by default and all other Control Room tabs still work
- verify chronology-only conversation cards against real saves with older/missing snapshot content
- verify updater, pause, visitor travel, citizen selection, and conversation persistence are unchanged
- responsive sanity pass at wide desktop, 1220-ish two-column layout, tablet, and narrow mobile

## Completed in v0.5 Independent UI Slice

- cap visitor chat height
- make chat log scroll internally
- anchor visitor input/actions
- rebalance and center main three-column layout
- use more right-side width for interaction/state surfaces
- make History the default Control Room companion beneath Visit
- show citizen-conversation participants, location, time, summary, and expandable transcript
- gracefully distinguish chronology-only conversation events from available exchange content

## Medium Priority

- arrival / departure visual pulse
- richer hover cards for citizens and locations
- clearer activity indicators on map tokens
- consider route direction / travel-progress affordances beyond selected-route highlight

## Later

- tiny robot tokens
- portrait/avatar chips
- planet/globe representation
- richer visible work-site activity
- accumulated settlement history in the environment
- animated miniature citizens

## Current Blocker / Next Session Gate

Assets is waiting on World & Simulation's stable v0.5 project/tool/equipment/structure schema for the remaining Making & Building UI layer.

Do not continue physical-state UI implementation until that contract is handed off through Simulation OUTBOX and/or Assets INBOX.
