# Agent City — Department Coordination Board

_Last updated: 2026-09-28_

This file is the shared project task board.

## Status Key

- **ACTIVE** — currently being worked
- **WAITING** — blocked on another department or coordinator integration
- **READY** — dependency or deliverable is ready for pickup
- **REVIEW** — department branch/work is complete enough for coordinator review
- **DONE** — finished and incorporated

## Current Board

### ACTIVE

_None._

### WAITING

_None._

### READY

_None._

### REVIEW

_None._

### DONE

- [Coordinator] v0.8.0 Living World assembled, versioned, regression-tested, and published from `a870982ba947fcc5af08ca190de396ae4308b645`; final CI `36462126434` passed the complete v0.4-v0.8 matrix
- [World & Simulation] v0.8 Stage 2 local exploration/shared physical activity integrated
- [Communication & Perception] v0.8 Stage 2 grounded shared-action bridge integrated
- [Memory & Social] v0.8 Stage 2 spatial/shared-exploration continuity integrated
- [Assets & Interface] v0.8 Stage 2 continuous map/shared-action UI/AssetQueue scaffold integrated
- [Coordinator] v0.8 Stage 1 assembled and regression-tested
- [Coordinator] v0.7.0 published from `d81a85bf03b69b969532016f59bbbed2233949ee`

## v0.8 Stage 1 Coordination Goal

Stage 1 establishes contracts and substrate before the larger Living World integration.

Order of authority:

1. Simulation defines seeded coordinate/world truth and stable physical subjects. **REVIEW**
2. Communication grounds what citizens/visitors may claim and defines conversational/shared-action boundaries. **REVIEW**
3. Memory retains only observations/claims that reached a citizen through valid sources. **REVIEW**
4. Assets renders only validated state and prepares asynchronous visual-generation infrastructure. **REVIEW**
5. Coordinator reviews Stage 1 interfaces before Stage 2.

The planned v0.7.1 progress/chat/RP polish is folded into v0.8.0.

Stage 1 is intentionally not the full v0.8 release.

## Simulation v0.8 Stage 1 Contract Locks

Coordinator and downstream departments must preserve:

1. `meta.planet_seed` is persistent hidden physical truth and never ordinary UI/LLM/Memory state
2. local frame `seed_site_local` uses meters, +x east, +y north, origin Seed Site
3. current local frame is a tangent plane compatible with later global lat/lon, not lat/lon itself
4. existing named locations/routes/deposits retain identity and are additively spatially anchored
5. hidden spatial queries are deterministic from seed + coordinate/chunk
6. nearby points vary coherently; scans are not independent random rolls
7. generated deposit bodies have stable IDs and physical extent
8. procedural deposit IDs are independent of discoverer/time
9. raw `generated_deposits`, hidden geometry, hidden richness, and raw query payloads remain hidden
10. `spatial_observations.id` is the stable validated spatial observation anchor
11. observation source-job ownership/range/travel legality remains Simulation-controlled
12. coordinate decimals do not imply sensor precision; `radius_m` + source action/tool define epistemic precision
13. existing route travel remains discrete in Stage 1: origin coordinate while traveling, destination coordinate on arrival
14. Stage 1 adds no scanner, free-roam move action, globe renderer, new communication technology, or arbitrary citizen technology
15. no department publishes `update.json`

## Safe Spatial Consumption Contract

### Assets

May consume:
- `state.spatial_frame`
- locations `x_m/y_m`
- citizens `position_x_m/position_y_m`
- structures/projects `x_m/y_m`
- visitor presence `x_m/y_m`
- `state.spatial_observations[]`

Must not infer continuous travel paths yet.

### Memory

May source:
- `simulation_spatial_observation`
- source ID = `spatial_observations.id`
- optional stable deposit subject `dep_*` or `gdep_*`

Must preserve `radius_m` and provenance and must never ingest hidden generated-body tables/seed.

### Communication

Visitor/citizen claims about unvalidated spatial facts remain claims.

Future shared physical activity must be a Simulation-owned action. Chat agreement alone does not move participants or produce observations.

## Required Stage 1 Integration Tests

At minimum preserve and run:

- all shipped v0.4-v0.7 regression suites
- `tests/smoke_v080_stage1.py`
- Communication Stage 1 smoke when complete
- Memory Stage 1 smoke if runtime ingestion is added
- Assets Stage 1 smoke

## Handoff Protocol

When Department A needs Department B:

