# World & Simulation — Backlog

## Near-Term After v0.5 Integration

- refine duplicate/parallel survey behavior intentionally
- cooperative job foundation: reserve multiple citizens without race conditions
- expose richer action progress metadata cleanly to UI where current job timing is insufficient
- support visitor turn-around / cancel travel behavior
- improve route/distance representation as geography grows
- continue testing citizen talk job edge cases after branch integration
- define explicit project-material transport before allowing remote construction
- decide how equipment transfer/storage assignment should work beyond maker-owned personal gear

## v0.5 Follow-On Depth

Core fabrication, construction, equipment modifiers, project lifecycle, energy reserve, charger representation, and coordinate groundwork are implemented on the department branch.

Remaining depth:
- broader physically learned fabrication processes after research exists
- tool requirements for particular future processes
- explicit remote construction logistics
- cooperative fabrication/construction jobs
- project cancellation/recovery rules
- equipment wear/weight/energy tradeoffs when maintenance systems arrive

## v0.6.0 — Research & Discovery

- hidden material properties
- experiment actions
- simulation-determined outcomes
- persistent discovered knowledge
- reproducible learned processes
- failed experiment history
- new capabilities derived from discovered properties
- keep newly learned processes separate from a visible fixed technology tree
- ensure research results remain unknown to LLM context until physically discovered/communicated

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

- additional regions
- environmental variation
- richer route network
- more materials
- native vegetation behavior
- distant work sites
- possible cultivation if citizens discover a reason
- global spherical coordinates (latitude/longitude) for persistent geography
- local (x, y) working frames around settlements/regions
- continuous citizen positions between named landmarks
- exploration intents that Simulation converts into validated reachable positions
- terrain-aware movement without overcomplicated physics
- citizen-created places and buildings between original landmarks
- routes/roads that can emerge from repeated use or construction

## v0.9.0 — Continuity

- multi-step plans
- revised/abandoned plans
- skill growth
- emergent specialization
- teaching
- routines
- longer-term resource strategies

## Open Questions

- how should cooperative jobs reserve multiple citizens?
- how should tool wear/weight/energy tradeoffs interact with job efficiency?
- how should research results remain unknown to the LLM until discovered?
- how should injuries/damage interrupt active jobs?
- how should reserved construction materials be physically transported to remote project sites?


## Integration Gate

Before this department resumes new physical-feature work:

1. Assets finishes the Making & Building visual layer from the documented Simulation state contract.
2. Coordinator assembles Simulation + Assets and runs the three smoke suites.
3. Any merge conflict that changes physical rules returns to World & Simulation for review.

Until then, the v0.5 physical core is considered complete for department handoff.
