# Agent City — Project State

_Last updated: 2026-09-28_

## Current Release

**v0.6.0 — Research, Discovery & Knowledge UI**

Agent City is a local-first autonomous mechanical civilization simulation. Six equal mechanical citizens live at Seed Site and act independently through validated simulation actions.

Core law:

> **The AI may decide intent. The simulation decides reality.**

Information law:

> **A citizen only knows what information could actually have reached them.**

Human users such as N7 are **visitors**, not gods, rulers, or omniscient operators.

## Current Milestone

**v0.7.0 — Maintenance, Consequences & Home Polish is now the active development milestone.**

v0.6.0 remains the current shipped release, assembled, tested, and published from immutable runtime commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`.

v0.7.0 adds long-term mechanical wear/repair consequences, a first lightweight avatar/visual-identity stage, stronger Home layout scaling, recent-activity-at-a-glance, and autonomous talk reliability work.

Major shipped v0.6 changes:

- hidden physical world properties exist independently of citizen knowledge
- repeated surveys can reveal deposits, confirm existing findings, reveal location properties, or produce no new finding
- experiments consume real samples/energy/time and persist discovery, verified, or inconclusive outcomes
- validated discoveries receive stable IDs and initially belong only to the citizen who actually learned them
- learned verification processes can descend from real discoveries without becoming a fixed tech tree
- ordinary UI state hides undiscovered deposits, hidden property tables, and hidden reserve quantities
- Communication now records recipient-local provenance for validated observations/results and unverified face-to-face claims
- claims must be grounded in the durable transcript and retelling does not verify them
- Memory provides bounded Citizen and Location knowledge views without creating a global shared encyclopedia
- planner and visitor dialogue receive provenance-backed knowledge without remote omniscience
- Home is simplified around the map, citizen quick list, and visitor chat
- dedicated Citizens character-sheet view includes physical state, authoritative cargo capacity, equipment, projects, experiments, learned processes, and bounded knowledge
- dedicated Locations field-notebook view begins sparse and fills as real discoveries/observations accumulate
- dedicated Records view holds Making, Stores, History, Region, and Updates away from the Home surface
- visitor accessibility now distinguishes remote, traveling, busy, and talking states; talk counterpart resolution no longer produces self-references
- v0.6 release CI passed all v0.4/v0.5 regressions, v0.6 Simulation, Communication, Memory, and UI integration smoke tests, Python compilation, and JavaScript syntax checks



The richer provenance layer for individual claims, source reliability, promises, help, and validated cooperation remains future depth. Those features must wait for explicit Communication provenance and Simulation event references rather than being inferred from ordinary conversation.

## Current Emergent Behavior

The citizens are already showing early social behavior originally expected closer to v0.4.0:

- Noma traveled to Resin Grove while Cato was working there
- Noma later initiated conversation with Cato
- Bex initiated conversation with Aris before considering distant travel
- Iri sought Vale because Vale might have useful local information

These are not scripted relationship events. They emerged from local awareness, legal talk actions, and autonomous planning.

## Departments

### Assets & Interface
Path: `docs/departments/assets/`

Owns:
- UI layout
- map readability
- citizen markers / avatars
- animation and visual state
- Control Room layout
- visual assets

### Memory & Social
Path: `docs/departments/memory/`

Owns:
- citizen memory
- relationship history
- visitor memory
- bounded context / retrieval / summarization
- social continuity

### Communication & Perception
Path: `docs/departments/communication/`

Owns:
- face-to-face conversation
- who can perceive whom
- information transfer
- last-known knowledge
- speech/hearing/observation
- future communication systems if citizens actually invent them

### World & Simulation
Path: `docs/departments/simulation/`

Owns:
- jobs and action validation
- movement
- resources
- energy/integrity
- extraction
- fabrication/construction later
- research outcomes later
- world geography and physical truth

## Coordination System

Departments communicate asynchronously through repository files:

- `docs/departments/COORDINATION.md` — shared work board
- each department's `INBOX.md` — incoming requests/dependencies
- each department's `OUTBOX.md` — completed handoffs/results

The main coordinator may route messages between these files.

A department chat should begin by reading its inbox and may usually be resumed with the instruction:

> **Check your inbox and continue.**

The only manual step still required is opening/activating the relevant ChatGPT department conversation; chats cannot directly wake or message one another.

## Handoff Rule

Departments own systems, not reality.

If one department needs another system changed, record the dependency in that department's `BACKLOG.md` or `STATE.md` instead of silently changing another department's rules.

Cross-department changes should preserve these two laws:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

## Development Pace

Use **stable, meaningful milestones**, not a stream of micro-updates.

If citizens begin demonstrating later-stage behavior early, strengthen the systems underneath that behavior instead of suppressing it to preserve the roadmap order.

See also:

- `docs/AGENT_CITY_UI_ROADMAP.md`
- `docs/departments/README.md`


## Civilization Autonomy Cutoff

Agent City should eventually reach a deliberate handoff point where development stops providing civilization-specific solutions and instead provides only the underlying world capabilities needed for citizens to invent their own responses.

Core rule:

> **Updates add possibility, not answers.**

Before v1.0, development may add missing substrate such as:
- fabrication and construction
- research and experimentation
- persistent material properties
- energy and maintenance rules
- geography, terrain, atmosphere, weather, and ecology
- tools/equipment as physical objects
- memory, perception, communication provenance, and planning support
- project and settlement-state mechanics

Development should not grant specific downstream solutions merely because a citizen problem appears. Examples that should normally emerge from citizen need, knowledge, materials, and fabrication rather than be directly unlocked by an update include:
- radios or other communication devices
- backpacks, carts, or hauling systems
- roads
- atmospheric processors
- specialized industrial tools
- settlement expansions or outposts

Around v1.0, the intended philosophical transition is:

- before v1.0: build the sandbox and its physical laws
- after v1.0: primarily maintain, visualize, optimize, fix, and deepen the sandbox while the citizens build the civilization

Post-v1.0 updates may still add new physical domains or richer simulation, but should avoid answering a problem the citizens are currently facing for them.

If citizens struggle with a logistical, environmental, or technical problem, prefer allowing them to adapt through existing systems rather than shipping a handcrafted solution.


## v0.6 Active Scope

### Research / Discovery

- hidden world-specific material properties
- experiment actions with simulation-determined outcomes
- successful and failed experiments persist as knowledge
- learned processes may become reproducible only after discovery
- no visible predetermined technology tree
- communication technology remains something citizens may eventually invent, not a granted unlock

### Known Truth vs World Truth

Ordinary citizen/visitor-facing views must not expose raw hidden Simulation state.

A location may begin with almost no information beyond what has actually been mapped or observed.

Knowledge sheets fill in only through valid:
- direct observation
- survey
- measurement
- experiment
- physical record
- conversation / information transfer

Unknown resources or properties remain absent rather than appearing as greyed-out secrets.

### UI / Navigation

Home should answer:
> **What is happening right now?**

Home prioritizes:
- map
- citizen quick list
- selected-citizen chat
- compact visitor-location badge
- meaningful live alerts only

Citizens view should answer:
> **What do we know about this citizen?**

Locations view should answer:
> **What do we know about this place?**

Locations should feel like a field notebook that gradually fills in as the civilization learns.

### Character / Location Visuals

Citizen detail pages should reserve a full-body visual identity area and show current physical equipment/configuration when supported by validated state.

Location detail pages should include a simple scene/visual representation now, with room for richer graphics later.

### Known v0.5 bug carried into v0.6

Visitor availability messaging must correctly resolve the other participant in a talk job and distinguish:
- remote location
- visitor traveling
- citizen traveling
- citizen currently busy/talking

Do not display a self-reference such as "Vale is currently speaking with Vale."


## Conversation / Coordinator Continuity

The GitHub documentation is the durable handoff layer for future Agent City coordinator chats.

A new coordinator conversation should begin by reading:
1. `docs/AGENT_CITY_PROJECT_STATE.md`
2. `docs/AGENT_CITY_UI_ROADMAP.md`
3. `docs/departments/COORDINATION.md`
4. the relevant department `STATE.md` / `DECISIONS.md` / `BACKLOG.md` files when planning new work

Important boundary:
- GitHub notes preserve project architecture, decisions, roadmap, release lineage, department contracts, and handoffs.
- The local Agent City SQLite save remains authoritative for the civilization's changing physical state. Do not copy transient citizen positions/cargo/activity into GitHub as if they were current forever.

Recent coordinator decisions already captured in the repository include:
- long-term world generation may use a persistent hierarchical random seed so planets/star systems are deterministic hidden reality rather than handcrafted or rerolled on discovery
- if citizens eventually invent spaceflight, additional seeded planets/moons/stars can be revealed through the same system
- stellar-scale engineering, including a possible Dyson-style swarm, is allowed only as an emergent citizen-built outcome rather than a predetermined unlock
- v0.8 should begin a local asynchronous asset-generation foundation: validated Simulation objects/projects can queue visual work for a local worker/procedural 3D pipeline; visual generation never blocks or defines physical reality
- v0.6.0 Research, Discovery & Knowledge UI shipped
- Home should answer "What is happening right now?"
- Citizens and Locations should hold deeper detail
- Location notebooks reveal only knowledge actually discovered/communicated
- future citizen creation/population growth is possible in principle but must emerge from real research/fabrication/energy/identity systems
- full-body citizen visual/character-sheet direction is desired
- visitor location should remain compact on the map
- future citizen-to-visitor requests/alerts should obey real communication mechanisms
- weather/atmosphere are future world substrate, not arbitrary punishment
- updates should add possibility, not answers

If a future chat needs to resume coordinator work, these repository files should be treated as the persistent source of truth rather than relying on old chat transcript memory alone.


## v0.7 Active Scope

### Maintenance / Consequences
- gradual component/equipment/structure wear
- lubrication and repair needs where physically appropriate
- battery health as a long-term condition separate from current charge
- damaged tools/structures can lose capability or become unavailable
- repair/replacement/preventative maintenance are real simulation actions
- maintenance should create occasional decisions, not constant busywork
- no arbitrary RPG debuffs; consequences come from physical condition/state

### Home Polish
- citizen rail roughly matches map height and scrolls internally
- future-ready citizen search/filter
- Visit/chat roughly matches map height on desktop
- chat remains internally scrollable with anchored input
- compact Home Recent Activity, around 5 meaningful events/conversations
- Records remains the full archive

### Avatar First Stage
- full-body 2D/static citizen identity area on Citizens
- smaller matching map/home token
- simple state-driven browser animation only
- no Mixamo or 3D rigging required in v0.7
- visual equipment changes only when backed by validated physical equipment

### Talk Reliability
- investigate repeated valid talk attempts ending without durable exchanges
- preserve the hard invariant that failed generation never creates fake dialogue
- improve reliability and add internal diagnostics for failure causes
