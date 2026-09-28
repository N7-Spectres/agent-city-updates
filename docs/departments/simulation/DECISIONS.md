# World & Simulation — Decisions

## Physical Authority

Simulation state is authoritative over narration.

An LLM statement cannot:

- move a citizen
- create materials
- complete construction
- discover a deposit
- repair damage
- create a communication device
- change a structure
- create research results

without a validated simulation transition.

## No Gamey Tech Tree

Research should not become a visible fixed ladder of predetermined human technologies.

Hidden material properties and world-specific outcomes should allow experimentation to matter.

## Aptitudes Are Not Classes

Aris, Bex, Cato, Iri, Noma, and Vale have starting aptitudes, not permanent jobs.

Experience may eventually create specialization.

## Mechanical Needs

Citizens do not need human food/oxygen/sleep.

They do need physically relevant mechanical support such as:

- energy
- integrity
- maintenance
- lubrication
- replacement parts
- tools
- workspace
- shelter from relevant environmental hazards

## Parallel Work

Multiple citizens may sometimes perform overlapping work.

Do not automatically forbid parallel effort simply because one citizen began first.

If duplicate work matters, model it intentionally as:

- independent verification
- redundant effort
- cooperative work
- wasted effort

rather than relying on accidental race conditions.

## Visitor Role

Visitors may observe, travel, converse, and suggest.

Visitors do not become in-world rulers or direct command consoles.

## Ownership Boundary

Simulation owns action legality, time, resource accounting, geography, and physical consequences.

Other departments may consume simulation state but should not rewrite physical rules for convenience.


## Geospatial Direction

Agent City should eventually use a spherical world without forcing every local calculation to operate directly in latitude/longitude.

Use two coordinate layers:

1. **Global physical position** — latitude/longitude on the planet surface.
2. **Local working coordinates** — a small tangent-plane / local (x, y) frame around a settlement, work site, or region for buildings, paths, and short-distance movement.

Latitude/longitude is authoritative global geography. Local (x, y) is a convenient local representation that converts back to the same physical surface.

Named places such as Seed Site, Resin Grove, and Northern Ridge may remain useful landmarks, but they should eventually have physical coordinates rather than being only abstract graph nodes.

Citizens should eventually be able to occupy continuous positions between named locations.

Construction may occur between established locations when the simulation validates a suitable site. This allows useful emergent infrastructure such as a field shelter, charging stop, storage cache, workshop, road, or later a new settlement.

Do not give the LLM unrestricted arbitrary coordinates. The AI should choose intent such as "explore northeast", "survey between Seed Site and Northern Ridge", or "find a suitable midpoint site"; Simulation validates and selects/restricts the actual reachable position.

Keep the physical model realistic enough to create meaningful distance, terrain, routes, and infrastructure decisions, but avoid unnecessary geodesy/physics complexity.


## v0.5 Physical Production

Fabrication and construction are simulation transitions, not narrative claims.

A fabricated object exists only after:
- required materials are validated and consumed/reserved according to the process,
- a real timed fabrication job completes,
- Simulation persists the resulting equipment record.

A constructed structure exists only after:
- a persisted project exists,
- required materials are reserved,
- a real construction job is underway,
- the job completes successfully,
- Simulation persists the resulting structure at the validated site.

## Project Lifecycle

The minimal v0.5 lifecycle is:

`planned -> reserved -> underway -> complete`

Do not skip directly from discussion or intention to physical completion.

Remote construction is not allowed to teleport settlement materials. Until explicit project-material transport exists, v0.5 construction remains settlement-local.

## Physical Equipment Effects

Capability changes come from real equipment records, not arbitrary level bonuses.

Current supported examples:
- cargo equipment adds explicit carrying capacity
- extraction equipment changes extraction job duration through an explicit multiplier

Equipment effects are derived from owned or physically available equipment.

## Energy Return Reserve

Remote work and outbound travel must preserve enough energy to reach a known operational charger plus a modest safety margin.

The planner may choose intent, but Simulation withholds/rejects physically unsafe actions.

