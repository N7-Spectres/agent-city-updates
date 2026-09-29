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

### Home panel sizing / glanceable history

The Home screen should use the full map-height column space more intentionally.

**Citizen rail**
- extend the citizen panel to approximately the same visual height as the world/map panel
- keep the citizen rows inside an internally scrollable list
- reserve a stable header area above the list
- add a name search/filter control when population growth makes scrolling less convenient
- this is future-proofing for more than six citizens; Home should not become vertically longer just because population grows

**Visit / chat rail**
- extend the Visit panel to approximately match the map/world panel height on desktop
- keep the conversation log internally scrollable
- keep input/actions anchored
- do not let long conversations push the page downward
- responsive layouts may relax the hard height on smaller screens

**Recent activity on Home**
- restore a compact History summary to Home as an at-a-glance surface
- show only a small recent window, target: latest ~5 meaningful items
- include both citizen conversations and significant settlement events in chronological order
- conversation entries should show a concise summary when a real stored exchange exists
- failed talk attempts may appear as events but must not masquerade as successful conversations
- provide a clear "View all history" action that opens Records → History

Records remains the deep archive. Home only answers "What just happened?"

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

A dedicated Locations page/view should provide deeper place summaries discovered by the civilization.

### Knowledge-bound Locations view

The Locations page must never become an omniscient strategy map.

It should show only what citizens have actually observed, measured, surveyed, tested, built, or communicated through a valid information path.

New/poorly known locations may begin mostly blank.

As knowledge accumulates, the location sheet fills in over time:
- survey/discovery state
- known deposits/resources
- structures and projects at the site
- citizens currently present when directly/authoritatively known to the visitor UI
- route/distance information already mapped
- local coordinates where meaningful
- environmental/terrain/atmospheric observations only after measurement
- historical significance or accumulated activity from real records

Example:
- Resin Grove initially: description + mapped route, most fields unknown
- after survey: Plant Fiber appears under Known Resources
- after later testing: additional material properties or environmental notes may appear
- unknown resources remain hidden, not shown as locked/greyed "secrets"

The visual should feel like a field notebook/data sheet gradually being completed by the civilization, not a god-view database.

Home should show where places are. Locations should explain only what is actually known about them.

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

As exploration grows, the map should support citizen-named landmarks. A physical feature may first appear as an unnamed known feature or coordinate; once citizens adopt a name through real use/discussion, that name becomes part of the persistent map history. Aliases/renames may exist when socially justified.

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

### Shipped milestone — v0.6.0 Research, Discovery & Knowledge UI

v0.6.0 shipped as a large combined research/discovery and information-architecture milestone.

Shipped direction:

#### Research / discovery substrate
- hidden world-specific material properties
- experiment actions with simulation-determined outcomes
- successful and failed experiments become persistent knowledge
- citizens can reproduce learned processes
- research can unlock new fabrication possibilities without exposing a predetermined technology tree
- communication technology is **not granted**; it may emerge only if citizen need, experimentation, materials, and fabrication capability make it possible
- knowledge must remain local/provenanced: a citizen or UI surface should not know a discovery until it was observed, measured, or communicated through a real mechanism

#### Knowledge model / data sheets
- add a clear distinction between **world truth** and **known truth**
- location records exposed to ordinary UI must be knowledge-filtered rather than raw hidden simulation state
- locations begin sparse and fill in as surveys, experiments, measurements, and conversations add evidence
- unknown resources/properties remain absent rather than displayed as hidden slots
- retain source/provenance and discovery time where useful
- support later environmental, atmospheric, terrain, and material-property observations without inventing them early

#### UI / navigation
- simplify Home around: map, citizen quick list, selected-citizen chat, and only high-value live status
- move deeper citizen information into a dedicated **Citizens** view / character sheet
- add a dedicated **Locations** view / field notebook
- Locations should include a simple visual/scene representation of the place plus its gradually filled knowledge sheet
- keep Making, Stores, History, and Updates as secondary/system views rather than crowding Home
- visitor current location may be reduced to a compact map badge
- fix occupied-citizen visit messaging: when a citizen is already in a talk job, show the actual counterpart rather than a self-reference
- do not label every unavailable visit as "Not at the same location"; distinguish remote, traveling, busy/talking, and other physical reasons accurately
- support meaningful alerts/requests without turning Home into an admin dashboard

#### Citizen character sheets
- full-body visual identity slot
- appearance / current physical configuration
- currently equipped physical gear
- activity/location/travel state
- cargo and capacity
- energy/integrity
- recent work and projects
- known discoveries / relevant memory
- later specialization/skills when those systems become real

Shipped result: Agent City now separates hidden world truth from citizen knowledge, preserves provenance and uncertainty, and presents Home/Citizens/Locations/Records as distinct information surfaces. Location and citizen sheets can grow over time without exposing undiscovered world data.

