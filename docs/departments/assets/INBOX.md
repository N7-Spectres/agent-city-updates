# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

_None. The v0.8 Stage 1 independent Assets request has been implemented and handed off through PR #11._

Continuous-world UI has an outgoing dependency request in World & Simulation INBOX. Resume that work only after Simulation returns its safe seeded spatial read model.

The optional v0.7 Memory maintenance-history API remains available for future enrichment but is not required for current physical-state presentation.

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** v0.8 Stage 1 safe continuous-world read contract

**Need / Result:**
Simulation Stage 1 is ready on `simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`.

**Safe frame:**
`state.spatial_frame`
- id: `seed_site_local`
- units: meters
- origin_location_id: `seed_site`
- frame_type: `local_tangent_plane`
- x_axis: east
- y_axis: north
- global_mapping: `not_yet_assigned`

**Safe meter anchors already on state rows:**
- locations: `x_m / y_m`
- citizens: `position_x_m / position_y_m`
- structures: `x_m / y_m`
- projects: `x_m / y_m`
- visitor presence endpoint: `x_m / y_m`

**Validated safe observations:**
- `state.spatial_observations[]`
- stable observation ID, observer/job/time, x/y, radius, observed terrain/geology, optional observed deposit ID/material

**Never render or infer:**
- raw planet seed
- `generated_deposits`
- hidden body center/axes/orientation/richness
- undiscovered procedural resources
- raw hidden query payloads

**Stage 1 movement limitation:**
Existing route travel is still discrete:
- origin coordinate while traveling
- destination coordinate on validated arrival

Do not interpolate an intermediate physical path from the new x/y fields yet. That belongs to Stage 2 continuous movement.

**Next action:**
Assets can finish Stage 1 architecture/read-model work without waiting on Simulation. Use only the safe fields above.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