Operational charging structures are represented physically with `structures.provides_charging = 1`. Adding a future charger/outpost can therefore change safe operating range without a special-case planner rule.

## Cargo Return Choice

Do not hard-code automatic return-to-storage behavior.

Citizens may decide when returning/depositing is useful, subject to physical legality and energy safety.

## Event Identity

Durable `jobs.id` is the authoritative action/event anchor for validated physical work.

Durable `projects.id` is the authoritative project anchor.

Do not create a parallel generic event system unless future requirements exceed what these stable records can represent.

Pre-v0.5 completed jobs are labeled `legacy_complete` when richer outcome semantics were not recorded originally.

## Conversation / Physical Job Integrity

A physical talk job is successful only when a real durable conversation source exists for that job.

`citizen_conversations.source_job_id` is the link.

If no exchange was actually stored, Simulation marks the talk job failed and does not invent dialogue to make chronology look successful.


## World Substrate vs Citizen Solutions

Simulation development should provide laws, capabilities, and constraints rather than predetermined civilization answers.

Examples of appropriate simulation additions:
- fabrication mechanics
- measurable material properties
- atmosphere and weather
- energy and maintenance rules
- terrain and movement
- structures and equipment as physical objects
- experimentation and validated outcomes

Examples of things that should normally emerge through citizen behavior instead of being directly granted:
- a specific hauling solution
- a radio
- a road
- a field station
- a specialized processor
- a specific advanced tool

If a new system merely solves a current citizen problem for them, prefer not to add it.

If a new system makes a previously unmodeled part of physical reality available for citizens to reason about, it may be appropriate.

Target handoff:
- pre-v1.0: complete the world's core substrate
- v1.0 and beyond: preserve autonomy, fix/visualize/optimize/deepen the world, and let citizens determine their civilization's solutions


## v0.5 Handoff Lock

For coordinator/department integration, preserve all of the following together:

- project/equipment/structure state remains Simulation-authoritative
- `citizen_conversations.source_job_id` remains nullable and unique for source-linked talks
- a physical talk job without a durable stored exchange fails
- Assets displays Simulation state but does not infer physical completion/capability
- Memory may reference stable project/job/equipment/structure IDs but must not convert discussion into physical history
- no remote construction until project materials can be transported physically
- no publication or `update.json` change without explicit human instruction


## Population Growth / New Citizens

The initial population of six is a starting population, not necessarily a permanent hard cap.

There is currently no mechanism for citizens to create additional citizens.

If population growth becomes possible later, it should emerge through real simulation systems rather than a direct visitor control or automatic spawning. Creating a new autonomous citizen should require sufficient knowledge, materials, fabrication capability, energy support, and a validated activation process.

The civilization should decide whether creating another autonomous citizen is useful.

Keep a clear distinction between:
- autonomous citizens with their own identity, memory, and agency
- non-citizen machines, tools, carts, haulers, or other equipment

A newly created citizen should not automatically inherit another citizen's personal memories. Any future shared baseline knowledge must be explicitly designed and must not erase individual experience.

Population growth belongs later, after research, fabrication, maintenance, energy, and continuity systems are mature enough to support it meaningfully.


## Hidden Truth / Known Truth Boundary

Simulation may persist physical facts that no citizen knows.

Hidden truth must not appear in:

- ordinary `/api/state`
- planner prompts
- visitor-facing location/resource views
- Memory merely because the truth exists

A hidden fact becomes eligible for known-state interfaces only after a validated discovery event.

Absence from known state means unknown. Do not render an artificial "locked secret" that confirms hidden content exists.

## Discovery Is Local Knowledge First

A discovery event records what physically became knowable and who directly discovered it.

Direct discovery grants knowledge only to that citizen.

Do not automatically copy a discovery into every citizen's knowledge.

A second citizen may learn it later through:

- their own validated observation/experiment
- a real Communication transfer
- a future legitimate information mechanism

## Claims vs Verified Knowledge

A conversation claim is not itself a Simulation discovery.

