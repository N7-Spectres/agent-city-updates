# Assets & Interface — Decisions

## Visual Truth Rule

> **The visual layer may display simulation state. It may not create simulation state.**

Examples:

- show travel only if a real travel job exists
- move a citizen marker according to the real job start/end time
- show a building only after construction succeeds
- show cargo only if it exists in inventory
- show deposits only after validated discovery

## Map Philosophy

The map should become a readable physical world, not a decorative dashboard.

Stylization is allowed, but visual spacing should communicate meaningful geography whenever practical.

### v0.4 map rule

Before a true planet view exists, use the simulation's existing route distance as the source for relative map spacing where possible.

Presentation geometry may improve readability, but must not alter route distance or travel duration.

## Visitor Presentation

N7 and other visitors should have visible physical presence.

Visitor markers must not imply teleportation or remote face-to-face conversation.

## UI Philosophy

Important information should remain above the fold when practical.

Avoid requiring repeated page scrolling to switch between core views.

### v0.4 Control Room decision

Keep **Visit permanently visible** in the right rail.

Place Region / Stores / Structures / History / Updates in a separate persistent Control Room beneath it rather than making Visit itself a utility tab.

This preserves conversation continuity while allowing secondary state to be inspected without leaving the interaction surface.

## Citizen Cluster Decision

When several citizens occupy one location, use a compact labeled token cluster in a dedicated presentation zone around the location rather than stacking anonymous dots on the location marker.

Citizen initials are the current token stage; richer robot/avatar tokens may replace them later.

## Future Avatar Rule

Citizen avatars/tokens may become richer over time, but identity art must remain a presentation layer over validated citizen state.

## Ownership Boundary

Assets may request additional state fields from Simulation but should not alter action duration, resource outcomes, or physical legality simply to improve UI behavior.


## Review / Merge Rule

The v0.4 interface work remains presentation-only until runtime-tested.

Do not merge or publish the interface branch solely because static structural checks pass. Runtime behavior must confirm that visitor travel, citizen travel, selection, chat persistence, pause controls, updater controls, and responsive layout still work with real application state.


## v0.5 Conversation Viewport Rule

Long visitor conversations must scroll inside a bounded Visit panel.

The message log may grow historically, but the page layout should not become taller simply because a conversation is long. Visitor input/actions remain visible and usable outside the scrolling message viewport.

## v0.5 History Presentation Rule

History should distinguish:

- stored conversation content actually present in the current state snapshot, and
- authoritative chronology events whose exchange content is not present in that snapshot.

When only chronology is available, show the confirmed event metadata and explicitly say the exchange text is unavailable. Do not reconstruct or invent missing dialogue.

History is the default Control Room view for v0.5 because it is the most directly useful companion to persistent Visit interaction; Region remains available as a tab and physical region state remains centered in the world view.

## v0.5 Making & Building UI Rule

Fabrication, projects, equipment, tool modifiers, cargo-capacity effects, structures, sites, and construction progress may only be shown from authoritative Simulation state.

Assets must not derive physical bonuses or infer completion from names, LLM text, chronology prose, or frontend calculations when Simulation exposes a validated field instead.

Stable physical IDs should be preserved in UI data attributes / future links where useful so project, structure, tool, and history surfaces can refer to the same real object.


## Dependency Gate Rule

When a requested UI surface depends on new Simulation-owned physical state, Assets should complete independent presentation work first, then stop at a clear dependency boundary.

Do not mock, infer, or temporarily synthesize project/tool/structure state merely to finish the interface ahead of the authoritative schema.
