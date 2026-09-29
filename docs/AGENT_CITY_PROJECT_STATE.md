# Agent City — Project State

_Last updated: 2026-09-29_

## Current Release

**v0.8.7 — Route Travel Visualization**

Agent City is a local-first autonomous mechanical civilization simulation. Six equal mechanical citizens live at Seed Site and act independently through validated simulation actions.

Core law:

> **The AI may decide intent. The simulation decides reality.**

Information law:

> **A citizen only knows what information could actually have reached them.**

Human users such as N7 are **visitors**, not gods, rulers, or omniscient operators.

## v0.9 Stage 1 Integrated Baseline

**Status: integrated and green; not yet published as v0.9.0**

- branch: `release-v0.9.0-stage1-integration`
- immutable green head: `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- combined CI: `36615685005` — PASS
- VERSION on integration branch: `0.9.0` for test/release-line preparation only
- `update.json` remains on the published v0.8.7 runtime

Integrated:
- Memory causal archive / bounded active recall
- persistent citizen plans + plan lifecycle/source links
- canonical physical practice events
- recall-bound self-assessment/teaching language
- perspective-safe recognition without global reputation
- UI-safe remembered-event projection
- citizen-sheet Continuity UI:
  - Ongoing plans
  - Why this exists
  - Plan history
  - Recorded practice
  - Relevant memories
  - explicitly separated Citizen Interpretation layer
- all v0.4 through v0.8.7 regressions remain green
- all four v0.9 Stage 1 smokes pass together

Integration corrections discovered by combined CI:
- standalone Simulation smoke expected fallback Memory wording; integrated assertion now verifies source-linked causal recall
- Communication isolated test doubles were expanded to match the real integrated Continuity/Memory interfaces
- no runtime authority rules were weakened to make tests pass

Stage 1 does **not** yet add:
- competence modifiers
- teaching skill transfer
- habits/routines
- place attachment
- customs/culture
- authored roles/classes/reputation

## v0.9 Stage 2 Upstream Integrated Baseline

**Status: Simulation + Memory + Communication integrated and green; Assets runtime UI now authorized**

- branch: `release-v0.9.0-stage2-integration`
- green head: `ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- combined CI: `36633452433` — PASS
- `update.json` remains on published v0.8.7

Integrated Stage 2 upstream systems:
- family-bounded practice-derived competence
- duration-only bounded physical competence effects
- failed-attempt experience weighting
- degraded-workbench bottleneck dominance
- real two-citizen guided-practice sessions
- one-use learner guidance support on the next matching real task
- Memory retention/recall for guided-practice experience
- teacher/learner role memories remain event-local
- self-only measured competence language
- perspective-safe guided-practice/question/recognition language
- no global reputation, XP, levels, classes, mentor/expert titles, or conversation-only skill transfer

Combined integration correction:
- Communication's isolated Stage 2 competence test double was expanded to supply the integrated `guided_practice_snapshot(...)` interface.
- runtime semantics were unchanged.

Next:
- Assets implements the audited Stage 2 citizen-sheet UI on this exact base.
- Coordinator then runs the final Stage 2 matrix including the Assets smoke before Stage 3 begins.

## Next Major Milestone — v0.9 Civilization Continuity

The v0.9 architecture doctrine is now locked in:

- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

Core continuity law:

> **Persistent behavior must have a traceable history.**

v0.9 is explicitly not an RPG-class layer or generated biography system.

Locked direction:
- Memory is causal infrastructure, not flavor text.
- persistent plans must survive across unrelated actions and remain revisable/abandonable.
- practice may create differentiated competence only from real completed actions.
- no behavior-causing miner / engineer / researcher / builder identity labels.
- self-assessment must be grounded in personal history.
- recognition must emerge through citizen-specific perspective rather than a universal reputation score.
- places may accumulate different meanings for different citizens.
- visitor continuity must come from real source-linked encounters.
- habits require repeated behavior.
- customs/culture require repetition plus social transmission.
- bounded active recall and durable archive are separate concepts.

Planned stage order:
1. **Stage 1 — Causal Memory + Persistent Plans**
2. **Stage 2 — Practice, Competence, Teaching, Recognition**
3. **Stage 3 — Habits, Place Meaning, Social Customs**

Memory & Social is the first Stage 1 dependency. Simulation may audit persistent-plan/event requirements in parallel, but implementation contracts must preserve Memory provenance/retrieval boundaries.


## Recent Visual Foundation

**v0.8.1 — Citizen Visual Assets + Map Readability**

Shipped visual follow-up to v0.8.0.

Release:
- branch: `release-v0.8.1`
- immutable runtime commit: `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`
- final CI: `36468997929` — PASS

