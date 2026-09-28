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

## Visitor Presentation

N7 and other visitors should have visible physical presence.

Visitor markers must not imply teleportation or remote face-to-face conversation.

## UI Philosophy

Important information should remain above the fold when practical.

Avoid requiring repeated page scrolling to switch between core views.

## Future Avatar Rule

Citizen avatars/tokens may become richer over time, but identity art must remain a presentation layer over validated citizen state.

## Ownership Boundary

Assets may request additional state fields from Simulation but should not alter action duration, resource outcomes, or physical legality simply to improve UI behavior.
