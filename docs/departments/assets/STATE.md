# Assets & Interface — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_
_Current department branch: `assets-v0.4-control-room`_

## Mission

Make Agent City visually understandable and increasingly feel like a living place while never allowing the visual layer to invent physical reality.

## Current Implementation

Shipped v0.3.0:

- left: six citizen cards
- center: known-region map
- right: visitor conversation
- bottom drawer: Region / Stores / Structures / History / Updates
- live job progress bars and ETA
- citizen movement along map routes
- N7 visitor marker and visitor travel progress
- field cargo vs settlement Stores comparison
- citizen conversation display in History
- expandable citizen conversation exchanges

## v0.4 Interface Pass — Review Ready

Implemented on `assets-v0.4-control-room`, based from `release-v0.3.0`.

### Control Room

- Visit remains permanently visible in the right rail.
- Region / Stores / Structures / History / Updates now live in a second persistent right-side Control Room.
- The giant bottom detail drawer is removed from the branch.
- Existing visitor/chat DOM IDs and API behavior are preserved.

### Map readability

- location layout now derives radial spacing from existing `state.routes[].distance_km`
- route lines are rendered from the same computed geometry
- route distance labels are shown on the map
- the selected citizen's active travel route is highlighted
- citizen dots are upgraded to initial-bearing tokens
- citizens at the same location occupy a dedicated compact cluster zone
- traveler tokens use route-relative lane offsets when multiple travelers share a route
- visitor markers use a separate presentation offset when stationary
- location labels have explicit above/below placement rather than sharing the marker center
- focused and selected-citizen locations receive stronger visual treatment

No simulation durations, travel rules, resource state, discoveries, or action legality were changed.

## Verification Performed

Static structural verification on the department branch:

- 45 HTML IDs
- 45 JavaScript `getElementById` references
- zero missing referenced IDs
- zero duplicate IDs
- zero stale `detail-drawer`, `close-drawer`, `openDrawer`, `closeDrawer`, or `LOCATION_POSITIONS` references
- JavaScript parsed successfully during patch generation

Still required before incorporation:

- browser/runtime visual test with a running Agent City instance
- responsive sanity check at desktop, tablet, and narrow widths
- verify route-distance geometry against real `/api/state` values
- verify visitor travel, citizen travel, chat persistence, updater controls, and pause controls still behave normally

## Files Owned / Changed

- `static/index.html`
- `static/app.js`
- `static/styles.css`
- visual-only roadmap / department documentation

Changes to simulation timing, action legality, resource outcomes, or physical outcomes belong to World & Simulation.
