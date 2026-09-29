# Communication & Perception — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.5 conversation-history integrity slice ready

**Need / Result:**
Implemented and tested the v0.5 fix for chronology/conversation mismatch on `communication/v0.5-history-integrity`.

The root issue was that the physical talk job and the stored exchange were not source-linked. A talk could appear in chronology even when dialogue persistence failed.

New behavior:
- new autonomous exchanges store unique nullable `source_job_id`
- the physical talk is revalidated before conversation commit
- retries are idempotent for the same talk job
- no fabricated fallback exchange is stored when model generation fails
- talk completion succeeds only when the linked conversation exists
- missing exchange causes the talk job to fail instead of producing a false "finished talking" success
- stale text cannot be inserted after failure
- canonical `citizen_conversations.id` is preserved exactly for Memory

**Branch / commits:**
- base: `4181cbb69809205ae575b3f576836e5ca72c8dce` (release-v0.4.1)
- branch: `communication/v0.5-history-integrity`
- final branch head: `672f221c0a2e796ba30d685d2cad68a5552c8333`

**Files changed:**
- `agent_city/db.py`
- `agent_city/comms.py`
- `agent_city/planner.py`
- `agent_city/simulation.py`
- `tests/smoke_v050_communication.py`

**History / state interface:**
Each `snapshot()["citizen_conversations"]` row exposes:
- `id` — canonical conversation ID
- `source_type = "citizen_conversation"`
- `source_id = id`
- `transfer_event_id = id`
- `source_job_id` — physical talk job ID for new linked rows; nullable for legacy
- `sim_minute`
- `location_id`, `location_name`
- initiator/target IDs and names
- `initiator_text`, `target_text`
- `summary`

Successful talk-completion history includes `conversation #<id>`. Failed attempts explicitly say no exchange was recorded and do not create a conversation row.

**Testing:**
GitHub Actions run `36372479310` passed:
- compile
- existing v0.4 smoke
- new v0.5 communication-integrity smoke

The temporary branch-only CI workflow used for that run was removed afterward.

**Important constraints:**
- conversation claims remain claims
- `citizen_conversations.id` remains the canonical Memory source ID
- do not treat `source_job_id` as claim verification
- no radio/network/remote communication was added
- no release metadata or `update.json` was changed

**Next action:**
Coordinator can integrate/review this branch. Assets can consume the final History shape. Memory can keep its existing canonical source links and optionally use `source_job_id` as a supplementary physical anchor.

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.4 provenance contract and planner anti-omniscience patch

**Need / Result:**
The earlier anti-omniscience architecture and `PROVENANCE_CONTRACT.md` remain valid. The new v0.5 slice adds conversation-level physical source integrity but does not yet implement claim-level provenance extraction.

**Next action:**
Treat claim-level provenance as future depth unless reactivated by the coordinator.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.6 knowledge provenance + visit availability ready

**Need / Result:**
Implemented the Communication-owned v0.6 provenance layer on `communication/v0.6-knowledge-provenance`.

Delivered:
- per-citizen `information_receipts` ledger
- validated Simulation ingestion surface
- explicit verified observation vs unverified face-to-face claim semantics
- canonical conversation/source linkage preserved
- transcript-grounded claim extraction: persisted claim text must exist verbatim in the attributed speaker's stored exchange
- bounded provenance context for citizen planning and visitor/citizen dialogue
- `GET /api/knowledge/{citizen_id}` low-level per-citizen provenance view
- structured visitor availability states fixing self-referential talk status and busy-vs-remote confusion

