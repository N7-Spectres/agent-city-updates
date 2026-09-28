# World & Simulation — Backlog

## v0.6 Follow-On / Integration

The core hidden-truth, experiment, discovery, citizen-knowledge, safe snapshot, and learned-process substrate is implemented on `simulation/v0.6-research-discovery`.

Remaining cross-department/integration work:

- Communication maps real transferred facts to `discoveries.id` where safe
- Communication keeps unmatched conversation claims unverified rather than granting Simulation knowledge
- Memory ingests stable discovery/result IDs into bounded per-citizen recall without duplicating hidden truth
- Assets consumes only safe known-state collections and renders missing facts as absence
- coordinator assembles all v0.6 branches and runs the full smoke suite

## Near-Term Simulation Depth

- cooperative job foundation: reserve multiple citizens without race conditions
- visitor turn-around / cancel travel
- richer route/distance representation as geography grows
- explicit project-material transport before remote construction
- equipment transfer/storage assignment beyond maker-owned gear
- experiment tooling/workspace requirements if research depth later needs them
- explicit measurement of deposit quantity only if citizens develop a valid method
- intentional independent-verification semantics for parallel survey/experiment work

## v0.7.0 — Maintenance & Consequences

- wear
- lubrication
- battery health
- component failure
- tool damage
- structure degradation
- repair
- replacement parts
- preventive maintenance
- job interruption/recovery rules for damage or failure

## v0.8.0 — Living World

- citizen-generated place names for discovered geographic features / work sites / settlements
- keep physical coordinates separate from social names; places can exist unnamed before citizens decide they matter
- support persistent renaming/aliases/shared naming conventions as communication and history justify them

- additional regions
- environmental variation
- richer route network
- more materials
- native vegetation behavior
- distant work sites
- possible cultivation if citizens discover a reason
- global spherical coordinates (latitude/longitude)
- local tangent-plane working frames
- continuous citizen positions between landmarks
- exploration intents converted into validated reachable positions
- terrain-aware movement
- citizen-created places and buildings between original landmarks
- routes/roads emerging from use or construction

## v0.9.0 — Continuity

- multi-step plans
- revised/abandoned plans
- skill growth
- emergent specialization
- teaching
- routines
- longer-term resource strategies
- evaluate population growth only after research/fabrication/energy/maintenance/identity continuity are mature

## Open Questions

- how should cooperative jobs reserve multiple citizens?
- how should tool wear/weight/energy tradeoffs interact with job efficiency?
- when should communicated verified discoveries become reproducible skill/process knowledge rather than merely known facts?
- how should damage interrupt active experiment/construction jobs?
- how should reserved construction materials be transported to remote sites?


## v0.6 Integration Gate

Before starting new Simulation feature work:

1. Assets finishes the remaining data-driven v0.6 UI.
2. Coordinator integrates Simulation, Communication, Memory, and Assets.
3. Preserve both `agent_city/knowledge.py` and `agent_city/provenance.py`.
4. Run the full v0.4/v0.5 regression suite plus all v0.6 Simulation/Communication/Memory/Assets smoke tests.
5. Any merge conflict that changes physical truth, discovery semantics, or known-state filtering returns to World & Simulation for review.

Until that gate is complete, the v0.6 Simulation core is considered handed off and feature-complete for this session.