1. Department A writes a concise request to Department B's `INBOX.md`.
2. Department A records itself as **WAITING** here if the dependency blocks progress.
3. Department B reads its INBOX at the beginning of its next work session.
4. Department B completes the work or records why it cannot.
5. Department B writes the result to its own `OUTBOX.md` and, when useful, directly to Department A's `INBOX.md`.
6. The main coordinator reviews the handoff and updates this board.

## Coordinator Rule

Departments own systems, not reality.

Cross-department integration must preserve:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

A green department branch is not sufficient if merging it would silently remove another department's invariant.

## Communication v0.8 Stage 1 Contract Locks

Coordinator integration must preserve:

1. visitor-described physical details remain attributed reports until validated
2. dialogue distinguishes known fact, current observation, reported claim, hypothesis/proposal, and validated capability/action
3. concept art/visual assets never create physical equipment or capability
4. capability language derives from operational runtime equipment/structures, learned processes, and legal Simulation actions
5. legal action availability means attemptability, not guaranteed result
6. remote citizens do not receive exact live Seed Site storage quantities
7. Communication consumes safe meter positions and validated `spatial_observations`, never raw hidden spatial queries
8. coordinate decimal precision does not imply sensor/epistemic precision
9. Stage 1 chat agreement never changes coordinates, creates jobs, or creates observations
10. real visitor-linked shared activity remains Simulation-owned Stage 2 work
11. preserve v0.7 raw-exchange-first talk reliability and all v0.6 provenance/anti-omniscience rules
12. preserve `tests/smoke_v080_communication.py` in Stage 1 integration testing

Stage 2 dependency is recorded in World & Simulation INBOX and does not block Stage 1 review.


## Memory v0.8 Stage 1 Integration Locks

1. Memory reads `spatial_observations`, never `planet_seed` or hidden `generated_deposits` geometry/richness.
2. `spatial_observations.id` is evidence identity; `deposit_id` is stable physical subject identity.
3. Same-body repeat encounters keep the same subject and are not automatically separate durable memories.
4. First encounters, new methods, materially improved precision, and explicit milestones may be retained.
5. Routine meter movement / passive scans without new information are suppressed.
6. Stored coordinate precision must never exceed observation `radius_m`.
7. Spatial memories remain per-citizen and do not create a global map memory.
8. `simulation_spatial_observation` stays separate from generic knowledge-fact retrieval.
9. Preserve `tests/smoke_v080_memory.py` during Stage 1 coordinator integration.


## v0.8 Stage 1 Coordinator Review Result

Stage 1 handoff review is complete.

Reviewed branch heads:
- Simulation: `simulation/v0.8-seeded-world-stage1` @ `7473b6612ea23cf8d22b31176149da188476690e`
- Communication: `communication/v0.8-grounding-stage1` @ `a95e7af23eddaeb018bd6b2b6f19681a227e92af`
- Memory: `memory/v0.8-spatial-knowledge-stage1` @ `086e4c2e192b7a22a36d26be8288e01abfd1d197`
- Assets: `assets/v0.8-visual-stage1` @ `af2e058780103755360d143ca964855145e2254a`

Review findings:
- no direct file-overlap conflict exists between the four Stage 1 implementation slices that would obviously prevent integration
- Memory's spatial-observation field assumptions match Simulation's final `spatial_observations` schema and stable `deposit_id` / `radius_m` semantics
- Communication consumes only Simulation's safe spatial read model and keeps hidden seed/body truth out of prompts
- Assets correctly deferred continuous travel rendering and will not infer intermediate positions from Stage 1 coordinates
- Assets Stage 1 branch has static/smoke assertions but still needs the coordinator's combined release-style CI run after all branches are assembled
- Stage 2 must not start from separate department branches; first create and validate one combined Stage 1 integration base

Stage 1 review verdict:
**READY FOR COMBINED INTEGRATION TESTING.**

This is not yet a v0.8 release and does not authorize Stage 2 by itself.


## Simulation v0.8 Stage 2 Contract Locks

Coordinator integration must preserve:

1. `jobs.id` remains the physical authority for active local/shared movement.
2. `state.citizens[].local_movement` is server-derived from stored start/target/time fields; UI may smooth only that exact segment.
3. terrain affects duration/energy internally without exposing hidden seeded terrain merely because it influenced cost.
4. local/shared movement must preserve coordinate-based return-energy reserve.
5. face-to-face talk/Visit and local infrastructure use remain meter-proximity aware.
6. baseline walk/inspect observations use `detail_level='baseline'`, `material=NULL`, and `geology_class='unclassified'`.
7. `spatial_observations.id` is evidence identity; `deposit_id` is stable subject identity.
8. `shared_activities.id` is canonical Simulation shared-event identity; Communication proposal IDs remain separate intent/projection identities.
9. Simulation shared lifecycle separates `proposed`, `accepted`, `active`, `complete`, and pre-start `rejected`.
10. acceptance alone never creates movement; only the separate Simulation start transition creates `citizen_job_id`.
11. canonical rejection is allowed only before physical start and creates no job, coordinate change, or observation.
12. proposal source visit/exchange ownership and requested runtime equipment are validated by Simulation.
13. concept art never satisfies tool capability.
14. successful shared completion moves both participant positions and creates one linked safe observation.
15. legacy route compatibility is preserved for old location-only records, while real Stage 2 local offsets must return to the landmark before route departure.
16. hidden planet seed/generated body geometry/richness remain hidden.
17. preserve `tests/smoke_v080_stage2.py` in assembled Stage 2 regression testing.
18. no department publishes `update.json`.

## Required v0.8 Stage 2 Integration Tests

At minimum run together after merge:

- all existing v0.4-v0.7 regression suites
- all four v0.8 Stage 1 department smokes
- `tests/smoke_v080_stage2.py`
- `tests/smoke_v080_communication_stage2.py`
- `tests/smoke_v080_memory_stage2.py`
- `tests/smoke_v080_assets_stage2.py`

## Memory v0.8 Stage 2 Integration Locks

Coordinator integration must preserve:

1. Current authoritative spatial grounding and retained historical exploration Memory are separate prompt sections.
2. The 250 m nearby-memory selection radius is a relevance window, not epistemic precision.
3. Observation precision remains the source observation's `radius_m`.
4. `spatial_observations.id` remains physical evidence identity; stable `deposit_id` remains subject identity.
5. Repeat observations remain salience-bounded; movement ticks do not become memories.
6. Completed shared exploration Memory uses `source_type='simulation_shared_activity'` and `source_id=shared_activities.id`.
7. A shared exploration memory is created only for `status='complete'`, `outcome='success'`, non-null completion time, and linked observation.
8. Communication proposal/acceptance records remain intent/provenance and never substitute for physical completion.
9. The participating citizen may retain the event; bystanders do not receive it automatically.
10. Visitor identity plus source visit/exchange/job/observation IDs remain metadata for explainable continuity.
11. The linked spatial observation remains a separate evidence event from the shared social experience.
12. `simulation_spatial_observation` and `simulation_shared_activity` remain excluded from generic research/location knowledge facts.
13. Preserve Memory's `GET /api/memory/spatial/{citizen_id}` consumer view.
14. Memory and Communication both modify `main.py`; merge resolution must preserve both Communication shared-action lifecycle context and Memory retained/shared-exploration context.
15. Preserve `tests/smoke_v080_memory_stage2.py` in the assembled Stage 2 regression suite.
16. Never expose `planet_seed`, hidden generated-deposit geometry/richness, or infer exploration from chat.

## Communication v0.8 Stage 2 Contract Locks

Coordinator integration must preserve:

1. `conversations.id` is the durable social exchange source.
2. `shared_action_proposals.id` is Communication intent/UI projection, not physical truth.
3. `shared_activities.id` is the canonical Simulation shared-activity identity.
4. `jobs.id` is the real active physical movement job after explicit acceptance.
5. `spatial_observations.id` is validated exploration evidence at completion.
6. Communication derives candidate local targets only from explicit meter + cardinal visitor language.
7. Pointing, "over there", "this way", concept art, and hidden world truth do not become coordinates.
8. Simulation validates/persists the canonical proposal before Communication exposes a structured proposal.
9. Proposal state does not mean movement started.
10. Explicit visitor acceptance must succeed through Simulation and return a real job before dialogue/UI says started.
11. Completed exploration language requires Simulation completion and evidence IDs.
12. Communication never mutates participant coordinates, Simulation jobs, canonical activities, or observations.
13. Reject/expiry may not diverge from Simulation canonical proposal state; cancellation must be Simulation-owned.
14. Preserve Stage 1 grounding, v0.7 raw-exchange-first reliability, remote-store privacy, and all provenance boundaries.
15. Preserve `tests/smoke_v080_communication_stage2.py` in assembled Stage 2 regression testing.