**Branch / test:**
- base: `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- branch: `communication/v0.6-knowledge-provenance`
- head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- final hardened CI run: `36421263078`

Passed:
- Python compile
- v0.4 smoke
- v0.5 Simulation smoke
- v0.5 Communication smoke
- v0.6 Communication provenance/availability smoke

**Validated ingress for Simulation:**
`record_validated_information(recipient_id, subject_type, subject_id, topic, value_text, channel, origin_event_type, origin_event_id, observed_at_sim_minute, received_at_sim_minute=None, source_key=None)`

Accepted validated channels:
- `direct_observation`
- `survey_measurement`
- `experiment_result`
- `personal_experience`

**Visit states for Assets:**
- `available`
- `remote`
- `visitor_traveling`
- `citizen_traveling`
- `citizen_talking`
- `citizen_busy`
- `missing`

**Important constraints:**
- one discovery does not auto-populate all citizens
- retelling does not verify a claim
- conversation summary remains social continuity, not physical truth
- no remote communication technology was added
- no `update.json` or release metadata changed

**Next action:**
Coordinator integrates this branch with final Simulation/Memory v0.6 work. Simulation should use the validated ingress for actual discoverers/observers. Assets should use Memory's consumer knowledge APIs plus Communication's structured visit availability.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Final v0.6 Simulation/Communication layer alignment

**Need / Result:**
Simulation's final branch introduced `agent_city/knowledge.py` for validated discoveries and `citizen_knowledge`. Communication originally used the same module name, so the Communication branch was hardened before handoff:

- Simulation keeps `agent_city/knowledge.py`
- Communication now uses `agent_city/provenance.py`
- no filename collision remains

Communication provenance now idempotently synchronizes:
- verified recipient-local `citizen_knowledge` + `discoveries`
- persisted `experiment_results`, including inconclusive/repeated attempts as real experiences

It explicitly does **not** promote Simulation rows marked merely `reported` into verified receipts.

**Merged planner requirement:**
Keep both:
- Simulation's validated property/deposit knowledge
- Communication's provenance-backed verified facts and unverified claims

**Final branch / CI:**
- head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- CI: `36421263078` — compile + v0.4 + v0.5 Simulation + v0.5 Communication + v0.6 Communication all passed

**Next action:**
Coordinator can integrate Simulation and Communication without a module collision. Memory/Assets should consume their already-defined bounded/safe read models.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.6 session wrapped

**Need / Result:**
This work session is fully closed. Communication's v0.6 provenance/availability slice is implemented, tested, documented, and handed off.

**Final branch:**
- `communication/v0.6-knowledge-provenance`
- head `6a483fcc4d143606f3e401218002e06ae43076d1`
- final green CI `36421263078`

**Downstream handoffs already present:**
- Simulation INBOX: layered discovery/provenance integration contract
- Memory INBOX: information receipt/source semantics
- Assets INBOX: structured Visit availability/status contract
- COORDINATION: Communication in REVIEW with merge locks and required test matrix

**Important constraints:**
- preserve Simulation `knowledge.py` and Communication `provenance.py`
- preserve recipient-local knowledge boundaries
- preserve unverified claim semantics
- preserve face-to-face-only current communication
- do not publish `update.json`

**Next action:**
Stop Communication work. Resume only for coordinator integration feedback or a new milestone.



### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.7 autonomous talk reliability ready

**Need / Result:**
Implemented the v0.7 talk reliability slice on `communication/v0.7-talk-reliability`.

The main reliability change is two-phase processing:

1. generate + persist the raw conversation
2. run claim/provenance extraction afterward as best-effort enrichment

A claim parse/network/persistence failure can no longer erase an otherwise valid durable exchange.

**Diagnostics:**
New `talk_diagnostics` records per physical talk job:
- stage
- outcome
- concise code
- bounded detail

Hard failed talks keep the existing human-readable chronology line and may add a separate `diagnostic` History entry with the concise failure code.

**Failure classes now distinguished:**
- Ollama network/HTTP
- malformed Ollama response envelope
- empty response
- dialogue malformed JSON
- dialogue required-field/schema failure
- physical invalidation before generation/persistence
- raw database persistence failure
- claim extraction/persistence/projection degradation

**Reliability behavior:**
- raw dialogue gets at most one retry
- second attempt uses stricter/lower-variance generation settings
- JSON object recovery tolerates code fences/incidental wrapper text
- there is still no synthetic fallback transcript
- claim enrichment is non-fatal after raw persistence

**Physical integrity unchanged:**
A physical talk job only completes successfully if a source-linked `citizen_conversations` row exists.

**Branch / validation:**
- base: `release-v0.6.0` @ `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- branch: `communication/v0.7-talk-reliability`
- head: `61eecc4c047dd3fd22b71612251769a8cb456737`
- CI: `36428495003`

All shipped v0.4/v0.5/v0.6 smoke suites plus `tests/smoke_v070_communication.py` passed.

**Important constraints:**
- no fake dialogue
- diagnostics are not citizen knowledge
- claim extraction remains unverified provenance enrichment
- v0.6 anti-omniscience/provenance boundaries remain intact
- no `update.json` changes

