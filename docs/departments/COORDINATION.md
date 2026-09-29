# Agent City — Department Coordination Board

_Last updated: 2026-09-29_

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

- [Assets & Interface] continuity runtime UI waits on coordinator Stage 1 integration and any remaining Memory UI-safe remembered-event projection; Communication recall-bound compatibility is resolved.

- [Coordinator / v0.9 Stage 1 Integration] Memory + Simulation + Communication Stage 1 branches are ready; combine them and run all three v0.9 smokes with the full regression matrix.

### READY


### REVIEW

- [Communication & Perception] v0.9 recall-bound recognition/self-assessment/teaching layer complete on `communication/v0.9-recognition-stage1` @ `2b0b683086c03708d235fc2fefd08d64ed2d15d1`; CI `36612304549` passed the full published regression matrix + corrected v0.9 Communication smoke.

- [Assets & Interface] v0.9 continuity UI/read-model audit complete; durable design at `docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`; no runtime UI started before safe integrated contracts

- [Memory & Social] v0.9 Stage 1 Causal Memory Spine + canonical practice retention + recall-bound practice interpretation API complete on `memory/v0.9-causal-memory-stage1` @ `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`; CI `36607115487` passed the full v0.4-v0.8.7 matrix + expanded v0.9 Memory smoke.
- [World & Simulation] v0.9 Stage 1 Persistent Plans + Practice Evidence complete on `simulation/v0.9-continuity-stage1` @ `6b027708512671d8c851723fb900cfa1e0fcac73`; final CI `36603570434` passed the full v0.4-v0.8.7 matrix + v0.9 Simulation smoke.

### DONE

- [Coordinator] v0.9 Civilization Continuity doctrine locked in `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`
- [Coordinator] v0.9 stage order locked: Causal Memory + Persistent Plans → Practice/Competence/Teaching/Recognition → Habits/Place Meaning/Social Customs
- [Coordinator] v0.9 department packets placed in Memory, Simulation, Communication, and Assets INBOX files
- [Coordinator] v0.8.7 Route Travel Visualization published from `be617e6e870ec3f1914d76cdb85107a6efc294d7`; final CI `36595479188` passed
- [Coordinator] v0.8.0–v0.8.6 release history remains complete and published

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


## CI Noise Reduction

Starting with v0.8.1, the release branch no longer runs the full release smoke matrix on every ordinary push.

Hotfix release workflow:
- branch: `release-v0.8.1`
- workflow commit: `c55eb76b89b35a660275ac97f095dcc4f511683e`
- release-smoke now runs only when `VERSION` changes
- stale overlapping release runs are cancelled by workflow concurrency
- department/integration work should use focused checks first
- coordinator performs the one definitive full release smoke at the final version bump before updating `update.json`

This keeps real failures visible while avoiding a mailbox full of intermediate integration noise.


## Assets v0.8.1 Release Locks

Coordinator release must preserve:

1. PR #19 is based on `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`.
2. All six citizens retain approved full-body + token WebP assets.
3. Full-body, bust, and token slots may be populated; semantic expression slots remain null until separately approved.
4. Optional equipment layers remain empty unless authoritative physical state later supplies attachment semantics.
5. Concept-art props never create equipment or capability.
6. Map zoom/focus is presentation-only and never mutates Simulation coordinates.
7. Region reset clears presentation center override and returns zoom to 1×.
8. Location hit targets remain generous but visually transparent; dot/label carry hover/focus indication.
9. Keyboard focus and `prefers-reduced-motion` behavior remain intact.
10. No hidden seed/deposit geometry/richness becomes visible.
11. Preserve `tests/smoke_v081_assets.py`.
12. Assets branch full regression `36467360376` is green; coordinator still performs the definitive full release run at VERSION bump.
13. No department updates `update.json` before the final release run succeeds.


## v0.8.1 Release Result

Published runtime:
- branch: `release-v0.8.1`
- immutable commit: `fa27c942d08a9a97a2dbca5e86ab77dc7b9b7cc0`
- final GitHub Actions run: `36468997929`
- result: **PASS**

The updater now targets this immutable commit.