Communication may attach a transferred claim to a validated `discoveries.id` only when the actual communicated fact can be mapped to that discovery.

If the speaker's statement cannot safely be tied to a validated discovery, keep it as an unverified/remembered claim in Communication/Memory instead of inserting verified Simulation knowledge.

Repeated retelling never upgrades verification by itself.

## Experiments

Generic assay availability does not imply a hidden property exists for that method.

Simulation determines experiment outcome.

A completed experiment may be:

- `discovery`
- `verified`
- `inconclusive`

Inconclusive results persist.

Wrong-method experiments are allowed because failure is part of research rather than a UI-hidden answer key.

## Learned Processes

A learned process must descend from a validated discovery.

Current v0.6 learned processes are repeatable verification procedures only.

They are not technology-tree nodes and do not automatically unlock named civilization solutions.

## Survey Repetition

Survey legality must not leak whether hidden facts remain.

Repeat surveys may produce:

- new discovery
- independent confirmation
- no new finding

This also gives parallel/redundant survey work an intentional physical outcome instead of a race-condition-only meaning.

## Public Deposit State

Undiscovered deposits are absent from ordinary state.

Even after discovery, raw hidden remaining reserve quantity is not exposed unless a future validated measurement system explicitly discovers that quantity.

Extraction still uses authoritative hidden reserve accounting internally.


## v0.6 Integration Handoff Lock

Coordinator integration must preserve these Simulation decisions together:

- `world_properties` is hidden physical truth and never ordinary UI/planner state
- `discoveries.id` is the stable validated discovery anchor
- direct discovery grants knowledge only to the discovering citizen
- communicated claims do not silently become verified Simulation knowledge
- undiscovered deposits are absent from ordinary state
- discovered deposits do not expose hidden reserve quantity
- inconclusive experiments remain persisted outcomes
- learned processes descend from validated discoveries and are not tech-tree nodes
- missing knowledge is represented as absence, not a hint that secret data exists
- Simulation `agent_city/knowledge.py` and Communication `agent_city/provenance.py` are separate layers and both must survive merge


## Emergent Place Naming

As exploration expands beyond the starter region, named places should increasingly emerge from citizen discovery rather than being pre-authored by development.

Simulation should distinguish:
- the physical place/coordinate itself, which exists independently of naming
- one or more citizen-used names for that place, which are learned/social information

A newly discovered feature may initially have no citizen name. If repeated use, resource value, navigation importance, memorable events, or social discussion makes the place significant, citizens may decide to name it.

Examples:
- an unnamed lake becomes a named landmark after citizens repeatedly use it as a navigation/resource reference
- a ridge, basin, grove, work site, crossing, or settlement acquires a name through actual use
- names may change, gain aliases, or differ between citizens until communication establishes a shared convention

Do not have the Simulation invent a culturally meaningful name merely because a coordinate was generated. The physical feature can exist first; naming is a social/civilizational act.

Future place names should be persistent history. Once adopted and used, they should survive restart and remain part of maps/records unless citizens intentionally rename the place.


## Deterministic Procedural Universe

Long-term world generation should be deterministic from a persistent random seed so the universe feels discovered rather than invented on demand.

Preferred hierarchy:
- universe seed
- star-system seed(s) derived from universe seed
- planet/moon seed(s) derived from system seed
- regional/local terrain seeds derived from body seed

The simulation may generate distant content lazily for performance, but the result must be deterministic from the stored seed. Observing a location should reveal what was already determined by the seed, not reroll reality.

Seeded generation may define hidden physical truth such as:
- stellar type, luminosity, age, and orbital layout
- planetary radius, gravity, rotation/orbit
- atmosphere and climate tendencies
- terrain/geology
- water/ice distribution
- native materials/chemistry
- moons/rings
- resource distributions
- later distant star systems

Citizens must still discover this truth through real observation/research. The seed is an implementation mechanism, not in-world omniscience.

If citizens eventually create spaceflight, the same deterministic system can reveal additional planets, moons, asteroids, or neighboring stars without requiring handcrafted content.