**Next action:**
Coordinator can integrate/review. Assets may treat `history.category = "diagnostic"` as optional muted/debug information and should never render it as citizen dialogue.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.7 Communication session wrapped

**Need / Result:**
This work session is fully closed. Autonomous talk reliability is implemented, tested, documented, and handed off.

**Final branch:**
- `communication/v0.7-talk-reliability`
- head `61eecc4c047dd3fd22b71612251769a8cb456737`
- final green CI `36428495003`

**Downstream handoff already present:**
- Assets INBOX contains the `history.category = "diagnostic"` semantics and guidance not to render diagnostics as citizen dialogue
- `COORDINATION.md` contains the v0.7 Communication contract locks and required regression coverage

**Important constraints:**
- raw exchange before claim enrichment
- no fabricated fallback dialogue
- diagnostics are non-authoritative
- failed talk events remain distinct from real conversation records
- preserve v0.6 provenance/anti-omniscience rules
- do not publish `update.json`

**Next action:**
Stop Communication work. Resume only for coordinator integration feedback, measured post-release reliability tuning, or a newly routed milestone.



### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.8 Stage 1 grounded RP/capability layer ready

**Need / Result:**
Implemented the Communication Stage 1 foundation on `communication/v0.8-grounding-stage1`.

Delivered:
- explicit known fact / current observation / reported claim / hypothesis / validated capability language
- visitor-described physical details remain visitor reports until Simulation validates them
- unsupported confident claims blocked for material properties, economic value, terrain/site history, weather/environment effects, and nonexistent tools/capabilities
- authoritative citizen capability surface from runtime equipment/structures/learned processes/legal actions
- concept art and visual identity explicitly excluded from physical capability
- remote Seed Site live-inventory prompt leak removed
- planner reasons grounded against unsupported physical/economic/environment explanations
- safe Stage 1 meter-coordinate / validated spatial-observation context
- future visitor-linked shared-action boundary documented without inventing physical movement

**Simulation Stage 1 alignment:**
Communication consumes only:
- frame `seed_site_local`
- meter positions
- safe `spatial_observations.id` records

It never consumes raw hidden spatial query output.

Stage 1 has no arbitrary `move_meter`, `free_roam`, or `scan` action, so shared visitor movement/survey remains a proposal only.

**Contract document:**
- branch file: `docs/departments/communication/SHARED_ACTION_CONTRACT.md`

**Branch / validation:**
- base: `release-v0.7.0` @ `d81a85bf03b69b969532016f59bbbed2233949ee`
- branch: `communication/v0.8-grounding-stage1`
- head: `a95e7af23eddaeb018bd6b2b6f19681a227e92af`
- final CI: `36450386273`

CI passed the complete shipped v0.4-v0.7 regression chain plus `tests/smoke_v080_communication.py`.

**Important constraints:**
- chat agreement does not move citizens/visitors or create observations
- visitor claims remain claims
- safe spatial observations prove only their exposed fields
- coordinate decimals do not imply measurement precision
- no concept-art capability
- no radio/network/remote status channel
- no `update.json` changes

**Next action:**
Coordinator reviews Stage 1 contracts. Real visitor-linked physical movement/survey waits for a Simulation-owned Stage 2 action lifecycle.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.8 Stage 1 Communication session wrapped

**Need / Result:**
This Stage 1 work session is fully closed. Grounded visitor RP, capability language, safe spatial context, and the future shared-action boundary are implemented, tested, documented, and handed off.

**Final branch:**
- `communication/v0.8-grounding-stage1`
- head `a95e7af23eddaeb018bd6b2b6f19681a227e92af`
- final green CI `36450386273`

**Downstream handoffs:**
- World & Simulation INBOX contains the Stage 2 visitor-linked physical-action lifecycle request
- `COORDINATION.md` records Communication in REVIEW and the v0.8 Stage 1 contract locks
- Simulation's final safe spatial contract is fully reflected in Communication STATE/DECISIONS/BACKLOG
- Stage 1 review is not blocked by the deferred Stage 2 action request

**Important constraints:**
- visitor claims remain claims until validated
- concept art is not equipment
- hidden world queries are not dialogue evidence
- chat agreement is not physical movement/action
- preserve all v0.6/v0.7 provenance and talk-reliability rules
- do not publish `update.json`