Shipped:
- 12 runtime WebPs across six citizens
- full/bust/token profile wiring
- equipment layers left non-authoritative
- map zoom out / in / Region reset
- location click presentation focus
- transparent location hit targets with dot/label focus feedback
- improved cluster readability at closer zoom

No Simulation, Communication, or Memory semantics changed in v0.8.1.


## v0.8.2 Release Result

Published runtime:
- branch: `release-v0.8.2`
- immutable commit: `9a11b2bc21ba2338d6b231924036bf6d5935475c`
- final GitHub Actions run: `36473856852`
- result: **PASS**

Shipped:
- compact Energy/Integrity micro-bars on Home citizen cards
- exact percentages retained
- Citizen sheet uses the same live values
- long-term battery health/capacity is visually and semantically separated from current charge
- Home card geometry preserved

No Simulation, Communication, or Memory behavior changed.


## v0.8.3 Release Result

Published runtime:
- branch: `release-v0.8.3`
- immutable commit: `e4d216b133a18dc4c68e1bba1ceb0457e952efb6`
- final GitHub Actions run: `36478041248`
- result: **PASS**

Shipped:
- stable personality/voice profiles for all six founding citizens
- personality influences tone/preferences but not authority, rank, command rights, capability, or knowledge
- natural dialogue rules hide planner/scheduler/API vocabulary from ordinary speech
- visitor dialogue and citizen-to-citizen dialogue both consume the personality layer
- planner sees personality only as a soft bias and remains bound by legal actions, provenance, survival, and Simulation reality

No Simulation or Memory authority changed.


## v0.8.4 Release Result

Published runtime:
- branch: `release-v0.8.4`
- immutable commit: `ff78aab0e85331238eb67c989952a72499d1ed78`
- final GitHub Actions run: `36487822361`
- result: **PASS**

Shipped:
- claim-safe citizen conversation summaries
- deterministic guard against unsupported verification verbs in raw social summaries
- one retry when the model upgrades a claim; safe fallback on final failure
- intent remains intent until Simulation records the physical event

No Simulation or Memory authority changed.


## v0.8.5 Release Result

Published runtime:
- branch: `release-v0.8.5`
- immutable commit: `5b2395d7e7643a3d7ac9a82ac68090fc97b5f0b7`
- final GitHub Actions run: `36498819565`
- result: **PASS**

Shipped:
- 06:00–20:00 active autonomous cycle
- 20:00–22:00 wind-down
- 22:00–06:00 low-activity/recharge cycle
- repeated overnight charging to usable battery-health capacity
- critical-energy autonomous priority for charging or safe return
- preserved physical `possible_actions()` contract and active-job continuity
- charger named-location grounding
- dawn/day/dusk/night presentation from simulated time

No Memory or Communication authority changed.


## v0.8.6 Release Result

Published runtime:
- branch: `release-v0.8.6`
- immutable commit: `a72f96b763671f01c5a8aa0ba41d87f7eb6b9a09`
- final GitHub Actions run: `36591711494`
- result: **PASS**

Observed trigger:
- Iri at Resin Grove with 6% energy
- Seed Site route cost: 3.6%
- previous start validation also demanded 5% after arrival, creating a deadlock despite enough energy to physically reach the charger

Shipped:
- charger destination counts as the safety endpoint
- charger-bound trip may arrive below the normal reserve
- citizen must still afford real route cost
- ordinary away-from-charger reserve behavior is unchanged
- v0.8.5 critical-energy recharge priority takes over after arrival

Emergency admin principle:
- bug-created impossible states may receive minimal recovery intervention
- prefer fixing the rule so the existing save self-recovers
- direct state edits are last-resort repair, not visitor gameplay authority


## v0.8.7 Release Result