## Stellar-Scale Engineering

Do not grant megastructures as tech-tree unlocks.

If the civilization eventually develops sufficient materials science, orbital mechanics, fabrication, automation, energy demand, and space industry, stellar-scale power collection may become physically possible.

A Dyson-style project should emerge from citizen needs and engineering history rather than being scripted. A distributed Dyson swarm / orbital collector network is the more physically plausible default than a rigid solid shell, though the simulation should not force a specific design if citizens discover another workable world-specific solution.

The development team should provide the physical substrate for orbital construction and energy collection, not a "Build Dyson Sphere" button.


## v0.7 Maintenance Model

Maintenance is physical consequence, not an RPG debuff system.

Use four primary signals:

- equipment condition
- structure condition
- citizen joint wear
- citizen battery health

Avoid adding many overlapping abstract condition meters unless a future physical system genuinely requires them.

## Gradual Wear

Wear should come from simulated time and real use.

Routine use makes small changes. Maintenance should become relevant over meaningful stretches of simulated life rather than after every task.

Time-based wear advances only while simulation time advances.

## Condition and Capability

Equipment condition scales its real physical modifiers.

Current rule:

- above 20 condition: equipment may function
- lower condition proportionally weakens its bonus
- at/below 20: non-operational until repaired

Structures use the same critical operational boundary.

Degraded supporting structures may increase job duration rather than inventing arbitrary success penalties.

## Maintenance Thresholds

Current planner-facing thresholds:

- equipment/structure service due below 90
- battery replacement due below 85 health
- chassis lubrication/service due at joint wear >= 12
- critical equipment/structure at condition <= 20

These thresholds are Simulation rules. Assets should consume the exposed derived fields rather than duplicating them.

## Battery Health vs Energy

`energy` is current usable charge.

`battery_health` is long-term usable capacity.

Battery health caps maximum recharge. Replacing the battery restores health but does not grant free charge.

## Maintenance Material Locality

Service consumes real materials.

Current v0.7 maintenance using settlement stores is limited to Seed Site. Do not allow remote repairs to consume Seed Site inventory magically.

Remote service can expand later only after explicit material transport/storage exists.

## Maintenance Memory Boundary

Stable `maintenance_events.id` represents meaningful completed service/repair/replacement.

Do not create a durable social/memory event for every tiny wear decrement.

Threshold crossings may appear in physical History, while Memory should normally retain meaningful maintenance events, failures, shortages, or major degradation rather than routine microscopic wear.

## Future Charger Compatibility

Charging functionality is capability-based through `structures.provides_charging`, not hard-coded to the starter Charging Station name.

Maintenance/degradation logic must preserve that capability model for future citizen-built chargers/outposts.


## v0.7 Integration Handoff Lock

Coordinator integration must preserve the v0.7 maintenance model as one physical system:

- battery health remains distinct from current charge
- condition-scaled equipment capability remains Simulation-authoritative
- degraded structures may slow or block supported work
- critical equipment/structures remain visible and repairable
- future chargers remain capability-based through `provides_charging`
- passive wear advances only with simulation time
- service/repair consumes real materials and real job time
- remote maintenance cannot consume Seed Site stock until physical logistics exist
- `maintenance_events.id` remains the stable completed-maintenance anchor
- routine wear does not become one durable event per tiny decrement
- all v0.6 hidden-truth/provenance/knowledge boundaries remain unchanged


## Render Representation vs Physical Quantity

Simulation quantity and render representation are separate concerns.

For fungible bulk materials, Simulation stores the authoritative quantity while Assets may aggregate many units into one representative visual bundle, pile, stack, or storage-fullness state.

Examples:
- 20 logs in Simulation do not require 20 individual log meshes
- 10 Plant Fiber may render as one bundle
- materials deposited into storage normally stop existing as loose world visuals while remaining fully present in authoritative storage inventory
- withdrawing or staging material may create a representative visible object again

Unique tools, machines, crafted equipment, and other identity-bearing objects should generally retain individual visual identity.

