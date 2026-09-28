# Agent City UI Roadmap

_Last updated: 2026-09-28_

## Locked Direction

Agent City should gradually become a visual, living world rather than a dashboard.

The long-term goal is to see the **planet itself**, with each of the six citizens represented by a small avatar moving around the world, traveling between regions, interacting with structures, gathering materials, researching, building, repairing, and talking with visitors.

This should happen in **stable, meaningful milestones**. Avoid micro-updates when several related improvements can ship together. The simulation remains more important than flashy visuals.

Development is allowed to move faster than the original phase order when the citizens naturally begin using capabilities earlier than expected. The roadmap should describe the direction of travel, not artificially hold the civilization back.

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
**Right:** persistent Control Room rail

The right rail should keep important information above the fold rather than opening a large drawer below the world. It should support the visitor conversation plus easy access to History, Stores, Structures, Region details, and Updates. A future layout may keep Visit visible while switching a secondary right-side panel between those utility views.

Secondary information should be immediately reachable without repeated page scrolling.

Secondary views include:

- Region details
- Stores / resources
- Structures
- History
- Updates
- Later: research, citizen memories, relationships, diagnostics, and admin tools

The UI should feel like **visiting a place**, not operating a spreadsheet.

## Information Architecture Direction

The main Home view should prioritize only information needed for immediate observation and interaction.

### Home

Keep Home visually light:

- central map / world view
- citizen list for quick selection
- each citizen row shows only high-value live state: name, current activity, current location/travel state, carried cargo, and a compact energy/integrity signal
- persistent visitor chat for the selected citizen
- visitor's own current location shown as a small map-corner badge rather than a large dedicated status surface
- surface only meaningful exceptions/alerts when they require attention; do not fill Home with every available statistic

### Citizen detail page

A separate Citizens page/view may hold deeper per-citizen information such as:

- equipment
- cargo capacity and physical modifiers
- recent jobs/history
- remembered relationships / interaction history
- known discoveries / last-known information
- current and past projects
- longer-term activity summaries

Selecting a citizen on Home should remain fast and map-centric; detailed inspection belongs on the Citizen view.

### Locations page

A dedicated Locations page/view should provide deeper place summaries discovered by the civilization:

- survey/discovery state
- known deposits/resources
- structures and projects at the site
- citizens currently present
- route/distance information
- local coordinates where meaningful
- later environmental/terrain/atmospheric observations
- historical significance or accumulated activity where supported by real records

Home should show where places are. Locations should explain what is known about them.

### Secondary system views

Making, Stores, History, and Admin/Updates remain useful secondary surfaces. As information grows, prefer top-level pages/tabs or context-sensitive detail panes over stacking multiple nested scrolling boxes into the Home screen.

Guiding rule:

> **Home answers "What is happening right now?" Detail pages answer "What do we know about this thing?"**

## Visual Roadmap

### Shipped milestone — v0.3.0 World Presence

- live progress and ETA for active jobs
- traveling citizens move along their actual route based on simulation time
- pausing freezes movement because visuals derive from simulation time
- N7 has a physical visitor location and can travel between connected regions
- face-to-face visits require physical co-location
- citizen-to-citizen conversations are visible in History with expandable exchanges
- Stores shows settlement inventory beside material still being carried in the field

This is the first step from a status dashboard toward a visibly inhabited world.

### Shipped milestone — v0.4.0 Memory & Relationships / Control Room

- citizen conversations now create durable directional relationship history
- repeated encounters survive restart and enter bounded planning/dialogue context
- existing conversation history is backfilled idempotently into social memory
- conversation memory remains distinct from validated physical truth
- Visit stays visible while Region / Stores / Structures / History / Updates live in a persistent right-side Control Room
- the large bottom drawer is retired
- map spacing is derived from route distance for clearer geography
- route lengths are labeled
- citizen initials and compact clusters improve crowded locations
- travelers, visitors, labels, and location nodes use clearer separate presentation zones
- selected active travel routes receive stronger visual emphasis

This milestone deliberately does **not** invent friendship scores, radios, trust meters, or unverified social outcomes. Richer promises, claim reliability, cooperation, and help memories require stronger provenance and validated physical-event links.

### Current emergent-development note

The civilization is already showing behavior that was originally expected later in the roadmap.

During v0.3.0 testing:

- Noma traveled to Resin Grove while Cato was working there.
- Noma later autonomously initiated a face-to-face conversation with Cato.
- Bex initiated conversation with Aris before considering distant travel.
- Iri initiated conversation with Vale because Vale might have useful local information.
- Citizens are beginning to choose **who to talk to and why** as part of their own planning.

This is not yet a full relationship system. It is early social behavior emerging from local awareness, legal talk actions, recorded dialogue, and autonomous planning.

**Roadmap rule:** when later-stage behavior begins emerging naturally, build the missing persistence and consequences around the behavior that already exists instead of replacing it with a scripted system.

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

## Major Milestone Roadmap

### v0.4.0 — Memory & Relationships

The current communication layer is already producing proto-v0.4 behavior, so this milestone should deepen what the citizens are naturally doing rather than inventing a social system from scratch.

Planned direction:

- durable memories of meaningful citizen-to-citizen interactions
- familiarity and relationship history built from actual events
- remembered cooperation, disagreements, promises, help, and information exchange
- future decisions influenced by prior interactions
- last-known information remains separate from confirmed physical truth
- no arbitrary RPG-style relationship score exposed as the social reality
- Control Room UI redesign: move History / Stores / Structures / Region / Updates from the bottom drawer into the right-side interface

Goal: citizens should develop personal histories with one another, and those histories should begin affecting what they choose to do.