Published runtime:
- branch: `release-v0.8.7`
- immutable commit: `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- final GitHub Actions run: `36595479188`
- result: **PASS**

Shipped:
- route-travel citizen tokens visually advance along the actual known route
- screen position is proportional to authoritative travel-job progress
- compact travel percentage badge added
- remaining route distance included in token detail
- no Simulation, Communication, or Memory authority changed


## v0.9 Civilization Continuity Coordination Lock

Doctrine:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

Primary law:
> **Persistent behavior must have a traceable history.**

Dependency order:
1. Memory defines causal retained-history / bounded-retrieval / archive-vs-recall contract.
2. Simulation consumes that contract for persistent plan/event substrate and later bounded competence effects.
3. Communication consumes Memory + Simulation sources for perspective-safe self-assessment, recognition, and future teaching.
4. Assets consumes safe read models only and must not invent identity labels, expertise badges, relationships, habits, or customs.

Global anti-patterns:
- no RPG-style permanent classes
- no behavior-causing specialization labels
- no universal reputation score
- no skill from conversation alone
- no authored habits/customs without repeated evidence
- no fabricated memory used to justify present behavior
- no visitor favoritism from account/admin status
- no department publishes `update.json` during Stage 1 work

Stage 1 completion target:
a citizen can resume, revise, pause, abandon, or complete a meaningful persistent plan after unrelated actions/time have passed, with the current reason traceable to real retained history and without leaking that continuity to citizens who never acquired it.


## Simulation v0.9 Stage 1 Integration Locks

Coordinator and downstream implementation must preserve:

1. `citizen_plans.id` is the canonical persistent-plan identity.
2. A plan is citizen-owned intent continuity, not a command queue and not a competence label.
3. Plan creation requires at least one canonical `memory_event_id` owned by that citizen.
4. `plan_memory_sources` stores causal Memory references; plan reason text alone is not evidence.
5. `plan_transitions.id` preserves creation/revision/pause/resume/abandon/complete/supersede and real step history.
6. `jobs.plan_id` may reference only an active plan owned by the acting citizen.
7. A physical job outcome records `step_outcome` but never auto-completes the plan.
8. `practice_events.id` is one-to-one source-backed physical practice evidence from a real eligible `jobs.id`.
9. Completed and failed physical work may be practice evidence; talk/wait/agreement/proximity/UI never are.
10. Historical eligible jobs are backfilled idempotently into practice evidence without retroactive XP.
11. Stage 1 creates no competence score, XP, level, role, class, specialization, expert title, or reputation.
12. Memory remains owner of recall scoring/aging/reinforcement and `memory_event_facets`; Simulation must not duplicate that system.
13. Simulation consumes Memory public APIs `causal_recall_snapshot`, `causal_recall_context_for`, and `link_memory_event` after integration.
14. Standalone Simulation fails closed for autonomous new-plan candidate retrieval until Memory causal recall is present.
15. `sync_plan_memory_facets()` must survive integration so merge order cannot lose plan-pinned Memory facets.
16. Safe UI/read models may expose plan/practice history but not Memory recall scores as identity strength.
17. Preserve `tests/smoke_v090_simulation_stage1.py`.
18. No department publishes `update.json` during Stage 1.

## Required v0.9 Stage 1 Integration Tests

At minimum run together after Memory + Simulation integration:

- complete published regression matrix v0.4 through v0.8.7
- `tests/smoke_v090_memory_stage1.py`
- `tests/smoke_v090_simulation_stage1.py`
- Communication/Assets v0.9 focused tests when those branches add runtime/UI work

## Memory v0.9 Stage 1 Integration Locks

Coordinator and downstream implementation must preserve:

1. `memory_events` remains the durable source-backed archive.
2. `memory_event_facets` is an index/projection only; it does not create truth, identity, skill, habit, or reputation.
3. Active recall is bounded and computed separately from the durable archive.
4. Aging may reduce recall priority but must never rewrite/delete source history.
5. Reinforcement comes from multiple distinct related Memory events and affects retrieval priority only.
6. Repeated unverified claims remain unverified regardless of reinforcement count.
7. Recall is citizen-scoped; no global continuity packet exists.
8. Persistent plans should store stable initiating/revision `memory_event_id` references.
9. Old plan reasons may be pinned into active recall so they remain accessible after unrelated time/work.
10. Pinning preserves access, not obligation; plans remain revisable/pausable/abandonable.
11. Plan reason text alone is not causal evidence; the source Memory IDs are.
12. Preferred causal chain is `real source → memory_event_id → plan/source link → bounded recall → interpretation → intent → Simulation validation`.
13. No roles/classes/specialization fields may be introduced as behavior causes.
14. No skill/competence gain may come from conversation, agreement, proximity, UI, or concept art.
15. Internal recall score/reinforcement count must not become a citizen-visible reputation/memory-strength/identity metric.
16. Self-assessment and social recognition remain future perspective layers backed by this source history.
17. Hidden Simulation truth must never enter Memory merely because it exists.
18. Preserve `tests/smoke_v090_memory_stage1.py` in v0.9 Stage 1 integration testing.
19. `practice_events.id` is canonical physical practice evidence supplied by Simulation.
20. If the same physical job already has a durable Memory event, practice retention must reuse/link that event rather than duplicate it.
21. Otherwise one verified `simulation_practice_event` may be created for the citizen participant.
22. Practice facets improve recall only; they do not create XP, competence, role/class/specialization, title, or reputation.
23. Completed and failed eligible physical practice are both valid historical evidence; failure is not a permanent trait.
24. Model-facing self-assessment/teaching must consume `practice_recall_snapshot_for` / `practice_recall_context_for` or equivalent Memory active recall, not the full durable practice ledger.
25. Internal `recall_score` and `reinforcement_count` are retrieval machinery and must not appear as citizen-visible natural-language evidence.

### Memory v0.9 Stage 1 API

Internal Python interfaces:
- `causal_recall_snapshot(...)`
- `causal_recall_context_for(...)`
- `link_memory_event(memory_event_id, facet_kind, facet_value)`

No public HTTP recall-score API is part of Stage 1.

## Communication v0.9 Stage 1 Integration Locks

Coordinator integration must preserve:

1. Own physical `practice_events` may support self-description, but never XP, level, class, role, rank, specialization, or guaranteed competence.
2. Communication permits "I've done this several times" only when that citizen has at least 3 real practice events for the relevant activity.
3. Self-assessment is citizen interpretation, not objective capability truth.
4. Recognition of another citizen uses only Memory owned by the speaker; another citizen's global practice table is not speaker knowledge.
5. Recognition must preserve verification state; repeated unverified reports remain unverified even when reinforced in recall.
6. No universal reputation, expert badge, master/trainer/mentor/specialist title, leader rank, or authority weight is created.
7. Comparative claims such as "Bex has done this more than I have" require source-backed comparative evidence available to the speaker for both sides.
8. Conversation/explanation/teaching creates no learner practice, competence, skill transfer, or physical outcome.
9. A future real teaching mechanism requires Simulation-owned guided-practice/action evidence.
10. Canonical `citizen_plans` are read-only to Communication; discussion/suggestion does not create/revise/pause/resume/abandon/supersede/complete plan state.
11. Visitor familiarity/importance must descend from real retained visits, exchanges, or shared activities; UI/account/admin status creates no social authority.
12. Communication consumes Memory's `causal_recall_snapshot` as owner-scoped perspective evidence and Simulation's `practice_snapshot_for` / `plan_snapshot_for` as canonical own-history/current-plan sources.
13. `GET /api/continuity-language/{citizen_id}` is an evidence/debug read model, not a reputation/skill API.
14. Preserve `tests/smoke_v090_communication_stage1.py` in combined Stage 1 regression testing.
15. Preserve all prior provenance, anti-omniscience, natural-dialogue, and raw-exchange-first reliability rules.

Communication contract:
- `docs/departments/communication/V090_RECOGNITION_TEACHING_CONTRACT.md` on the Communication branch.

### Recall-bound compatibility resolution

Final Communication integration must additionally preserve:

- full Simulation `practice_events` ledger is objective archive/history/debug only
- model-facing self-assessment and teaching use Memory `practice_recall_snapshot_for(...)` / `practice_recall_context_for(...)`
- active recall aging/salience may omit durable practice from present autobiographical context
- "I've done this several times" requires at least 3 currently recalled source-backed practice experiences for that activity
- `recognition_context()` may consume speaker-owned causal recall but must not expose numeric `reinforcement_count`
- internal `recall_score` / `reinforcement_count` are retrieval machinery, never citizen-visible experience/reputation facts
- final Communication head: `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- final compatibility CI: `36612304549` PASS