### Shipped milestone — v0.7.0 Maintenance, Consequences & Home Polish

Mechanical life gains deeper physical consequences while the Home screen becomes easier to live with over long sessions.

Shipped direction:

#### Maintenance / consequences
- component wear
- lubrication needs
- battery health / long-term battery condition
- damaged tools and structures
- repair jobs and replacement parts
- preventative maintenance
- scarcity-driven reprioritization
- maintenance should affect real capability, not arbitrary stat penalties
- wear and damage should accumulate gradually enough to create decisions without constant emergency spam
- tools/equipment may lose efficiency as condition drops
- structures may become less reliable or unavailable if neglected
- citizens should normally notice and respond to maintenance needs autonomously

#### Avatar / visual identity first stage
- begin the avatar era with lightweight 2D/static identity assets, not full 3D rigs
- Citizens page gets a full-body visual identity slot for each citizen
- Home/map may use a smaller crop/token derived from the same identity
- simple state-driven browser animation is allowed: idle pulse/bob, travel motion, charging glow, talking/working indicator
- animation must derive from validated simulation state
- no Mixamo/3D dependency is required for this milestone
- future 3D rigging/walk cycles may come later if the project grows into animated miniature citizens
- physically equipped gear should eventually alter the citizen visual only when validated equipment exists
- if no authoritative art/configuration exists yet, use clearly provisional visuals rather than inventing unsupported physical equipment

#### Home / interaction polish
- full-height scrollable citizen rail aligned roughly with the map height
- future-ready citizen name search/filter
- full-height Visit/chat rail aligned roughly with the map height
- internal chat scrolling with anchored input/actions
- compact Home Recent Activity feed, target ~5 latest meaningful events/conversations
- clear path from Home Recent Activity to Records → History
- keep Records as the detailed archive
- improve autonomous citizen talk reliability so valid same-location talks normally produce a durable exchange
- retain the integrity rule that failed generation never creates fake dialogue

Routine maintenance should remain mostly autonomous. Interesting failures and shortages should create decisions rather than repetitive chores.

Goal: survival and upkeep should matter, and Home should remain readable as the civilization and its history grow.

Shipped result: v0.7.0 adds real mechanical wear/service consequences, bounded maintenance memory, more reliable durable citizen conversations, scalable Home rails/search/Recent Activity, and the first lightweight avatar framework. The assembled release passed the complete v0.4-v0.7 smoke chain.

### Merged into v0.8.0 — Glanceable Job Progress & Interaction Polish

v0.7.1 is not planned as a separate release. Its UI/chat/RP-grounding work is folded into v0.8.0 so the interaction layer ships together with the continuous seeded-world foundation it depends on.

Small UI follow-up to v0.7.0.

Scope:
- restore the compact active-job progress bar to Home citizen cards
- show authoritative elapsed / total simulation minutes and a concise remaining/ETA indicator
- apply to active travel, extraction, survey, charging, fabrication/construction, experiment, and maintenance jobs where start/end times exist
- idle rows remain compact
- progress derives only from Simulation job timing
- preserve v0.7 full-height scrollable citizen rail, search/filter, avatars, and responsive layout
- no simulation-rule changes
- **Visitor roleplay grounding:** visitors may describe their own gestures, questions, observations, and suggestions, but visitor chat must not silently create authoritative objects, deposits, transfers, terrain facts, history, or completed physical actions
- citizen replies should treat visitor-provided physical details as observations/claims to inspect, not automatically confirmed truth
- encourage natural phrasing such as "that looks promising," "we could inspect it," or "I would need to verify that" when the world state is not yet validated
- preserve playful face-to-face RP without letting the text box become a world editor
- citizen comparisons must stay inside their actual known properties; do not invent microstructure, material value, terrain names, landmarks, or site history as factual support
- uncertainty language is encouraged when evidence is incomplete, but uncertainty does not license invented details
- if a citizen has a real equipped/available analysis tool, dialogue may propose using it; stronger conclusions require a real validated scan/test result
- concept-art scanners/tools do not count as runtime equipment
- visitor chat keyboard behavior: **Enter sends**, while **Shift+Enter inserts a new line**
- preserve the visible Talk/send button for mouse/touch users
- do not submit on IME/composition Enter events

This restores a useful v0.3-v0.5 at-a-glance affordance that was lost during the v0.6 Home simplification.

### Shipped milestone — v0.8.0 Living World

Shipped release commit: `a870982ba947fcc5af08ca190de396ae4308b645`  
Final CI: `36462126434` — PASS

Expand the planet beyond the starter region.

