# World & Simulation — State

_Last updated: 2026-09-28_
_Current shipped release: v0.7.0_
_Active implementation branch: `simulation/v0.8-seeded-world-stage1`_
_Branch head: `7473b6612ea23cf8d22b31176149da188476690e`_

## Mission

Own physical truth.

> **The AI may decide intent. The simulation decides reality.**

For v0.8 Stage 1 this now includes:

> **The world is deterministic physical truth before it is discovered.**

## Shipped Foundation Preserved

Stage 1 starts from immutable shipped v0.7.0 commit:

`d81a85bf03b69b969532016f59bbbed2233949ee`

All v0.5-v0.7 production, research, knowledge/provenance, maintenance, visitor, and talk-reliability rules remain intact.

## v0.8 Stage 1 — Seeded Spatial World Foundation

### Persistent Planet Seed

Every save now owns one persistent hidden seed:

- `meta.planet_seed`

It is created once if absent and preserved on future startups/migrations.

The raw seed is never exposed through ordinary `/api/state`, visitor/citizen prompts, or UI-facing payloads.

### Local Meter Coordinate Frame

The existing starter world is now anchored in a local tangent-plane frame:

`seed_site_local`

Safe frame metadata:

- units: meters
- origin: Seed Site
- x axis: east
- y axis: north
- frame type: local tangent plane
- global lat/lon mapping: not yet assigned

This is deliberately compatible with a later global spherical coordinate layer.

### Existing Landmarks Preserved

The existing named locations remain the same physical places and IDs.

Current anchor examples:

- Seed Site: (0 m, 0 m)
- Northern Ridge: (0 m, 1800 m)
- Rocky Basin: (1400 m, 0 m)
- Southern Flats: (0 m, -2100 m)
- Resin Grove: (-1200 m, 0 m)

Legacy route distances remain unchanged.

The old x/y-km fields are preserved for compatibility while meter fields are added.

### Meter Positions Added

Persisted meter position foundation now exists for:

- locations: `x_m / y_m`
- citizens: `position_x_m / position_y_m`
- structures: `x_m / y_m`
- projects: `x_m / y_m`
- visitors: `visitor_presence.x_m / y_m`

Existing saves migrate positions from their current landmark/location.

Current legacy route travel remains landmark-based in Stage 1:
- a traveler keeps the origin position while the legacy travel job is underway
- position snaps to the destination landmark when that validated travel completes

Continuous path interpolation/free-roam is intentionally deferred to Stage 2.

### Deterministic Hidden Spatial Engine

New module:

- `agent_city/spatial.py`

Simulation-only hidden query:

- `query_hidden_world(conn, x_m, y_m)`
- wrapper: `simulation.query_spatial_truth(x_m, y_m)`

The result is authoritative hidden truth and must never be copied directly into UI/LLM state.

Generated fields use deterministic hashing + spatially interpolated noise rather than independent random rolls per scan.

Current hidden query includes:

- terrain class
- elevation
- roughness
- geology class
- generated deposit bodies covering the coordinate

Same seed + same coordinate always returns the same result.

Nearby coordinates vary coherently.

### Stable Generated Deposit Bodies

New hidden table:

- `generated_deposits`

Fields include:

- stable `id`
- `source_kind` — `procedural` or `legacy`
- material
- source chunk coordinates
- center x/y
- long/short ellipse axes
- orientation
- hidden richness

Procedural deposit IDs derive deterministically from:

- planet seed
- source chunk
- deposit slot

A nearby query that remains inside the same body returns the same stable deposit ID.

Moving one meter does not automatically mint a new deposit.

### Existing Deposits Anchored

All pre-v0.8 named deposits are migrated into the same hidden spatial-body model.

They retain their existing stable IDs:

- `dep_ferrite`
- `dep_veyra`
- `dep_silicate`
- `dep_copper`
- `dep_carbon`
- `dep_clay`
- `dep_fiber`
- `dep_resin`

Their deterministic geometry is anchored around the existing named location instead of replacing legacy deposit/history records.

### Validated Spatial Observations

New safe persisted table:

- `spatial_observations`

Stable fields:

- `id`
- `observer_id`
- `source_job_id`
- `observation_kind`
- `frame_id`
- `x_m / y_m`
- `radius_m`
- `observed_minute`
- terrain class
- elevation
- geology class
- optional stable deposit ID
- optional material
- summary

Safe observations do **not** expose:

- planet seed
- hidden deposit richness
- full hidden deposit center/axes/orientation
- raw chunk truth

### Minimal Simulation-Owned Observation Contract

New function:

`record_local_spatial_observation(citizen_id, x_m, y_m, ..., max_range_m, observation_kind, radius_m)`

It:

- requires a real citizen
- checks the observation point against the citizen's real meter position
- rejects while the citizen is physically traveling
- validates that any supplied source job belongs to that citizen
- queries hidden truth internally
- persists only the safe observation row
- returns a stable observation ID

This is the Stage 1 primitive future survey/scanner/shared-exploration systems may call after their own physical action/tool rules are validated.

It is **not** itself a scanner or free-roam action.

### Ordinary Safe State

`/api/state` now safely exposes:

- meter positions carried by existing citizen/location/structure/project rows
- `state.spatial_frame`
- `state.spatial_observations[]`

It does **not** expose:

- `planet_seed`
- `generated_deposits`
- hidden body geometry
- hidden richness
- raw hidden world query results

All existing v0.6 hidden-property/resource rules remain preserved.

### Visitor Position

Visitor presence now carries `x_m / y_m`.

Existing visitor route travel updates the visitor meter position to the destination landmark on validated arrival.

### Precision Semantics

Stored numeric coordinates may contain decimal meters for stable computation.

Those decimals are **not** a promise of measurement precision.

Observation precision/footprint is represented by `radius_m` and by the future action/tool contract that produced the observation.

Memory/UI should not infer millimeter-level knowledge merely because a floating-point coordinate has decimals.

## Stage 1 Non-Goals Preserved

Stage 1 does **not** add:

- arbitrary continuous citizen movement
- a globe renderer
- a scanner tool
- free-roam exploration
- generated place naming
- visitor-controlled physical actions
- new communication technology
- arbitrary new citizen technologies
- generated-resource extraction
- direct UI access to seeded hidden truth

## Migration

v0.7 saves migrate additively.

No existing location, route, citizen, project, structure, deposit, discovery, maintenance, memory, provenance, or conversation record is reset.

## Validation

Runtime Stage 1 code passed GitHub Actions run:

`36449582788`

Passed:

- Python compilation
- JavaScript syntax
- all v0.4-v0.7 regression suites
- `tests/smoke_v080_stage1.py`

The only later branch commit restored the normal release-only workflow.

## Status

World & Simulation v0.8 Stage 1 substrate is ready for coordinator/cross-department review.

No `update.json` or release metadata was changed.


## v0.8 Stage 1 Session Close

World & Simulation Stage 1 work is complete and handed off.

Authoritative handoff:
- branch: `simulation/v0.8-seeded-world-stage1`
- head: `7473b6612ea23cf8d22b31176149da188476690e`
- base: shipped v0.7.0 commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- validation: GitHub Actions run `36449582788`

Dependent department contracts delivered:
- Communication: safe meter coordinates, validated spatial observations, future shared-action boundary
- Memory: stable observation/deposit subject IDs and coordinate precision semantics
- Assets: safe spatial frame/position/observation read model

All Stage 1 departments are now ready/reviewable. The only remaining dependency is coordinator Stage 1 review before Stage 2 is authorized.

No release metadata or `update.json` was changed.
