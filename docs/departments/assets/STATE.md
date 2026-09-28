# Assets & Interface — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_

## Mission

Make Agent City visually understandable and increasingly feel like a living place while never allowing the visual layer to invent physical reality.

## Current Implementation

Main layout:

- left: six citizen cards
- center: known-region map
- right: visitor conversation
- bottom drawer: Region / Stores / Structures / History / Updates

v0.3.0 added:

- live job progress bars
- simulated-minute progress
- job ETA
- citizen movement along map routes
- N7 visitor marker
- visitor travel progress
- field cargo vs settlement Stores comparison
- citizen conversation display in History
- expandable citizen conversation exchanges

## Current Visual Problems

### Map readability

The map is becoming crowded as more state appears.

Observed issues:

- location circles, labels, citizen dots, and the visitor badge overlap
- route lengths do not communicate distance strongly enough
- citizen clusters are difficult to parse at a glance
- traveler markers can compete visually with location markers
- current star-shaped layout is functional but increasingly cramped

### Bottom drawer

History / Stores / Structures / Region / Updates open below the main layout.

This requires excessive scrolling on taller pages.

## Planned Direction

### Control Room layout

Move the bottom drawer into a persistent right-side utility area.

Desired structure:

- left: citizens
- center: world
- right: Visit + utility views

Potential utility tabs:

- Visit
- History
- Stores
- Structures
- Region
- Updates

A future version may keep Visit visible while switching a secondary right-side panel.

### Map readability pass

- increase spacing between region nodes
- make route length more visually proportional to travel time/distance
- give location labels dedicated positions
- give citizen clusters dedicated positions around/near locations
- keep traveling citizens clearly on route lines
- keep visitor marker visually separate
- improve symbol hierarchy and legend
- prepare for citizen initials/avatar tokens

## Files Commonly Owned

- `static/index.html`
- `static/app.js`
- `static/styles.css`
- visual-only roadmap sections

Changes to simulation timing, action legality, or physical outcomes belong to World & Simulation.