Planned direction:
- establish a persistent planet seed and seeded coordinate-based hidden world
- move toward meter-scale local positions inside the existing regional coordinate framework
- scans/surveys query deterministic hidden truth at the actual coordinate rather than rolling a new result
- nearby terrain/resource results should vary coherently with geology; one meter of movement does not automatically mean a new deposit
- discovered deposits gain stable identity and spatial extent so the same vein can be encountered from multiple nearby points

- additional terrain and routes
- environmental variation
- more native materials and vegetation
- distant work sites
- richer exploration
- reasons for new infrastructure away from Seed Site
- cultivation or agriculture may emerge if renewable biological materials become valuable

Goal: make the planet itself an evolving participant in the civilization.


### Shipped milestone — v0.8.1 Citizen Visual Assets + Map Readability

Shipped v0.8.1 commit: `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`  
Final CI: `36468997929` — PASS

Visual-only follow-up:
- export/import approved runtime-ready citizen art
- populate full-body, bust/head-token, and map-token slots where assets exist
- keep optional equipment as separate removable layers
- preserve existing fallback silhouettes for any missing expression/frame
- concept art remains identity reference; depicted gear is not physical inventory
- no Simulation behavior changes

### Shipped milestone — v0.8.5 Daily Rhythm & Recharge

Shipped v0.8.5 commit: `5b2395d7e7643a3d7ac9a82ac68090fc97b5f0b7`  
Final CI: `36498819565` — PASS

Daily autonomy and world-presentation follow-up:
- citizens retain the full physical action set, while autonomous planning filters choices by simulated time-of-day
- 06:00–20:00 is the normal active cycle
- 20:00–22:00 is wind-down
- 22:00–06:00 favors recharge, safe return, maintenance, conversation, unloading, and low activity
- critically low energy overrides personality/productivity in autonomous choice
- active physical jobs are never cancelled merely because night begins
- overnight charging can continue through multiple real charging jobs until usable battery capacity is full
- degraded battery health remains the real capacity ceiling
- map/world presentation reflects dawn, day, dusk, and night using the existing authoritative simulation clock
- visual time-of-day never changes or invents Simulation state

This establishes a daily settlement rhythm without turning the citizens into scripted shift workers.

### Shipped milestone — v0.8.6 Stranded Citizen Recovery

Shipped v0.8.6 commit: `a72f96b763671f01c5a8aa0ba41d87f7eb6b9a09`  
Final CI: `36591711494` — PASS

Energy-safety correction:
- reaching an operational charger is a valid safety endpoint
- charger-bound travel does not require an additional reserve after arrival
- actual travel energy cost still must be available
- non-charger destinations retain the normal return reserve
- fixes low-energy deadlocks without teleporting citizens or rewriting legitimate world history

Confirmed bug recovery should prefer repairing the governing rule so the existing save can recover naturally. Direct admin state repair remains a last resort for impossible states created by software defects.

### Shipped milestone — v0.8.7 Route Travel Visualization

Shipped v0.8.7 commit: `be617e6e870ec3f1914d76cdb85107a6efc294d7`  
Final CI: `36595479188` — PASS

Presentation-only movement readability:
- known-route travelers are positioned along the route according to authoritative job progress
- map placement and left-card progress now describe the same travel fraction
- compact travel percentage appears with the moving token
- remaining route distance is available in token detail/tooltip text
- Simulation still owns actual arrival and persisted position; presentation interpolation cannot create movement

### v0.9.0 — Civilization Continuity

Architecture lock:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

Continuity law:

> **Persistent behavior must have a traceable history.**

Support long-running autonomous development across months and simulated years without converting citizens into authored classes or scripted character arcs.

### Stage 1 — Causal Memory + Persistent Plans

- Memory becomes the bounded continuity spine used by planning.
- retain provenance-linked personal, social, place, success/failure, and unfinished-plan experiences.
- distinguish durable archive from active recall.
- retrieve only relevant, citizen-scoped continuity under context limits.
- add persistent citizen-owned plans with reasons, source history, current state, next step/unresolved question, revision, abandonment, and completion.
- plans remain intentions, not command queues; every physical step is still Simulation-validated.
- unrelated actions/time must not erase a meaningful unfinished plan.

### Stage 2 — Practice, Competence, Teaching, Recognition

- real completed practice may accumulate experience.
- competence differences may affect physical outcomes only through bounded Simulation-owned effects.
- no permanent job/class labels.
- citizens may form evidence-backed self-assessments such as "I've gotten better at this."
- other citizens may notice experience differences only through information that actually reached them.
- social recognition remains perspective, not a universal reputation score.
- teaching requires an explicit real transfer mechanism; conversation alone cannot create skill.

### Stage 3 — Habits, Place Meaning, Social Customs

