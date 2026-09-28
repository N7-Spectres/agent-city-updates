# World & Simulation — Backlog

## v0.7 Follow-On / Integration

The v0.7 maintenance substrate is implemented on `simulation/v0.7-maintenance`.

Remaining integration work:

- Assets consumes authoritative condition/effective-capability fields
- Memory may ingest meaningful `maintenance_events.id` records without storing every wear tick
- coordinator integrates Simulation with Communication talk-reliability, Memory policy/hooks, and Assets UI
- full assembled v0.7 smoke run before publication

## Later Maintenance Depth

- explicit tool/structure failure modes beyond simple non-operational condition
- repair interruption/recovery rules
- component-specific wear only if future systems need that detail
- remote maintenance after physical project-material logistics exist
- preventative maintenance planning across multiple remote sites
- replacement/salvage lifecycle for irreparable equipment
- battery-cell chemistry differences only if future research discovers meaningful properties
- structure-specific degradation from future atmosphere/weather/terrain systems

## Near-Term Simulation Depth

- cooperative jobs / multi-citizen reservation
- visitor turn-around / cancel travel
- richer route/distance representation
- explicit project-material transport before remote construction
- equipment transfer/storage assignment beyond maker-owned/shared-at-location gear
- explicit deposit-quantity measurement only if citizens develop a valid method

## v0.8.0 — Living World

- additional regions
- environmental variation
- richer route network
- more materials
- native vegetation behavior
- distant work sites
- cultivation if citizens discover a reason
- global spherical coordinates
- local tangent-plane working frames
- continuous positions between landmarks
- terrain-aware movement
- citizen-created locations/infrastructure between starter landmarks

## v0.9.0 — Continuity

- multi-step plans
- revised/abandoned plans
- skill growth
- emergent specialization
- teaching
- routines
- longer-term resource strategies
- population growth only after physical/identity prerequisites mature

## Open Questions

- how should cooperative maintenance jobs reserve citizens/tools?
- when should an asset become irreparable instead of fully serviceable?
- how should future weather/environment change degradation rates?
- how should remote repair materials be staged and accounted for?


## v0.7 Integration Gate

Before starting new Simulation feature work:

1. Assets finishes the v0.7 maintenance presentation.
2. Memory finishes any bounded maintenance-history ingestion it chooses to add.
3. Coordinator integrates Simulation + Communication + Memory + Assets.
4. Preserve both v0.7 Simulation maintenance rules and Communication talk-reliability rules during conflict resolution.
5. Run the full v0.4-v0.6 regression suite plus v0.7 Simulation, Communication, Memory (if added), and Assets smoke tests.
6. Any merge conflict that changes wear rates, maintenance thresholds, repair material accounting, battery behavior, or operational-state rules returns to World & Simulation for review.

Until that gate is complete, the v0.7 Simulation core is feature-complete and handed off.