Rendering must never alter quantity or physical truth. Asset instancing/aggregation is a presentation optimization only.


## Seeded Spatial Truth

The procedural planet should expose deterministic hidden physical truth at coordinates, not generate a fresh result every time somebody scans.

Core rule:

> **The seed determines what is physically there. Citizens and visitors only learn it through valid observation.**

Implementation direction:
- store one persistent planet/body seed in the save
- use authoritative coordinates for every citizen, visitor, sample, discovery, structure, and scan
- derive local terrain/geology/resource truth deterministically from planet seed + coordinate/chunk
- generate lazily for performance, but never reroll an already-determined coordinate
- the same coordinate queried later must resolve to the same hidden physical world
- nearby coordinates should be spatially correlated rather than independent random rolls

Deposits should be spatial bodies/fields, not "one random deposit per scan".
A scan one meter away may:
- still be inside the same vein/deposit,
- cross into a different part of that same body,
- reveal a separate nearby deposit,
- or find nothing useful.

When a real deposit is first encountered, give it a stable physical ID plus spatial extent/geometry sufficient to recognize later encounters with the same body.

Knowledge boundary:
- Simulation/world generation may know the hidden terrain/material/deposit truth
- citizens and visitors do not know it until valid observation, survey, scan, experiment, or communication occurs
- the UI must not expose raw seed/world-generator output
- a scan result reveals only what the actual instrument/action can measure

This same hierarchy should later scale from local meter-level exploration to global planetary coordinates and, eventually, additional seeded celestial bodies.


## v0.8 Stage 1 Seeded Spatial Truth

The planet seed is persistent save state and hidden physical truth.

Do not expose `meta.planet_seed` to citizens, visitors, UI, Memory, or Communication.

A query result is not a discovery. Calling the hidden world function does not itself make anything known.

## Determinism

World generation must be deterministic from the persistent seed and physical coordinate/chunk.

Do not use per-scan random rolls for terrain/geology/deposit identity.

Lazy materialization is allowed only when the materialized result is a cache of deterministic truth.

## Spatial Correlation

Terrain/geology must vary spatially and continuously enough that nearby positions are related.

Resource bodies have physical extent.

Moving one meter may:
- remain inside the same body
- leave a body near its edge
- enter another overlapping body

It must not automatically generate a brand-new deposit merely because the coordinate changed.

## Stable Deposit Identity

Procedural deposit IDs derive from stable seeded source coordinates/slots.

A deposit's identity is independent of who discovers it and when.

Legacy named deposits retain their pre-v0.8 IDs and are spatially anchored rather than replaced.

## Local / Global Coordinate Layers

Stage 1 local coordinates are a tangent-plane frame:

- x = east meters
- y = north meters
- origin = Seed Site

Later global latitude/longitude may map this frame onto a spherical body without changing local history or IDs.

Do not reinterpret the current local x/y values as latitude/longitude.

## Hidden vs Safe Spatial State

Hidden:
- planet seed
- generated-deposit table
- richness
- full hidden body geometry
- raw hidden query results

Safe after validation:
- actor's authoritative meter position
- known landmark meter coordinates
- persisted validated observation
- stable deposit ID/material only when a validated observation actually revealed contact

## Observation Contract

`spatial_observations.id` is the stable Stage 1 observation/event anchor.

A validated observation must be tied to:
- a real observer
- a real coordinate
- a physical range
- a simulation minute
- an optional real source job belonging to that observer

Traveling citizens cannot make local stationary observations.

A future scanner/survey/shared action owns its own legality, duration, energy/tool requirements and calls the observation primitive only after those physical rules are satisfied.

## Coordinate Precision

Floating-point coordinate storage is computational precision, not epistemic/sensor precision.

Use `radius_m` and source action/tool semantics to describe what was actually observed.

## Route Compatibility

Named route travel remains the authoritative movement system in Stage 1.

Meter positions snap to validated route destinations on completion.

Do not present the Stage 1 position field as continuous travel interpolation until Simulation implements a real continuous movement/path contract.