### Shipped milestone — v0.5.0 Making & Building

Resources are now physically transformable into equipment and structures through validated Simulation jobs/projects.

Shipped direction:

- fabrication jobs
- construction jobs
- material requirements
- tool / capability requirements
- multi-step projects with planned → reserved → underway → complete states where appropriate
- structures placed at real locations
- new construction appears in the world only after successful completion
- settlement layout begins visibly changing over time
- fabricated extraction/collection tools can improve gathering speed and/or usable yield through real physical capability, not abstract level bonuses
- fabricated carry equipment can increase cargo capacity; later equipment may trade capacity against energy use, terrain suitability, speed, or wear
- citizen experience may later contribute modestly to efficiency without becoming a visible RPG skill tree
- returning cargo to storage remains a citizen decision rather than a forced script
- add a simple energy-reserve rule so remote work/outbound travel cannot consume energy needed to reach a known charger plus a modest safety margin
- future field chargers/outposts can extend the safe working radius
- lay coordinate groundwork for future construction between original landmarks without requiring full free-roam globe exploration in this milestone
- UI polish: fixed-height internally scrolling visitor chat, anchored input, more compact/centered three-column layout, and useful citizen-conversation history showing what was discussed

Shipped result: the civilization can now begin altering its environment and capabilities through real fabrication/construction state. Equipment changes physical carrying/extraction behavior, projects persist through explicit lifecycle states, and the UI exposes those authoritative records without inventing outcomes.

### v0.6.0 — Research & Discovery

Research becomes experimental rather than a fixed technology tree.

Planned direction:

- hidden world-specific material properties
- experiments with simulation-determined outcomes
- successful and failed experiments become knowledge
- citizens can reproduce learned processes
- research can unlock new fabrication possibilities without exposing predetermined recipes
- communication technology is **not granted**; it may emerge only if citizen need, experimentation, materials, and fabrication capability make it possible

Goal: knowledge should be discovered through interaction with this particular world.

### v0.7.0 — Maintenance & Consequences

Mechanical life gains deeper physical consequences.

Planned direction:

- component wear
- lubrication needs
- battery health
- damaged tools and structures
- repairs and replacement parts
- preventative maintenance
- scarcity-driven reprioritization

Routine maintenance should remain mostly autonomous. Interesting failures and shortages should create decisions rather than repetitive chores.

Goal: survival and upkeep should matter without turning Agent City into a maintenance-clicking game.

### v0.8.0 — Living World

Expand the planet beyond the starter region.

Planned direction:

- additional terrain and routes
- environmental variation
- more native materials and vegetation
- distant work sites
- richer exploration
- reasons for new infrastructure away from Seed Site
- cultivation or agriculture may emerge if renewable biological materials become valuable

Goal: make the planet itself an evolving participant in the civilization.

### v0.9.0 — Civilization Continuity

Support long-running autonomous development across months and simulated years.

Planned direction:

- multi-step citizen projects and plans
- abandoned or revised plans
- skill growth through repeated practice
- emergent specialization without permanent classes
- teaching and knowledge transfer
- routines and personal work preferences
- longer resource strategies
- places that accumulate meaning through history
- social customs or traditions only when repeated events actually create them

Goal: the civilization's present should increasingly be explainable by its own accumulated history.

### v1.0 — Bonsai Civilization

v1.0 is reached when Agent City can be left running, revisited over a long period, and produce a settlement whose world state, relationships, knowledge, structures, habits, and decisions meaningfully descend from its own history.

The core loop should be:

**observe → decide → act → experience consequences → remember → communicate → learn → build → change the world → repeat**

The save/database is the continuity of the civilization. The local language model may later be upgraded without replacing the citizens or erasing their history.

## Autonomy Cutoff

Agent City should eventually reach a point where the development team stops supplying civilization-specific answers and instead maintains the world in which the citizens can discover their own answers.

Core rule:

> **Updates add possibility, not answers.**

A good update may add a missing physical domain such as atmosphere, terrain, fabrication, maintenance, chemistry, or weather.

A poor update would directly unlock a named solution because the citizens currently need it.

Examples:
- add atmospheric composition and gas-processing physics, not "Atmospheric Processor unlocked"
- add fabrication/material/tool rules, not "Backpack unlocked"
- add terrain/path/infrastructure rules, not "Road technology unlocked"
- add communication physics and components, not "Radio unlocked"

v1.0 is the intended handoff point where the sandbox is mature enough that future development is mostly QoL, visualization, performance, bug fixes, balance/realism corrections, and broad physical-world expansion.

The civilization itself should increasingly be authored by the citizens' accumulated decisions rather than by release notes.

## Development Pace Philosophy

The release numbers are milestones, not gates.

If citizens begin demonstrating behavior associated with a later milestone early, treat that as evidence about what systems should be strengthened next. Do not suppress emergent behavior merely to preserve the planned order.

Prefer:

- observing what the citizens actually do
- identifying where the simulation or memory model is too shallow
- adding persistence, constraints, and consequences
- bundling related work into substantial releases

Avoid:

- scripting interesting behavior that is already emerging on its own
- rushing every observation into a micro-release
- adding technologies or conveniences before the civilization has earned them
- changing physical reality merely because an LLM says something happened

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

**Stable milestones, emergent direction.**

Do not sacrifice simulation integrity, persistence, grounding, or citizen continuity for graphical complexity or release speed.

A simple visual representation of a real event is always better than a beautiful animation of something that did not actually happen.

When the citizens surprise us, treat the surprise as test data. Strengthen the systems underneath it rather than scripting the outcome.