- repeated choices may become routines/preferences only after an explicit evidence threshold.
- places may accumulate citizen-specific remembered meaning.
- recurring cooperation may become an expected pattern when its real history supports it.
- customs/traditions require repeated behavior, multiple participants/observers, retained social memory, communication about the pattern, and continued voluntary repetition.
- no authored culture templates.

Goal:
the civilization's present should increasingly be explainable by its own accumulated history.

Success means questions such as "Why does Iri avoid running her battery so low now?" or "Why does Bex keep choosing this work?" can be answered from real source-linked history rather than hidden identity labels.

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


### v0.8 Stage 2 — Exploration Lifecycle

Stage 2 integration result: **PASS** on `release-v0.8.0@022f7655e9e958e3c35866d90679166a5b1c21e6` (Actions `36461596122`). The physical exploration, shared-action, bounded-memory, and continuous-map layers now coexist in one tested runtime.

Stage 1 established the hidden seeded world and safe spatial contracts. Stage 2 makes that substrate physically usable.

Direction:
- real local meter-space movement for citizens
- visitor-linked shared walk/inspection activities through explicit acceptance, never chat auto-execution
- authoritative movement start/target/progress fields for visual interpolation
- validated local observations at real coordinates
- same seeded deposit retains stable identity across nearby encounters
- bounded spatial memory enters planning/dialogue only for citizens who legitimately know it
- continuous local map uses only safe positions/observations
- proposed vs active shared activity is visually explicit
- preserve named landmarks/routes as anchors during transition
- no scanner is granted merely because concept art depicts one

Stage 2 uses the integrated Stage 1 base:
`release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`.

### v0.8 Asset Pipeline Foundations

Begin laying the local visual-generation substrate for the later 3D world without making asset generation authoritative over simulation.

Direction:
- add a persistent local asset-job queue keyed to validated physical objects/projects
- store a structured visual/geometry specification derived only from authoritative Simulation state
- add a local Asset Worker process that can pick up queued jobs while Agent City runs
- start with deterministic procedural/modular geometry rather than requiring AI-generated meshes
- allow Blender/headless or another local generator to emit reusable runtime assets such as GLB when appropriate
- asset generation runs asynchronously and may use real fabrication/construction time as a natural processing window
- simulation completion must never wait on a visual asset; use a safe fallback representation until the asset is ready
- failed/slow asset generation cannot change physical reality
- future local LLM assistance may translate validated functional designs into constrained visual recipes, but may not invent capability/materials/components
- preserve provenance from physical object/project ID → visual specification → generated asset
- this is foundation work, not yet full autonomous 3D world generation

Core rule:

> **Simulation defines the object. Assets renders the object.**


### v0.8 Rendering Aggregation Rules

Future 3D/world rendering must not use one visible mesh per unit for bulk fungible resources.

Core rule:

> **Simulation tracks reality. Rendering shows only the amount of reality necessary to understand the scene.**

Rendering tiers:

1. **Individual object**
   - use when the item has its own identity or active interaction value
   - examples: tools, machines, crafted equipment, batteries, unique parts, actively handled objects

2. **Representative pile / bundle / stack**
   - use for many identical fungible resources
   - examples: logs, stone, plant fiber, ingots, resin containers
   - one visual bundle/pile may represent many simulation units
   - visual size/fullness may scale with quantity without spawning one object per unit

3. **Storage abstraction**
   - deposited materials normally disappear as loose world objects
   - the storage inventory remains the authoritative quantity
   - storage structures/containers may visually imply fullness or category presence
   - withdrawing/staging material may re-create a representative visible object/pile

Important constraints:
- rendering never invents, creates, deletes, or changes physical quantity
- depositing into storage removes visual clutter, not inventory truth
- withdrawing/staging can temporarily de-aggregate visually
- unique crafted objects should preserve their identity
- bulk materials should prefer aggregation/instancing for performance and readability

Example:
- citizen gathers 10 logs → show one carried log bundle
- citizen deposits logs → bundle disappears, storage count increases by 10
- another citizen withdraws 2 logs → show a small staged log representation
- settlement owns 80 logs → do not render 80 separate log meshes

This policy should guide the local asset worker and future procedural 3D system.


## v0.8 Citizen Visual Identity System

Assets planning reference:
`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

Direction:

- six citizens share one mechanical species/civilization language
- each keeps a distinct silhouette and accent identity
- clean base bodies contain no optional equipment
- Home/map uses expressive head tokens
- token visor system supports neutral / blink / happy / focused / curious frames
- Citizens page uses full-body art
- real equipment is rendered as removable modular visual layers only when validated state supports it
- Cato remains the intentionally heavy logistics citizen
- Iri remains especially slim/elegant and construction-oriented
- later 3D models should preserve the same silhouette/color canon and keep optional gear as separate meshes

Core rule:

> **Identity stays. Equipment changes. Expressions live. Simulation remains truth.**
