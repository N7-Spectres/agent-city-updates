# World & Simulation — Backlog

## v0.8 Stage 2 Handoff

Implemented on `simulation/v0.8-exploration-stage2`:

- terrain-costed local meter movement
- coordinate return-energy reserve
- server-derived active movement position/progress
- baseline direct inspection jobs
- meter-aware talk/visit/infrastructure legality
- explicit shared proposal/accept/start/complete lifecycle
- stable shared activity/job/observation source IDs
- shared visitor+citizen movement/inspection
- legacy route compatibility
- additive migration

Cross-department integration remaining:
- Communication binds `shared_action_proposals.simulation_action_id` to Simulation `shared_activities.id`
- Communication maps Simulation `active` to its safe UI `started` state and completion/failure fields
- Communication updates same-region citizen visibility to use meter proximity now that local movement exists
- Memory consumes `shared_activities.id` only for successful completed shared exploration
- Assets consumes `local_movement`, shared lifecycle, visitor shared position, and observation radius
- coordinator merges Stage 2 branches and runs all Stage 1 + Stage 2 smokes

## v0.8 Next Physical Depth

### Generated resource lifecycle
- turn observed `gdep_*` bodies into citizen-known discoverable resource subjects
- finite extraction quantity without exposing hidden richness
- extraction position/range requirements
- independent verification of same body by multiple citizens

### Richer movement
- continuous coordinate travel beyond current 300 m local steps
- coordinate-based charger routing over larger areas
- path/terrain obstacles instead of straight local segment only
- fully coordinate-based replacement for legacy routes when ready
- visitor local independent movement if explicitly designed without becoming admin control

### Shared activities
- active cancellation / interruption
- proposal expiration cleanup
- explicit failed/cancelled completion records
- additional Simulation-owned activity kinds only when physically justified
- multi-citizen cooperative exploration later
- tool-capability-specific observations after real equipment/process discovery

### Place/site creation
- convert significant observation clusters/worksites into persistent physical place IDs
- social naming remains separate from physical site identity

### Global geography
- local tangent-frame to global lat/lon mapping
- distant regions / additional tangent frames
- globe-scale travel only after coordinate/path model is ready

## Existing Follow-On Depth

- cooperative multi-citizen jobs
- project-material transport for remote building/maintenance
- equipment transfer/shared caches
- route turn-around/cancel
- explicit resource quantity measurement only through earned capability

## Open Questions

- when should a local exploratory coordinate become a persistent site/place record?
- how should hidden deposit richness map to finite extractable quantity without leaking reserve estimates?
- when is the legacy route network ready to become fully coordinate-native?
- should visitor-only local walking exist, and if so how is intent exposed without a direct-control feel?


## Stage 2 Integration Gate

Before additional Simulation feature work:

1. Communication consumes the final reject/start/status contract.
2. Assets finishes the Stage 2 map/shared-action presentation.
3. Coordinator assembles Simulation + Communication + Memory + Assets.
4. Run the full v0.4-v0.7 regression matrix, all Stage 1 smokes, and all Stage 2 department smokes.
5. Any merge conflict affecting movement authority, hidden/public boundaries, shared-action lifecycle, proximity rules, or evidence identity returns to World & Simulation.

Until then, Stage 2 Simulation is feature-complete for this work session.
