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