Final dependency resolution:
- Simulation provides canonical pre-start reject for `proposed`/`accepted` rows with no job, movement, or observation.
- Communication now consumes and tests the final accept -> start -> reject lifecycle. No Communication Stage 2 dependency remains.


## Assets v0.8 Stage 2 Integration Locks

Coordinator integration must preserve:

1. Meter-space rendering consumes only safe Simulation spatial state.
2. +x is east and +y is north in `seed_site_local`.
3. Local-focus viewport may change camera scale/center but never physical coordinates.
4. Citizen local movement uses server-derived current x/y plus the Simulation-defined start/target segment only.
5. Browser smoothing is presentation-only and must respect `prefers-reduced-motion`.
6. Visitor shared movement uses authoritative visitor presence; chat agreement alone never moves the visitor.
7. Communication proposal ID, Simulation shared-activity ID, and Simulation job ID remain distinct.
8. Proposed/accepted intent must not look physically active.
9. Active presentation requires a real `simulation_action_id`.
10. Canonical rejection creates no movement path/marker.
11. Observation markers require a real `spatial_observations.id`.
12. `radius_m` communicates observation uncertainty; coordinate decimals do not imply greater precision.
13. Baseline observation UI must not reveal material or classified geology.
14. Assets must never consume `planet_seed`, hidden `generated_deposits`, hidden body geometry, or richness.
15. Citizen concept art still does not create equipment/capability.
16. Runtime-ready citizen art is absent; keep asset slots empty until approved source files exist.
17. `agent_city/asset_worker.py` and `data/asset_worker.db` are presentation infrastructure only and must never mutate Simulation truth.
18. No Blender or 3D generator dependency is required for v0.8.
19. Preserve `tests/smoke_v080_assets_stage2.py` in the final Stage 2 regression matrix.
20. No department publishes `update.json`.


## v0.8 Stage 2 Coordinator Handoff Review

All four department branches are now complete and ready for combined integration.

Final branch heads:
- Simulation: `simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`
- Communication: `communication/v0.8-shared-actions-stage2` @ `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- Memory: `memory/v0.8-exploration-stage2` @ `306a9ef4329ab81afa5912846333a1d9782ee9be`
- Assets: `assets/v0.8-exploration-ui-stage2` @ `7f5294efaab738b44af116514a65d22478851ad0`

Review notes:
- all four branches are ahead of the unified Stage 1 base and none are behind it
- Simulation owns physical movement/shared activity/observation truth
- Communication proposal IDs remain distinct from Simulation activity/job IDs
- Memory completion memories require real completed Simulation shared activities and linked observations
- Assets renders only authoritative movement/proposal/observation state
- Communication and Memory both modify `main.py`; coordinator merge resolution must preserve both shared-action lifecycle context and bounded exploration-memory context
- Assets branch CI `36460454385` passed Stage 1 + Stage 2 Assets smoke and AssetQueue lifecycle checks

Verdict:
**READY FOR COMBINED STAGE 2 INTEGRATION TESTING.**

This is not yet the published v0.8.0 release.


## v0.8 Stage 2 Integration Result

Combined Stage 2 integration is complete.

Unified runtime:
- branch: `release-v0.8.0`
- commit: `022f7655e9e958e3c35866d90679166a5b1c21e6`
- GitHub Actions: `36461596122`
- result: **PASS**

The full assembled matrix passed:
- Python compile
- JavaScript syntax
- v0.4 regression smoke
- all v0.5 smoke suites
- all v0.6 smoke suites
- all v0.7 smoke suites
- all four v0.8 Stage 1 smokes
- v0.8 Stage 2 Simulation smoke
- v0.8 Stage 2 Communication smoke
- v0.8 Stage 2 Memory smoke
- v0.8 Stage 2 Assets/UI smoke

Integration preserved the explicit identity chain:
- conversation/exchange = social source
- Communication proposal = intent/UI projection
- Simulation shared activity = canonical physical shared event
- Simulation job = active physical movement
- spatial observation = validated exploration evidence

No v0.8 release metadata or `update.json` publication has occurred yet.


## v0.8.0 Release Result

Published runtime:
- branch: `release-v0.8.0`
- immutable commit: `a870982ba947fcc5af08ca190de396ae4308b645`
- final GitHub Actions run: `36462126434`
- result: **PASS**

The updater may now target this immutable commit.

No additional v0.8 department work remains open.
