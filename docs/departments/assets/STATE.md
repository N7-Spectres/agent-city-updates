# Assets & Interface — State

_Last updated: 2026-09-28_
_Current release: v0.4.1_
_Current department branch: `assets/v0.5-making-ui`_
_Current review surface: draft PR #2_

## Mission

Make Agent City visually understandable and increasingly feel like a living place while never allowing the visual layer to invent physical reality.

## Shipped Baseline

v0.4.1 runtime lineage includes:

- left citizens / center world / right Visit + Control Room
- distance-aware map geometry and route labels
- citizen initial tokens and traveler presentation
- persistent visitor conversation
- Region / Stores / Structures / History / Updates in the right-side Control Room
- v0.4.1 blank-reply conversation hotfix

The v0.5 Assets branch is based from immutable runtime commit:
`4181cbb69809205ae575b3f576836e5ca72c8dce`.

## v0.5 Independent UI Work — Implemented

Branch: `assets/v0.5-making-ui`
Draft PR: **#2 — Assets: v0.5 compact interaction and conversation history**

### Compact Visit / layout

- Visit panel now has bounded height instead of growing with long conversations.
- Chat messages scroll internally.
- Visitor input and Talk action remain anchored below the scrolling conversation area.
- Previous-visit history has its own capped scroll region.
- Main three-column layout is rebalanced and centered, with more width reserved for the right-side interaction surfaces.
- Right rail heights are aligned more closely with the center world panel.
- Responsive behavior was adjusted for the fixed-height interaction design.

### Useful History

History is now the default Control Room view beneath Visit.

Recent Citizen Conversations now display:

- both participants
- location
- simulation time
- concise stored summary
- expandable exchange transcript when text is present

The UI now compares authoritative chronology rows with the conversation content included in the current state snapshot.

If chronology contains a `conversation` event but no matching exchange content is present in `state.citizen_conversations`, the UI renders a distinct chronology-only card saying that the exchange text is not included in the current snapshot. It does not invent missing dialogue.

## Verification Performed

Static branch verification:

- 45 HTML IDs
- 45 JavaScript `getElementById` references
- zero missing IDs
- zero duplicate IDs
- zero stale bottom-drawer hooks
- JavaScript parsed successfully
- branch is 3 commits ahead / 0 behind pinned v0.4.1 base
- changed runtime files are only:
  - `static/index.html`
  - `static/app.js`
  - `static/styles.css`

## Waiting Dependency — Making & Building

The remaining required v0.5 Assets work is the visual layer for real fabrication / construction / projects / tools / equipment.

Assets sent a schema request directly to:
`docs/departments/simulation/INBOX.md`

Needed authoritative Simulation fields include stable IDs, lifecycle/status, validated location/site, participants, physical progress, material reservation/consumption summaries, equipment ownership/location, and explicit physical modifiers the UI may safely display.

Assets will not infer project completion, tool effects, cargo capacity, coordinates, material use, or construction results.

## Next Action

When Simulation replies with the stable schema:

1. read Simulation OUTBOX / Assets INBOX,
2. inspect the exact runtime fields,
3. add restrained Making & Building views to PR #2 / `assets/v0.5-making-ui`,
4. keep all physical truth simulation-owned,
5. run static verification again and hand off for coordinator smoke testing.

No `update.json` or release metadata changes are part of this department branch.


## Session Handoff — Closed

Assets & Interface is paused in **WAITING** state.

Completed this session:
- created `assets/v0.5-making-ui` from pinned v0.4.1 runtime commit `4181cbb69809205ae575b3f576836e5ca72c8dce`
- opened draft PR #2
- implemented compact bounded Visit/chat layout
- anchored visitor input/actions
- rebalanced the three-column layout
- made History the default Control Room view
- improved citizen conversation history presentation
- added chronology-only conversation fallback without inventing missing dialogue
- statically verified the branch

External dependency:
- World & Simulation must hand off the final authoritative project/tool/equipment/structure schema before Assets can safely complete the Making & Building visual layer.

Resume procedure:
1. read `docs/departments/COORDINATION.md`
2. read `docs/departments/assets/INBOX.md`
3. read `docs/departments/simulation/OUTBOX.md`
4. if the schema is ready, continue on `assets/v0.5-making-ui` / draft PR #2
5. do not publish `update.json` or infer physical state in the frontend
