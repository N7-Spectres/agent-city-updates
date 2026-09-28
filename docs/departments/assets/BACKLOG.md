# Assets & Interface — Backlog

## Review / Integration — v0.5

Assets implementation is complete. Remaining work is coordinator/runtime validation.

- integrate `assets/v0.5-making-ui` with `simulation/v0.5-making-building`
- runtime-test draft PR #2 against the integrated v0.5 backend
- verify long visitor conversations stay inside the bounded chat viewport
- verify Previous Visits never displaces visitor input/actions
- verify History opens by default and other Control Room tabs still work
- verify canonical conversation IDs/source-job IDs display correctly on new talks
- verify failed talk attempts appear only in chronology, with no fabricated transcript
- verify Making tab with real:
  - planned projects
  - reserved projects/materials
  - underway projects
  - completed projects/resulting structures
  - fabricated equipment
  - cargo modifiers
  - extraction-speed modifiers
  - charging structures
- verify local coordinates are presented only as local site data
- verify updater, pause, visitor travel, citizen selection, conversation persistence, and responsive behavior remain intact

## Completed in v0.5 Assets

- fixed-height chat
- internal chat scrolling
- anchored input/actions
- centered/rebalanced layout
- useful History companion view
- canonical conversation-source display
- chronology-only legacy fallback
- Making tab
- authoritative project lifecycle display
- project material reservation display
- equipment display
- explicit modifier display
- extended structure display

## v0.6 Visit Status Polish

- render the backend's real visit availability reason instead of the generic "Not at the same location" label for every inaccessible state
- distinguish: remote location, visitor traveling, citizen traveling, citizen already talking/busy
- when citizen is busy talking, display the actual counterpart supplied by Communication/Simulation

## Medium Priority

- arrival / departure visual pulse
- richer hover cards for citizens and locations
- clearer activity indicators on map tokens
- consider route direction / travel-progress affordances beyond selected-route highlight

## Later

- tiny robot tokens
- portrait/avatar chips
- planet/globe representation
- richer visible work-site activity on the world map
- accumulated settlement history in the environment
- animated miniature citizens

## Current Blockers

_None within Assets._ The department branch is ready for coordinator integration and runtime smoke testing.


## Next Owner

**Coordinator / Integration**

There is no remaining Assets implementation task before v0.5 assembly. Any new Assets work should come from coordinator smoke-test findings or a new inbox request.