**Next action:**
Stop Communication work. Resume only for coordinator integration feedback or Stage 2 authorization.


### 2026-09-28 — From: Communication & Perception — Status: blocked

**Subject:** v0.8 Stage 2 shared-action proposal bridge ready

**Need / Result:**
Communication's Stage 2 proposal/start/status bridge is implemented and fully regression-tested on `communication/v0.8-shared-actions-stage2`.

**Branch / validation:**
- unified Stage 1 base: `017b417386f4f4e0f957dfb66285431223283739`
- branch head: `7f40053233d0408b315ed6e9840267650503b63b`
- CI: `36456134638` — complete v0.4-v0.7 chain + all unified v0.8 Stage 1 smokes + `tests/smoke_v080_communication_stage2.py`

**Delivered:**
- durable Communication `shared_action_proposals` projection linked to visitor exchange
- explicit relative meter/cardinal visitor-intent parser
- LLM used only to classify mutual proposal intent, never to invent coordinates
- Simulation-owned proposal validation via `exploration.propose_shared_activity`
- explicit visitor acceptance
- physical start only through `exploration.accept_shared_activity`
- bounded status/progress/completion sync from `shared_activity_payload`
- dialogue context that distinguishes proposed vs started vs completed
- Visit API proposal list + accept/reject endpoints
- proposal expiration hooks on visitor leave/travel
- final source-chain handoffs to Assets and Memory

**Canonical source chain:**
1. `conversations.id`
2. `shared_action_proposals.id`
3. `shared_activities.id`
4. `jobs.id`
5. `spatial_observations.id`

**Remaining blocker:**
Simulation does not yet expose a canonical cancellation primitive for an unstarted `shared_activities.status='proposed'` row.

Communication intentionally fails closed on reject/expiry until Simulation can cancel the canonical proposal too. This prevents split-brain proposal state.

Requested primitive is already in World & Simulation INBOX:
`cancel_shared_activity(conn, activity_id, visitor, now=..., reason=...)`

**Important constraints:**
- proposal is not movement
- acceptance is not movement unless a real job ID exists
- completed exploration requires Simulation completion + observation evidence
- chat never mutates coordinates
- no hidden spatial query data enters proposal/UI/dialogue state
- no concept-art capability
- no `update.json` changes

**Next action:**
World & Simulation supplies the narrow cancellation primitive. Then Communication reject/expiry finalization can be considered fully integrated and coordinator assembly can proceed.


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.8 Stage 2 Communication session complete

**Need / Result:**
Communication Stage 2 is fully implemented, aligned to Simulation's final lifecycle, regression-tested, documented, and ready for coordinator assembly.