Delivered:
- approved runtime-ready full-body + token WebP art for Aris, Bex, Cato, Iri, Noma, and Vale
- full / bust / token slots wired to those assets
- optional equipment layers remain separate and empty unless runtime equipment later supplies them
- map zoom out / zoom in / Region reset
- click-to-focus presentation centering for locations
- location hit targets remain generous but no longer render the visible rectangular hover/focus surface
- denser citizen clusters become more readable as presentation zoom increases
- Simulation/Communication/Memory semantics unchanged

## Current Milestone

**v0.8.7 — Route Travel Visualization**

Published presentation hotfix:
- branch: `release-v0.8.7`
- immutable runtime commit: `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- final CI: `36595479188` — PASS

Delivered:
- legacy route-travel citizen tokens now interpolate between origin/destination using authoritative job progress
- visual map position corresponds to the same progress fraction shown in the citizen card
- traveling tokens display a compact percentage badge
- travel tooltip/accessibility text includes destination and approximate route distance remaining
- meter-space map no longer pins route travelers to their origin coordinate until arrival
- interpolation remains presentation-only and never writes x/y back to Simulation
- local meter movement and shared-activity movement semantics remain unchanged
- dedicated `tests/smoke_v087_route_tokens.py` regression added

**v0.8.6 — Stranded Citizen Recovery**

Published energy-safety hotfix:
- branch: `release-v0.8.6`
- immutable runtime commit: `a72f96b763671f01c5a8aa0ba41d87f7eb6b9a09`
- final CI: `36591711494` — PASS

Delivered:
- charger-bound travel treats the operational charger itself as the safety destination
- no extra 5% post-arrival return reserve is required when the destination has an operational charger
- citizens must still possess enough current energy to pay the real travel cost
- trips to non-charging destinations retain the normal return-energy safety margin
- a critically low citizen who reaches charging remains governed by v0.8.5 autonomous recharge priority
- no teleportation or position rewrite is needed for the observed Iri 6% Resin Grove case
- dedicated regression reproduces Iri at Resin Grove with 6% energy and verifies successful return followed by charging priority

### Emergency Admin Recovery Rule

When a confirmed software bug creates an impossible/deadlocked civilization state, a minimal admin correction is allowed as a repair mechanism.

Prefer, in order:
1. fix the underlying rule so the existing save can recover naturally,
2. if natural recovery is impossible, apply the smallest direct state correction necessary,
3. record the intervention as diagnostic/admin recovery rather than pretending it was an in-world citizen action.

Admin recovery must not become a routine visitor power, shortcut normal consequences, grant resources/technology, or rewrite legitimate citizen outcomes.

**v0.8.5 — Daily Rhythm & Recharge**

Published autonomy/energy rhythm release:
- branch: `release-v0.8.5`
- immutable runtime commit: `5b2395d7e7643a3d7ac9a82ac68090fc97b5f0b7`
- final CI: `36498819565` — PASS

Delivered:
- 06:00–20:00 normal autonomous active cycle
- 20:00–22:00 wind-down that favors wrapping up, returning, unloading, maintenance, conversation, and recharge over starting major new work
- 22:00–06:00 low-activity/recharge cycle that prevents idle citizens from treating night as another full work shift
- critically low autonomous citizens prioritize a physically legal charger or safe return toward charging
- overnight charging repeats real charge jobs until current Energy reaches true usable battery capacity
- degraded battery health is treated as the full-charge ceiling; no pointless charge cycle is offered at that ceiling
- existing active jobs are allowed to finish normally rather than being cancelled by time-of-day
- `possible_actions()` remains the physical-legality contract; daily rhythm is applied only through the autonomous-planning layer
- charger availability requires both physical proximity and matching named location
- world presentation now reflects dawn / daylight / dusk / night without changing Simulation truth
- all v0.4–v0.8.4 regressions plus `tests/smoke_v085_daily_rhythm.py` pass

The release preserves the authority split:
- Simulation defines physical legality and energy truth
- autonomous planning applies daily rhythm to legal choices
- presentation reflects simulated time but never changes reality

**v0.8.4 — Conversation Summary Truth**

Published Communication hotfix:
- branch: `release-v0.8.4`
- immutable runtime commit: `ff78aab0e85331238eb67c989952a72499d1ed78`
- final CI: `36487822361` — PASS

Delivered:
- citizen-to-citizen summaries remain social records rather than physical evidence
- claim-safe summary verbs favor reported / discussed / compared / planned / agreed
- conversation summaries may not independently upgrade claims into validated / confirmed / verified / proved / demonstrated / established facts
- agreements to inspect, travel, recharge, build, or test remain intentions until Simulation records the physical action/outcome
- a citizen reporting inventory/status is still a report to the listener, not independent verification
- Simulation, Memory, personality, and UI authority remain unchanged


**v0.8.3 — Citizen Personality + Natural Dialogue**

Published behavior/dialogue patch:
- branch: `release-v0.8.3`
- immutable runtime commit: `e4d216b133a18dc4c68e1bba1ceb0457e952efb6`
- final CI: `36478041248` — PASS

Delivered:
- distinct stable personality tendencies and voice guidance for Aris, Bex, Cato, Iri, Noma, and Vale
- personality influences preferences, tone, curiosity, caution, and cooperation without granting authority or extra knowledge
- no default leader/ruler/command weighting
- visitor and citizen-to-citizen dialogue keeps planner/system vocabulary backstage
- natural speech replaces phrases such as "active job queued" / "current intent" / "propose shared action" where ordinary language fits
- planner may use personality as a soft behavioral bias only; Simulation legality, knowledge boundaries, survival constraints, and physical outcomes remain authoritative
- Simulation and Memory semantics unchanged


**v0.8.2 — Live State Readability**

Published UI-only patch:
- branch: `release-v0.8.2`
- immutable runtime commit: `9a11b2bc21ba2338d6b231924036bf6d5935475c`
- final CI: `36473856852` — PASS

Delivered:
- Home citizen cards keep the same compact dimensions
- current Energy and Integrity now use thin inline micro-bars plus exact percentages
- Citizen sheet uses the same authoritative live Energy/Integrity values and matching meters
- long-term battery health/capacity is clearly separated from current charge
- no Simulation, Communication, Memory, or physical-state semantics changed


v0.8.0 — Living World is assembled, fully regression-tested, versioned, and published from immutable runtime commit `a870982ba947fcc5af08ca190de396ae4308b645`.

Final release validation:
- GitHub Actions run `36462126434`
- Python compilation passed
- JavaScript syntax passed
- all v0.4 regressions passed
- all v0.5 smoke suites passed
- all v0.6 smoke suites passed
- all v0.7 smoke suites passed
- all four v0.8 Stage 1 smokes passed
- v0.8 Stage 2 Simulation smoke passed
- v0.8 Stage 2 Communication smoke passed
- v0.8 Stage 2 Memory smoke passed
- v0.8 Stage 2 Assets/UI smoke passed

Major shipped v0.8 changes:

- persistent hidden planet seed
- deterministic meter-scale local world truth derived from seed + coordinate
- spatially coherent terrain/geology/resource generation instead of per-scan rerolls
- stable spatial deposit bodies with repeat-encounter identity
- additive migration of existing named landmarks/deposits into the spatial model
- authoritative local x/y positions for citizens, visitors, structures, projects, and locations
- real local exploration/movement jobs with distance/terrain/energy consequences
- coordinate-aware return-energy reserve
- validated local observations with bounded uncertainty and stable evidence IDs
- explicit visitor-linked shared walk/inspect lifecycle with separate proposal, accept, start, reject, active, and complete states
- Communication grounding for visitor RP, hypotheses, capabilities, and tool use
- bounded spatial Memory for nearby prior observations and completed shared exploration
- continuous meter-space map presentation using only authoritative movement fields
- shared-action proposal/accept/reject/progress UI
- observation uncertainty rings and baseline privacy
- restored citizen job progress bars and Enter-to-send chat
- six-citizen visual-profile framework with removable equipment layers
- presentation-only local AssetQueue scaffold and render-tier contract
- no Blender/3D runtime dependency yet

The release preserves the authority chain:
- conversation/exchange = social source
- Communication proposal = intent/UI projection
- Simulation shared activity = canonical physical shared event
- Simulation job = active physical movement
- spatial observation = validated exploration evidence


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
- `docs/V100_DEVELOPMENTAL_AUTONOMY_NOTES.md` — future v1.0 scaffolding/autonomy notes; not current v0.9 scope
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


## Shipped v0.6 Scope

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
- v0.8.1 Citizen Visual Assets + Map Readability shipped from immutable runtime commit `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`
- v0.8.0 Living World shipped from immutable runtime commit `a870982ba947fcc5af08ca190de396ae4308b645`
- the planned v0.7.1 follow-up scope is folded into v0.8.0; there will not be a separate 0.7.1 release unless a critical hotfix appears
- v0.8 Living World should begin with a persistent planet seed and meter-scale deterministic spatial truth: the hidden world is derived from seed + coordinate, scans reveal rather than reroll reality, and discovered deposits retain stable physical identity/spatial extent
- v0.7.1 visitor roleplay grounding should keep natural face-to-face RP while treating visitor-described physical details as claims/observations until Simulation validates them; chat must not become a hidden world editor
- v0.7.0 Maintenance, Consequences & Home Polish shipped from immutable runtime commit `d81a85bf03b69b969532016f59bbbed2233949ee`
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


## Shipped v0.7 Scope

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
