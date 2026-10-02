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


## v1.1.3 shared sun / day-night lighting

Local, Region, and Planet now share one presentation light source driven only by the authoritative simulation clock.

- Local uses a tangent-space sun direction and terrain surface normals.
- Region and Planet use the same sun converted into globe coordinates.
- The Seed Site local day/night state therefore agrees with the lit hemisphere on the globe.
- Planet uses a soft terminator rather than a hard half-sphere cutoff.
- Region keeps a higher readability floor while preserving the same light direction.
- Night retains an ambient floor so terrain and markers remain usable.
- DOM labels, citizen markers, and selection UI remain outside world-light attenuation.
- The sun/light model never changes time, coordinates, travel, visibility authority, discovery, or resources.

The light cycle interpolates continuously between state refreshes using the existing simulation time ratio. It is a presentation of Simulation time, not a second clock.