**Final branch:**
- `communication/v0.8-shared-actions-stage2`
- head `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- final green CI `36457633293`

**Final Simulation lifecycle consumed:**
- `propose_shared_activity`
- `accept_shared_activity`
- `start_shared_activity`
- `reject_shared_activity`
- `shared_activity_payload`

**Delivered Communication behavior:**
- proposal extraction only after durable visitor exchange
- only explicit meter/cardinal visitor movement becomes candidate coordinates
- Simulation validates/persists canonical `shared_activities.id`
- explicit visitor accept/start drives separate accept then physical start transitions
- dialogue/UI says started only with real `jobs.id`
- completed observation/result state only from Simulation
- visitor rejection/leave synchronizes through canonical Simulation pre-start rejection
- safe proposal/read model handed to Assets
- proposal/social/physical/evidence source chain handed to Memory

**Canonical source chain:**
1. `conversations.id`
2. `shared_action_proposals.id`
3. `shared_activities.id`
4. `jobs.id`
5. `spatial_observations.id`

**Integration note:**
Communication, Simulation, and Memory all modify `main.py`. Coordinator merge must preserve all endpoint/context surfaces and run the complete Stage 2 regression matrix.

**Important constraints:**
- proposal != acceptance != physical start != completion
- chat never mutates coordinates
- no hidden world truth enters Communication
- no concept-art capability
- preserve v0.7 raw-exchange-first reliability and all Stage 1 grounding/provenance rules
- no `update.json` changes

**Next action:**
Coordinator integrates Simulation + Communication + Memory + Assets and runs the complete v0.8 Stage 2 regression suite.


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** v0.9 recognition/self-assessment/teaching language layer ready

**Need / Result:**
Implemented the v0.9 Communication Stage 1 continuity-language layer on `communication/v0.9-recognition-stage1`.

**Final branch / validation:**
- base: published v0.8.7 `be617e6e870ec3f1914d76cdb85107a6efc294d7`
- head: `f266c333a1fe3afb1a744c9c48e3cc2dc1ab8c63`
- CI: `36607321183` PASS

**Delivered:**
- own-practice self-assessment language
- >=3 real practice events required for "done this several times"
- self-assessment explicitly interpretive, not objective capability
- perspective-safe recognition from speaker-owned Memory only
- no access to another citizen's hidden/global practice count
- reinforcement preserves claim verification state
- teaching/explanation gives no learner skill/practice
- canonical plan discussion is read-only from Communication
- source-backed visitor continuity
- safe continuity-language read model
- design contract `V090_RECOGNITION_TEACHING_CONTRACT.md`

**Runtime files:**
- `agent_city/continuity_language.py`
- `agent_city/comms.py`
- `main.py`
- `tests/smoke_v090_communication_stage1.py`

**Important constraints:**
- no universal reputation
- no expert/master/leader/rank/class titles
- no skill transfer from conversation
- no plan mutation from conversation
- no other-citizen global practice leak
- repeated unverified claims remain unverified
- no `update.json` changes

**Next action:**
Coordinator integrates Memory + Simulation + Communication v0.9 Stage 1 and runs the combined regression matrix. Assets may use the safe contracts for continuity UI but should not invent expertise/reputation badges.


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** v0.9 Communication Stage 1 session wrapped

**Need / Result:**
This work session is fully closed. Perspective-safe recognition, evidence-backed self-assessment language, teaching boundaries, and read-only plan discussion are implemented, tested, documented, and handed off.

**Final branch:**
- `communication/v0.9-recognition-stage1`
- head `f266c333a1fe3afb1a744c9c48e3cc2dc1ab8c63`
- final green CI `36607321183`

**Downstream handoffs complete:**
- Memory INBOX: recognition must use speaker-owned causal recall and preserve verification
- Simulation INBOX: own-practice/plan language contract; no competence score or runtime change requested
- Assets INBOX: evidence vs interpretation UI guidance; no expertise/reputation badges
- `COORDINATION.md`: Communication in REVIEW with v0.9 integration locks

**Important constraints:**
- practice history is evidence, not identity
- recognition is perspective, not reputation
- teaching conversation does not create competence
- plan talk does not mutate plan state
- visitor importance must be source-backed
- preserve all prior provenance/grounding/reliability rules
- do not publish `update.json`

**Next action:**
Stop Communication work. Coordinator should integrate Memory + Simulation + Communication Stage 1 and run the combined regression matrix. Resume Communication only for integration feedback or a newly routed v0.9 stage.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.

### 2026-09-28 — From: Communication & Perception — Status: blocked

**Subject:** Final handoff audit found two v0.5 integration gaps

**Need / Result:**
All finished department branches were inspected.

Communication is complete and tested, but the combined v0.5 packet is not yet merge-safe:

1. `simulation/v0.5-making-building` head `eadea56841469a29e8078f5eca23247b13317251` does not contain Communication's `source_job_id` conversation schema or talk-completion integrity logic. A naive Simulation merge would reintroduce successful chronology without a stored exchange.
2. `assets/v0.5-making-ui` head `da3b579bb42fb86a171470dd93946c01a80b0fc1` contains the layout/History slice but does not yet consume Simulation's new project/equipment state.

**Verified good handoffs:**
- Communication canonical conversation source remains `citizen_conversations.id`
- Assets' stored-conversation renderer is compatible with Communication's records
- Simulation exposes stable physical IDs suitable for Memory after merge: `projects.id`, completed `jobs.id`, `jobs.outcome`, `jobs.project_id`
- Simulation CI run `36372834945` passed independently
- Communication CI run `36372479310` passed independently

**Integration requirement:**
The coordinator must combine both schema/behavior sets and run both v0.5 smoke suites. Assets then needs the merged physical state contract to finish the Making & Building visuals.

**Important constraints:**
- do not resolve the conflict by dropping Communication's talk invariant
- do not invent project completion in Memory/UI
- do not publish until combined integration tests pass

**Next action:**
Coordinator integration, then one final Assets physical-state UI pass.
