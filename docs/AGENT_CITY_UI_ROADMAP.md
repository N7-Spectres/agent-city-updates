# Agent City UI Roadmap

_Last updated: 2026-09-27_

## Locked Direction

Agent City should gradually become a visual, living world rather than a dashboard.

The long-term goal is to see the **planet itself**, with each of the six citizens represented by a small avatar moving around the world, traveling between regions, interacting with structures, gathering materials, researching, building, repairing, and talking with visitors.

This should happen in **small, stable steps**. The simulation remains more important than flashy visuals.

## Core Experience

Agent City is a long-running "bonsai civilization."

The point is not to rush toward an end state. It should be enjoyable to revisit over months and see genuine progress, history, changed behavior, new infrastructure, discoveries, and relationships.

N7 and other human users are **visitors**, not gods, rulers, or omniscient operators. Visitors can talk to citizens, observe the settlement, ask questions, and make suggestions. Hidden admin controls remain outside the fiction.

The six original citizens remain:

- Aris — Extraction / prospecting aptitude
- Bex — Fabrication aptitude
- Cato — Logistics / resource planning aptitude
- Iri — Construction aptitude
- Noma — Research / experimentation aptitude
- Vale — Generalist / cooperation aptitude

Their aptitudes are starting strengths, not permanent careers.

## UI Layout Direction

The preferred main-screen structure is:

**Left:** six citizens  
**Center:** world / planet view  
**Right:** visitor conversation

Secondary information should be available through obvious controls near the upper-right rather than permanently filling the screen.

Secondary views include:

- Region details
- Stores / resources
- Structures
- History
- Updates
- Later: research, citizen memories, relationships, diagnostics, and admin tools

The UI should feel like **visiting a place**, not operating a spreadsheet.

## Visual Roadmap

### Phase 1 — Current Map Polish

Keep the current region map, but improve visual clarity.

Planned improvements:

- stronger selected-citizen highlight
- selected citizen's current location clearly highlighted
- route highlighting when a citizen is traveling
- hover information for citizen dots
- hover information for locations
- small citizen labels or initials
- clearer activity indicators
- subtle arrival / departure indicators

Goal: make the existing simulation easier to read without changing the simulation itself.

### Phase 2 — Citizen Avatar Tokens

Replace plain citizen dots with small visual tokens.

Possible progression:

1. colored circle + initial
2. tiny robot icon
3. small portrait/avatar chip
4. animated miniature citizen later

Selecting an avatar should also select that citizen for conversation.

Goal: begin giving each citizen a visible presence in the world.

### Phase 3 — Planet View

Evolve the flat region diagram into a visual representation of the planet.

Desired feel:

- visible planetary surface or globe-like map
- Seed Site and discovered regions shown geographically
- unexplored areas remain unknown
- structures appear where they physically exist
- resource locations appear only after discovery
- citizens visibly occupy specific locations

The world view should grow naturally as exploration expands.

Goal: make Agent City feel like an actual world rather than a node diagram.

### Phase 4 — Visible Movement

Citizens should visibly travel between locations.

Initial version can be simple animation:

- avatar moves along a route
- travel progress corresponds to real simulation job progress
- no visual teleporting when a journey takes time
- arrival animation or pulse
- optional route trail

Later versions may support walking animations.

Goal: what the player sees should correspond to what the simulation says is physically happening.

### Phase 5 — Visible Interaction

Add lightweight visual feedback for real actions.

Examples:

- mining / extraction indicator
- carrying-material indicator
- survey indicator
- charging indicator
- repair indicator
- research / experiment indicator
- construction indicator
- two-person cooperation indicator

These are visualizations of validated simulation actions. They do **not** create the actions themselves.

### Phase 6 — Living Settlement

As Agent City develops, the world view should show its history physically.

Examples:

- new workshops appear after construction
- roads or paths remain visible
- cultivated vegetation appears if agriculture emerges
- abandoned or repurposed buildings remain part of the landscape
- larger infrastructure appears over time
- original Seed Site remains visible unless the citizens physically dismantle it

Goal: a visitor should be able to look at the settlement and see years of accumulated history.

## Important Technical Rule

> **The AI may decide intent. The simulation decides reality.**

The visual layer must obey the same rule.

An animation or avatar must never show a physical event merely because an LLM mentioned it.

Visual state comes from validated simulation state only.

Examples:

- A citizen is only shown traveling if a real travel job exists.
- A building only appears after construction succeeds.
- A citizen only carries material that exists in their inventory.
- A deposit only appears after it is actually discovered.
- A research effect only appears after the simulation produces a real experiment result.

## Time Philosophy

Agent City should feel accelerated, not fast-forwarded because the observer is bored.

Current target:

**1 real hour = 4 simulated hours**

Approximate result:

- 6 real hours = 1 simulated day
- 1 real day = 4 simulated days
- 1 real week = 28 simulated days
- about 3 real months = 1 simulated year

Normal play should not encourage arbitrary 100x fast-forwarding.

Time stops when Agent City is closed unless a future background-running mode is explicitly enabled.

## Long-Term Goal

Eventually, opening Agent City should feel something like this:

- the planet is visible in the center
- six small citizen avatars are moving through it
- structures and resources exist where the simulation placed them
- citizens visibly work, travel, cooperate, and return home
- clicking a citizen opens conversation
- visitors can watch the settlement grow over months
- children or other visitors can recognize citizens they have spoken to before
- old structures and past decisions remain visible as part of the city's history

The visual world should become a window into the simulation, not a separate game layered on top of it.

## Development Rule

**Small steps first.**

Do not sacrifice simulation integrity, persistence, grounding, or citizen continuity for graphical complexity.

A simple visual representation of a real event is always better than a beautiful animation of something that did not actually happen.
