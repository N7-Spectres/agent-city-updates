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
