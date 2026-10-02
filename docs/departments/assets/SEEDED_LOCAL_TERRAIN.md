# Seeded Local Terrain Mesh

_Last updated: 2026-10-02_

## Purpose

Local mode now renders a real WebGL terrain mesh derived from Agent City's existing persistent world seed instead of always drawing a flat plane.

This is an **Assets / presentation consumer** of world-generation truth. It does not create geography, resources, discoveries, or citizen capabilities.

Core authority remains:

> **Simulation defines reality. Assets renders reality.**

## Seed boundary

The persistent `planet_seed` remains server-side.

The Local renderer reads only:

`GET /api/world/local-terrain`

That endpoint calls `public_terrain_heightfield()` and returns only a coarse elevation grid.

It does **not** return:
- `planet_seed`
- geology class / material fields
- deposit identities or geometry
- richness
- long / short axes
- hidden resource locations

The public mesh is therefore not a free prospecting or survey tool.

## Surface contract

The public heightfield:
- uses the same broad/local elevation noise namespaces as authoritative terrain
- samples a coarse odd-sized grid (default 41 × 41)
- quantizes elevation to 2 m increments
- is centered on Seed Site
- clamps requested radius to 800–4200 m
- carries the discovery-boundary marker `surface_only_no_geology_or_deposits`

Changing the world seed changes the mesh deterministically. The same seed + request yields the same mesh.

## Local presentation

The current Local renderer:
- expands the presentation surface from ±3.0 to ±3.45 world units
- requests terrain approximately 1.55× beyond the farthest known Local anchor
- uses 3.2× vertical exaggeration so broad relief remains readable at map scale
- defaults to a slightly wider Local camera: pitch 0.72, distance 4.85
- allows Local zoom-out to 10.5
- retains the old flat plane/grid as a fallback if the terrain endpoint is unavailable

The 3.2× height multiplier is **presentation-only**. It is not physical vertical scale.

## Grounding

`localWorld()` now samples the loaded terrain height before projecting Local entities.

This keeps:
- citizens
- known locations
- structures
- visitor markers

visually grounded on the mesh while their authoritative X/Y meter coordinates remain unchanged.

Known routes are subdivided into short visual segments and draped over the sampled surface instead of being drawn as one flat endpoint-to-endpoint line.

No renderer code writes coordinates back to Simulation.

## Discovery and future expansion

The mesh intentionally provides broad topography without resource truth.

Future safe extensions may include:
- higher detail only around validated surveyed/observed areas
- biome/surface tint derived from already-known observations
- chunked mesh streaming as Local range grows
- true 3D citizen/building assets grounded through the same terrain sampler

Do not add geology/resource coloring directly from hidden seed fields. A resource or material becomes visible only through the existing discovery pipeline.


## v1.1.2 readability pass

The seeded surface data and authority model are unchanged.

Presentation refinements:
- high areas receive a very subtle overlay based on public elevation
- locally steeper cells receive a subtle shadow overlay based on neighboring public elevations
- minor mesh wires are drawn every second sample instead of every sample
- every sixth sample remains a slightly stronger reference line
- known locations receive small pads that follow the sampled terrain surface
- the desktop Home world viewport receives a modest vertical expansion

These changes improve terrain readability only. They do not modify seeded elevation, discovery, travel, coordinates, or resource knowledge.
