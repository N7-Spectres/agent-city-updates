# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.1 — Citizen art + map zoom/readability hotfix

Add the map usability polish to the existing v0.8.1 visual hotfix scope.

**Observed live issue:**
At region scale, Seed Site and nearby citizen/location nodes bunch together and become difficult to read. The current `.map-node` keeps a 132×56 click target, and `.map-node.focused` / hover paints that whole box, producing the visible rectangle over the center of the map.

**Required UI adjustment:**
- add visible zoom-in / zoom-out / reset-region controls
- clicking a location node should center/focus it; optionally move into a closer local presentation without changing physical state
- zoom state is presentation-only and must never mutate Simulation x/y
- keep the generous node hit target, but do not render the rectangular button surface
- focus/hover should accent the node dot and/or label instead
- make clustered citizens/visitor/location labels readable as the user zooms in
- preserve keyboard focus accessibility and reduced-motion behavior
- do not expose hidden deposits, seed data, or any extra spatial truth

This should ship alongside the actual six citizen runtime art assets in v0.8.1.


**CI noise rule for this hotfix:**
- work from `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- the release smoke now triggers only when `VERSION` changes, so ordinary integration pushes should not fire full release CI
- run focused Assets checks on the department branch, then coordinator performs one final full release run at version bump

**Next action:**
When v0.8.1 work begins, implement/test these map controls and node styling together with the citizen art integration.


_None._

The v0.8 Stage 2 coordinator request and final Simulation/Communication contracts have been fully consumed.

Assets Stage 2 is complete on:

- branch `assets/v0.8-exploration-ui-stage2`
- head `7f5294efaab738b44af116514a65d22478851ad0`
- PR #15 — ready for review
- branch validation `36460454385` — PASS

No Assets-owned dependency remains before coordinator integration.

Runtime-ready approved citizen art is still absent from the repository; this is a later asset-source task, not a Stage 2 integration blocker.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