## No Technology by Substrate

Adding deterministic hidden geology does not grant citizens:
- scanners
- drills
- navigation electronics
- satellite maps
- prospecting sensors
- generated-deposit extraction capability

Physical technology still requires real learned processes/equipment/capability.


## v0.8 Stage 1 Integration Handoff Lock

Coordinator integration must preserve the seeded-world substrate as one coherent authority layer:

- persistent `planet_seed` remains hidden and stable per save
- deterministic hidden queries stay seed/coordinate-derived
- legacy landmarks/routes/deposits retain existing identity
- local meter coordinates remain a tangent-plane frame, not global lat/lon
- stable generated deposit IDs remain independent of discovery/person/time
- hidden deposit geometry/richness never leaks through ordinary state
- `spatial_observations.id` remains the safe validated spatial evidence anchor
- observation legality continues to enforce observer position, source-job ownership, range, and travel state
- coordinate decimals remain computational precision only; `radius_m` and source action/tool define epistemic precision
- Stage 1 route travel remains discrete and must not be visually or narratively upgraded to continuous movement
- Stage 1 does not grant scanners, free-roam movement, shared visitor actions, or other technologies
- all v0.5-v0.7 physical/knowledge/provenance/maintenance invariants remain intact


## v0.8 Stage 2 Continuous Local Movement

Local continuous movement is a timed Simulation job.

Authoritative movement state consists of:
- stable job ID
- frame ID
- start coordinate
- target coordinate
- start/end simulation time
- path distance
- terrain-derived traversal multiplier

Current position during movement is derived by Simulation from those fields and current simulation time.

Frontend interpolation may visually smooth the same authoritative segment, but it must not invent a different path or timing.

## Local Movement / Legacy Route Boundary

Stage 2 local movement does not replace legacy named routes.

If a citizen has intentionally moved away from a landmark through a completed Stage 2 local/shared action, they must physically return to the landmark before entering the legacy route network.

Legacy records/saves that only contain old `location_id` state and no Stage 2 offset history retain region-based route compatibility.

This compatibility rule is transitional and should be removed only when the route network itself becomes fully coordinate-based.

## Baseline Direct Observation

Baseline walking/inspection is not a scanner.

It may establish:
- directly visible terrain
- approximate elevation
- stable physical contact with a seeded body

It must not establish:
- material identity
- chemistry
- hidden geology classification
- deposit richness
- hidden geometry

Those require future validated capability/tool/process.

## Shared Activity Authority

Communication proposal identity and Simulation physical action identity are separate.

Simulation canonical shared physical source:
- `shared_activities.id`

Physical job source:
- `jobs.id`

Evidence source:
- `spatial_observations.id`

Do not use a Communication proposal row as proof that movement occurred.

## Shared Lifecycle Separation

Proposal, acceptance, and physical start are separate transitions.

Acceptance is consent/intention only.

Only `start_shared_activity` may create the real movement job after physical revalidation.

Chat text, proposal status, or acceptance status must never mutate coordinates or create observations.

## Shared Participant Rule

Current shared physical scope is deliberately narrow:
- one visitor
- one citizen
- local walk
- direct inspection at destination

It is not a general party/group/command system.

Stage 2 validates co-location, proximity, citizen energy, target range, and real equipment if requested.

## Shared Tool Rule

Only runtime equipment records may satisfy a requested tool.

Owned citizen equipment is physically available with the citizen.

Shared location equipment is considered physically available only while the citizen is near its landmark.

Concept art, dialogue, or visual layers never create tool capability.

## Exploration Evidence Identity

`spatial_observations.id` remains the physical evidence identity.

`deposit_id` remains stable subject identity.

A shared experience and its spatial observation are related but distinct records:
- shared activity = social/physical event
- observation = evidence produced by that event

Memory must not collapse them into one source.

## Continuous Proximity

Named location membership no longer implies face-to-face proximity.

Talk/Visit requires actual meter-scale proximity.

This is a durable Stage 2 spatial law for future continuous-world systems.
