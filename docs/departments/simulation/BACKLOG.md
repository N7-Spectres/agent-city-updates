# World & Simulation — Backlog

## v0.8 Stage 1 Handoff

Implemented on `simulation/v0.8-seeded-world-stage1`:

- persistent hidden planet seed
- local meter coordinate frame
- additive landmark/citizen/visitor/structure/project migration
- deterministic spatial terrain/geology query
- stable procedural deposit bodies with coherent extent
- legacy deposit spatial anchoring
- safe validated spatial observations
- observation range/source-job legality
- safe spatial read-model contract

Cross-department Stage 1 follow-on:
- Communication consumes coordinate/observation contracts for grounding and future shared-action design
- Memory consumes stable observation/deposit subject IDs without ingesting hidden generated world
- Assets may consume safe coordinates/observations but must not infer free-roam or hidden bodies
- coordinator reviews Stage 1 interfaces before Stage 2

## v0.8 Stage 2 Candidates

### Continuous movement
- citizen meter-scale move/travel actions
- path segment identity
- terrain-aware distance/energy/time
- continuous in-transit position
- return-energy reserve against coordinate-based charger reachability
- visitor/citizen shared movement only after Simulation owns the joint action

### Spatial discovery
- integrate existing survey jobs with real action coordinates
- scanner/tool capability only when physically invented/fabricated
- generated-deposit discovery records using stable body IDs
- generated-deposit extraction/quantity accounting
- observation footprints and repeated scan merging
- spatial independent verification by multiple citizens

### Global geography
- persistent planet/body reference frame
- map local tangent plane to global latitude/longitude
- deterministic additional regions and distant sites
- terrain-aware routes that can emerge from movement/construction
- citizen-created places between starter landmarks

### Emergent naming
- separate physical place identity from citizen/social names
- persistent aliases/adoption history
- no culturally meaningful Simulation-generated names

### Living environment
- atmosphere/weather/terrain properties only as physical substrate
- environmental effects on travel/maintenance when modeled
- vegetation/material distributions from the seeded world
- cultivation only if citizens discover/develop a reason/process

### Visitor-linked physical actions
- validated participant list
- co-location
- real duration/path/energy
- real outcome
- normal observation/provenance rules
- no chat-as-admin-control

## Existing Follow-On Depth

- cooperative multi-citizen jobs
- project-material transport for remote construction/maintenance
- equipment transfer/shared caches
- visitor turn-around/cancel travel
- explicit resource-quantity measurement only after valid capability exists

## Open Questions

- what minimum continuous-movement primitive best preserves current route behavior?
- how should generated bodies connect to finite extraction quantity without exposing hidden reserve estimates?
- when should a cluster of observations become a new physical place/site record?
- how should local tangent frames transition between distant settlements on the later spherical world?


## v0.8 Stage 1 Integration Gate

Do not start Stage 2 Simulation feature work until coordinator review confirms the Stage 1 contracts across all departments.

Coordinator review must verify:

1. Simulation hidden seeded world remains hidden.
2. Communication uses safe observations/coordinates only and keeps RP claims separate from validated facts.
3. Memory retains safe observation evidence without ingesting hidden generated-world tables.
4. Assets uses the safe spatial read model and does not infer continuous movement yet.
5. All v0.4-v0.7 regressions plus Simulation/Communication/Memory/Assets Stage 1 smoke tests pass after integration.
6. Any conflict that changes spatial identity, hidden/public boundaries, coordinate semantics, or observation legality returns to World & Simulation for review.

After that gate, Stage 2 may introduce continuous movement, coordinate-based exploration/survey actions, generated-deposit discovery/extraction, and shared visitor actions as separate validated systems.
