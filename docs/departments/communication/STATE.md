# Communication & Perception — State

_Last updated: 2026-09-29_
_Current release: v0.8.7_
_Active milestone: v0.9 Stage 2 — Guided Practice & Competence-Safe Language_

## Mission

Model how information can physically reach a citizen.

Communication owns:

- speech and hearing
- direct observation / local presence
- face-to-face citizen information transfer
- last-known knowledge and information age/source
- transfer provenance
- visitor interaction availability semantics
- future physical communication systems only if the civilization actually invents and builds them

Core law:

> **A citizen only knows what information could actually have reached them.**

## Shipped Baseline

v0.5.0 includes:

- local citizen observation without remote live-state omniscience
- same-location citizen talk as a real physical job
- canonical stored citizen conversations
- nullable unique `citizen_conversations.source_job_id`
- talk completion only when the stored exchange exists
- failed/invalidated talk creates no false information transfer
- bounded social context that treats conversation content as claims rather than physical truth
- face-to-face visitor geography

Published v0.5.0 base:

`d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`

## v0.6 Communication Implementation

**Branch:** `communication/v0.6-knowledge-provenance`  
**Base:** shipped v0.5.0 commit `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`  
**Branch head:** `6a483fcc4d143606f3e401218002e06ae43076d1`

### Information receipt ledger

New `agent_city/provenance.py` adds Communication-owned `information_receipts`.

A receipt means:

> a specific piece of information actually reached a specific citizen through a specific mechanism at a specific time.

It is **not** global world truth and it is **not** a replacement for Memory.

Receipt fields include:

- `recipient_id`
- `subject_type`, `subject_id`
- `topic`, `value_text`
- `channel`
- `source_actor_id`
- `origin_event_type`, `origin_event_id`
- `transfer_event_type`, `transfer_event_id`
- `source_conversation_id`
- `observed_at_sim_minute`
- `received_at_sim_minute`
- `assertion_kind`
- `verification`
- unique `source_key`

Supported channels:

- `direct_observation`
- `survey_measurement`
- `experiment_result`
- `personal_experience`
- `face_to_face_claim`

Assertion kinds:

- `validated_observation`
- `speaker_claim`

Verification values:

- `unverified`
- `verified`
- `contradicted`

### Validated Simulation ingress

`record_validated_information(...)` is the Communication ingress for a validated physical discovery/result.

It requires a specific recipient and authoritative physical event reference. A Simulation discovery does not automatically become knowledge for all six citizens.

Validated observations enter as:

- `assertion_kind = validated_observation`
- `verification = verified`

### Face-to-face claims

Citizen dialogue generation now optionally emits structured claims alongside the durable raw exchange.

Claims are persisted only when:

- the physical source-linked conversation is valid
- the claim names the actual speaker
- the stored `value` is a verbatim sentence/clause found in that speaker's durable transcript

The other participant receives the claim as:

- `channel = face_to_face_claim`
- `assertion_kind = speaker_claim`
- `verification = unverified`
- source actor and canonical conversation ID retained

Questions, greetings, guesses, implications, or model-generated text not present in the transcript do not become receipts.

Retelling does not verify a claim.

### Legacy migration

Only physically unambiguous v0.5 knowledge is backfilled:

- completed survey job -> verified survey-completed receipt for the surveyor
- confirmed deposit with recorded discoverer/time -> verified deposit receipt for that discoverer

Legacy conversation summaries are **not** reverse-engineered into precise claim receipts.

### Model-facing context

Citizen planning, autonomous citizen dialogue, and visitor dialogue now receive bounded provenance-backed information.

Rules explicitly separate:

- verified observation/result
- unverified speaker claim
- social conversation summary
- current direct observation
- unknown remote state

Remote state remains unknown unless a real information path exists.

### Knowledge read model

Communication exposes:

`GET /api/knowledge/{citizen_id}`

This is a provenance-oriented per-citizen read model containing:

- bounded receipts
- source/time/age
- grouped location facts
- the citizen's current location as current direct observation

It never merges all citizens into one omniscient notebook.

For v0.6 UI, Memory's higher-level bounded consumer endpoints remain the preferred Citizen/Location knowledge surface; Communication's endpoint is the lower-level provenance view.

### Visitor availability states

`visit_access_payload(visitor, citizen_id)` now returns structured states:

- `available`
- `remote`
- `visitor_traveling`
- `citizen_traveling`
- `citizen_talking`
- `citizen_busy`
- `missing`

Talk counterpart resolution handles both initiator and target correctly.

This fixes the self-referential case such as:

> "Vale is currently speaking with Vale."

A co-located busy/talking citizen is no longer mislabeled as merely "Not at the same location."

Remote access is checked before exposing local busy/talk detail, so visitor status does not become a remote information leak.

`GET /api/visit/{citizen_id}` now exposes `status` and structured `availability`.

## Tests

Final hardened GitHub Actions run:

`36421263078`

Passed:

- Python compile
- `tests/smoke_v040.py`
- `tests/smoke_v050.py`
- `tests/smoke_v050_communication.py`
- `tests/smoke_v060_communication.py`

The temporary branch CI workflow was removed after the green run.

## Current Integration Dependencies

### Layered v0.6 knowledge architecture

1. **Simulation** owns physical truth, validated `discoveries`, and current validated `citizen_knowledge`.
2. **Communication** owns immutable receipt/transfer provenance in `information_receipts`, including unverified face-to-face claims.
3. **Memory** owns durable bounded retention/retrieval and citizen/location summaries.
4. **Assets** consumes safe bounded read models and structured availability, not hidden truth.


### Simulation

Simulation's final v0.6 branch owns:
- `agent_city/knowledge.py`
- `discoveries`
- `citizen_knowledge`
- `experiment_results`
- hidden world truth and experiment outcomes

Communication deliberately uses a separate module:
- `agent_city/provenance.py`

At integration time, Communication idempotently mirrors only recipient-local **verified** `citizen_knowledge` rows and persisted experiment results into receipt history. It never reads `world_properties` alone to manufacture knowledge.

This removes the need for Simulation to call Communication on every event and avoids a module-name collision.

The generic `record_validated_information(...)` ingress remains available for validated observations that do not naturally live in Simulation's discovery tables.

### Memory

Memory may ingest or reference `information_receipts` for durable bounded retrieval. It remains owner of retention/summary policy.

### Assets

Assets should:

- use Memory's bounded Citizen/Location knowledge APIs for normal knowledge UI
- use Communication's structured visit availability states for Visit UI
- never infer hidden Simulation truth from absence or raw admin state

## Current Communication Technology

There is still:

- no radio
- no network
- no telepathy
- no remote status channel
- no automatic global knowledge propagation

Future long-distance communication requires actual need, discovery, materials, fabrication/construction, and a physically existing mechanism.

## Status

The Communication v0.6 provenance/availability slice is implementation-complete and ready for coordinator integration/review.

Claim verification by later evidence is intentionally minimal in this slice: the ledger can represent `verified` / `contradicted`, but richer reconciliation/reliability behavior remains future depth.

## Session Close — 2026-09-28

Communication v0.6 work is closed for this session.

Final implementation:
- branch: `communication/v0.6-knowledge-provenance`
- head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- final green CI: `36421263078`

Completed this session:
- implemented recipient-local information receipts
- implemented verified observation/result vs unverified speaker-claim semantics
- required persisted claim text to be verbatim from the durable speaker transcript
- preserved canonical conversation/source-job integrity
- added Simulation knowledge/result synchronization without reading hidden truth directly
- separated Simulation `agent_city/knowledge.py` from Communication `agent_city/provenance.py`
- fixed visitor availability/talk-counterpart status
- preserved anti-omniscience in planner and visitor dialogue context
- handed stable contracts to Simulation, Memory, and Assets
- updated shared coordination to REVIEW

No department-owned implementation remains for the current Communication v0.6 slice.

Resume only if:
1. coordinator reports an integration conflict,
2. Assets reports a Visit/provenance contract mismatch,
3. Memory needs a provenance-mapping adjustment, or
4. a later milestone activates contradiction/reliability, overhearing, physical records, or long-distance communication.

Before resuming, read `COORDINATION.md`, this department's `INBOX.md`, then this `STATE.md`.


## Shipped v0.6.0 Integration

Communication v0.6 work is included in the published runtime:
`6092aeafd685a3ba4cb8e9d455e586771d3f6d26`.

The assembled release passed the full cross-department smoke suite. Coordinator integration preserved Simulation truth, Communication provenance, Memory bounded retrieval, and Assets safe presentation as distinct layers.

## v0.7 Autonomous Talk Reliability

**Branch:** `communication/v0.7-talk-reliability`  
**Base:** shipped v0.6.0 commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`  
**Branch head:** `61eecc4c047dd3fd22b71612251769a8cb456737`

### Root reliability problem

v0.6 generated the durable raw exchange and structured claim metadata in one strict Ollama JSON response.

That made the physical conversation unnecessarily fragile: a malformed claim list or nested schema problem could invalidate an otherwise good face-to-face exchange.

### v0.7 reliability model

Talk generation is now two-phase:

1. **Raw exchange**
   - generate only `initiator_text`, `target_text`, and `summary`
   - allow one retry for malformed/empty/incomplete structured output or transient Ollama failure
   - revalidate the physical source-linked talk
   - persist the durable conversation immediately

2. **Claim/provenance enrichment**
   - run only after the raw exchange exists
   - extract claim metadata from the already-stored transcript
   - projection is best-effort
   - malformed claim metadata, network failure, or claim persistence failure does **not** erase or invalidate the raw conversation

This preserves:

> **A real stored exchange is the information-transfer event. Claim extraction is enrichment, not existence.**

### JSON tolerance

Raw dialogue parsing accepts:

- a normal JSON object
- a JSON object wrapped in Markdown code fences
- a response containing one recoverable JSON object surrounded by incidental text

It still rejects:

- unparseable content
- missing/blank required dialogue fields
- fabricated fallback text

### Retry behavior

Normal raw dialogue generation gets at most two attempts.

The second attempt:

- keeps the same physical conversation/context
- lowers temperature
- increases output allowance slightly
- still requires a real model-generated exchange

No synthetic fallback transcript exists.

### Diagnostics

New Communication-owned table:

`talk_diagnostics`

Each diagnostic is keyed to `source_job_id` and records:

- simulation minute
- stage
- outcome: `success | retry | degraded | failure`
- concise code
- bounded detail

Representative codes:

**Generation**
- `ollama_network_failure`
- `ollama_http_failure`
- `ollama_response_malformed`
- `ollama_empty_response`
- `dialogue_malformed_json`
- `dialogue_schema_incomplete`
- `dialogue_generated`

**Physical/persistence**
- `physical_talk_invalid_before_generation`
- `physical_talk_invalid_before_persistence`
- `citizen_record_missing`
- `persistence_database_failure`
- `exchange_persisted`

**Claim enrichment**
- `claim_ollama_network_failure`
- `claim_ollama_http_failure`
- `claim_response_malformed`
- `claim_malformed_json`
- `claim_schema_incomplete`
- `claim_persistence_failure`
- `claim_projection_failure`
- `claims_projected`
- `claims_empty`

Diagnostic writes themselves are best-effort and may never cause a valid talk to fail.

### History behavior

The ordinary failed-talk History line remains concise and citizen-readable:

> conversation attempt ended without a recorded exchange

If a diagnostic failure code exists, Simulation adds a separate `diagnostic` History entry such as:

> Talk job #42 failed before durable exchange: ollama_network_failure.

This gives debugging signal without replacing the normal chronology message with implementation noise.

### Physical integrity preserved

A talk still becomes physically `complete` only when its `source_job_id` has a durable `citizen_conversations` row.

No conversation row:
- participants are released
- job becomes `failed`
- no information transfer is invented

### Test status

Final GitHub Actions run:

`36428495003`

Passed:

- Python compile
- v0.4 regression smoke
- v0.5 Simulation smoke
- v0.5 Communication smoke
- v0.5 UI smoke
- v0.6 Simulation smoke
- v0.6 Communication smoke
- v0.6 Memory smoke
- v0.6 UI smoke
- new `tests/smoke_v070_communication.py`

The temporary branch workflow was removed after the green run.

## v0.7 Status

The autonomous talk reliability slice is implementation-complete and ready for coordinator review/integration.

No v0.6 provenance or anti-omniscience rule was weakened.

## v0.7 Session Close — 2026-09-28

Communication v0.7 work is closed for this session.

Final implementation:
- branch: `communication/v0.7-talk-reliability`
- head: `61eecc4c047dd3fd22b71612251769a8cb456737`
- final green CI: `36428495003`

Completed:
- separated raw dialogue persistence from claim/provenance enrichment
- added one bounded retry for malformed/empty/incomplete raw dialogue or transient Ollama failure
- added tolerant JSON-object recovery without synthetic fallback dialogue
- added `talk_diagnostics` with stage/outcome/code/detail
- classified model/network/schema/physical/persistence/claim-enrichment failures separately
- kept diagnostic writes non-fatal
- fixed SQLite locking by reading completion diagnostics inside Simulation's existing transaction
- preserved source-linked talk completion integrity
- preserved all v0.6 provenance and anti-omniscience boundaries
- handed History/debug semantics to Assets
- moved Communication to REVIEW in `COORDINATION.md`

No Communication-owned implementation remains for the active v0.7 slice.

Resume only if:
1. coordinator reports an integration conflict,
2. Assets needs clarification on diagnostic History semantics,
3. post-release diagnostics show a dominant live failure mode worth tuning, or
4. a new milestone routes additional Communication work.

Before resuming, read `COORDINATION.md`, `communication/INBOX.md`, then this file.

## v0.8 Stage 1 — Grounded Visitor RP & Capability Language

**Branch:** `communication/v0.8-grounding-stage1`  
**Base:** shipped v0.7.0 commit `d81a85bf03b69b969532016f59bbbed2233949ee`  
**Branch head:** `a95e7af23eddaeb018bd6b2b6f19681a227e92af`  
**Final CI:** `36450386273`

### Grounding vocabulary

New `agent_city/grounding.py` gives citizen/visitor dialogue an explicit epistemic vocabulary:

- **known fact** — confirmed Simulation state, validated knowledge, or verified provenance
- **current observation** — what current physical context explicitly makes observable
- **reported claim** — visitor/citizen report attributed to its source
- **hypothesis / proposal** — explanation, interpretation, likely use, value judgment, or future plan not yet validated
- **validated capability / action** — only what authoritative runtime state actually supports

Personality and conversational style may improvise.

Factual nouns, physical explanations, capabilities, and outcomes require evidence.

### Visitor roleplay grounding

Visitor-described details remain visitor-reported until Simulation validates them.

Citizens may respond naturally using language such as:

- "what you're seeing"
- "the feature you described"
- "if that observation holds"
- "that's worth testing"

They must not confidently invent:

- material microstructure/chemistry/properties
- economic or market value
- scarcity
- terrain/landmark names or site history
- weather/atmospheric/environment causes
- physical tools/capabilities
- completed shared actions

A visitor may coin a descriptive name socially, but that does not create a mapped/validated physical place.

### Authoritative capability surface

Citizen dialogue now receives a Simulation-derived capability surface containing only:

- operational equipment physically owned/available at current location
- operational structures at current location
- validated learned processes
- Simulation legal actions available now

Concept art, UI visuals, appearance descriptions, and imagined accessories never create physical equipment or capability.

Broken equipment may still appear in a legal service/repair action, but it is not presented as operational capability.

### Shared activity boundary

A citizen may conversationally agree to:

- walk somewhere with the visitor
- inspect something together
- survey a point
- use a tool
- collect/build/test something

but agreement remains **intention/proposal only** unless Simulation creates a real physical action.

Stage 1 deliberately does not make chat an action/command interface.

The branch includes:

`docs/departments/communication/SHARED_ACTION_CONTRACT.md`

which defines the future Communication/Simulation boundary without implementing movement.

### Remote Seed Site storage leak fixed

Visitor chat previously injected exact live Seed Site storage quantities into every citizen prompt, including citizens physically away from Seed Site.

Stage 1 now exposes live storage quantities only while the citizen is physically at Seed Site.

Remote citizens may rely only on retained/communicated information that actually reached them.

### Stage 1 spatial grounding

Communication aligned to Simulation's final Stage 1 spatial contract:

- frame: `seed_site_local`
- units: meters
- +x east / +y north
- citizen position: `position_x_m / position_y_m`
- visitor position: `visitor_presence.x_m / y_m`
- validated observation anchor: `spatial_observations.id`

Dialogue may consume only the ordinary safe read model:

- safe meter positions
- citizen's own validated `spatial_observations`
- terrain/elevation/geology exposed by those observations
- stable deposit/material contact only when a validated observation exposed it

Communication never calls hidden `query_hidden_world` / `query_spatial_truth` for dialogue context.

It never exposes:

- planet seed
- hidden deposit richness
- hidden body geometry/axes
- unseen terrain
- raw hidden-query payloads

Coordinate decimal precision is not treated as observation/sensor precision. `radius_m` and source action/tool semantics define what was actually observed.

### Current Stage 1 physical limit

Simulation Stage 1 intentionally provides no legal arbitrary:

- `move_meter`
- `free_roam`
- `scan`

action.

Therefore "move one meter north with me" remains a conversational proposal in Stage 1.

Real visitor-linked movement/survey/exploration is a Stage 2 Simulation dependency.

### Prompt surfaces grounded

Stage 1 grounding is applied to:

- visitor-to-citizen chat
- autonomous citizen-to-citizen dialogue
- planner reason generation

Planner prompts explicitly reject unsupported properties, market-value claims, site history, weather/environment explanations, tools, and capability assumptions as reasons for action.

### Regression validation

Final GitHub Actions run `36450386273` passed:

- Python compile
- all v0.4 smoke
- all v0.5 smoke suites
- all v0.6 Simulation/Communication/Memory/UI smokes
- all v0.7 Simulation/Communication/Memory/Assets smokes
- `tests/smoke_v080_communication.py`

Temporary branch CI was removed after the green run.

## v0.8 Stage 1 Status

The independent Communication grounding/shared-action-boundary slice is complete and ready for coordinator review.

Stage 1 does **not** implement real shared visitor movement or scanning. That remains correctly deferred to Simulation-owned Stage 2 actions.

## v0.8 Stage 1 Session Close — 2026-09-28

Communication v0.8 Stage 1 is closed for this session.

Final implementation:
- branch: `communication/v0.8-grounding-stage1`
- head: `a95e7af23eddaeb018bd6b2b6f19681a227e92af`
- final green CI: `36450386273`

Completed:
- grounded visitor RP in explicit evidence status
- separated known fact, current observation, reported claim, hypothesis/proposal, and validated capability/action
- prevented unsupported confident material/property/value/terrain/weather/capability claims
- derived capability language from real operational runtime equipment/structures/processes/legal actions
- explicitly excluded concept-art/visual equipment from runtime capability
- removed remote live Seed Site inventory leakage
- grounded planner reasons and autonomous citizen dialogue
- consumed only safe Stage 1 meter coordinates and validated `spatial_observations`
- documented future visitor-linked shared physical action boundary
- aligned the contract to Simulation's final `seed_site_local` Stage 1 substrate
- routed the Stage 2 action-lifecycle dependency to World & Simulation
- moved Communication to REVIEW in `COORDINATION.md`

No Communication-owned Stage 1 implementation remains.

Resume only if:
1. coordinator reports an integration conflict,
2. Stage 2 is authorized and Simulation delivers visitor-linked action lifecycle fields,
3. Assets/Memory need clarification on grounding/provenance semantics, or
4. a new Communication milestone is routed.

Before resuming, read `COORDINATION.md`, `communication/INBOX.md`, then this file.

## v0.8 Stage 2 — Shared-Action Proposal Bridge

**Branch:** `communication/v0.8-shared-actions-stage2`  
**Unified Stage 1 base:** `017b417386f4f4e0f957dfb66285431223283739`  
**Branch head:** `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`  
**Final green CI:** `36457633293`

### Purpose

Face-to-face visitor dialogue may now create a structured shared-action proposal without turning chat into physical authority.

The chain is explicit:

1. durable visitor/citizen exchange exists
2. Communication recognizes a mutually proposed explicit local movement
3. Communication derives only the visitor's explicit meter/cardinal relative intent
4. Simulation validates and persists canonical `shared_activities.id`
5. Communication exposes a pending proposal object
6. visitor explicitly accepts
7. Simulation revalidates and creates the real `jobs.id`
8. only then may dialogue/UI say movement started
9. Simulation completion supplies `spatial_observations.id` and physical outcome

### Explicit target parsing

Communication parses only explicit local meter + cardinal-direction language, for example:

- "walk five meters east"
- "move 2 m north and 3 meters west"

Communication does **not** convert:

- "over there"
- pointing gestures
- "this way"
- vague landmark prose

into coordinates.

The LLM is used only as a boolean classifier for whether the durable exchange mutually proposes the already parsed request. It does not invent target coordinates, tools, or action type.

### Canonical identity chain

- `conversations.id` — durable visitor/citizen exchange source
- `shared_action_proposals.id` — Communication intent/UI projection
- `shared_activities.id` — canonical Simulation shared-activity identity
- `shared_activities.citizen_job_id / jobs.id` — real active movement job after acceptance
- `shared_activities.observation_id / spatial_observations.id` — validated completion evidence

Proposal and physical event IDs are intentionally distinct.

### Communication proposal read model

New table:

`shared_action_proposals`

Safe fields include:

- visitor / citizen
- visit ID
- source exchange ID
- action kind / label / objective
- safe target frame/x/y
- requested tool ID
- proposal status
- acceptance availability
- canonical Simulation activity ID
- active Simulation job ID
- Simulation status/progress/start/end
- observation IDs
- safe outcome

### Visitor API

Visit responses now include bounded proposal state.

Communication endpoints:

- `GET /api/visit/{citizen_id}/shared-actions`
- `GET /api/shared-actions/{proposal_id}`
- `POST /api/shared-actions/{proposal_id}/accept`
- `POST /api/shared-actions/{proposal_id}/reject`

`POST /api/talk` may return:

- `exchange_id`
- `shared_action_proposal` object or null

### Dialogue status grounding

Visitor chat receives:

- available shared-activity guidance
- current proposal/activity status

Language rules:

- `proposed` is not physically started
- acceptance without a real Simulation job is not physically started
- `started` requires real `jobs.id`
- `completed` requires Simulation completion
- observation/result claims require Simulation observation evidence

### Simulation integration

Communication is aligned directly to:

- `agent_city.exploration.propose_shared_activity`
- `agent_city.exploration.accept_shared_activity`
- `agent_city.exploration.shared_activity_payload`

Communication never mutates:

- participant coordinates
- Simulation jobs
- canonical `shared_activities`
- observations

### Canonical pre-start rejection

Simulation's final Stage 2 lifecycle provides:

`reject_shared_activity(conn, activity_id, visitor, now=...)`

Communication uses that Simulation-owned transition before marking its projection rejected/expired.

Canonical rejection is allowed only before physical start and creates no job, movement, or observation.

### Validation

GitHub Actions `36457633293` passed:

- Python compile
- all v0.4-v0.7 regression suites
- all unified v0.8 Stage 1 Simulation/Communication/Memory/Assets smokes
- `tests/smoke_v080_communication_stage2.py`

Temporary CI workflow was removed after the green run.

## Current Stage 2 Status

Communication proposal/accept/start/reject/status implementation is complete and ready for coordinator assembly.


## v0.8 Stage 2 Final Resolution

Simulation's final Stage 2 lifecycle now includes canonical pre-start rejection via:

`reject_shared_activity(conn, activity_id, visitor, now=...)`

and a separate physical start transition via:

`start_shared_activity(conn, activity_id, visitor, now=...)`

Communication now consumes the final lifecycle exactly:

1. durable visitor exchange
2. Communication explicit meter/cardinal intent parse
3. Simulation `propose_shared_activity`
4. Communication proposal projection
5. explicit visitor accept/start action
6. Simulation `accept_shared_activity` records acceptance without movement
7. Simulation `start_shared_activity` creates the real movement job
8. Simulation status/progress/complete data syncs into Communication
9. Simulation `reject_shared_activity` synchronizes pre-start visitor decline/expiry without movement

Final Communication branch:
- `communication/v0.8-shared-actions-stage2`
- head: `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- final green CI: `36457633293`

Final validation passed:
- compile
- all shipped v0.4-v0.7 regressions
- all unified v0.8 Stage 1 department smokes
- `tests/smoke_v080_communication_stage2.py`
- direct adapter signature checks for Simulation accept -> start -> reject

No Communication-owned Stage 2 dependency remains.

Communication is ready for coordinator assembly/review with Simulation, Memory, and Assets.


## v0.8 Stage 2 Session Close — 2026-09-28

This Communication work session is closed.

Completed:
- structured shared-action proposals sourced from durable visitor exchanges
- explicit meter/cardinal target parsing only
- canonical Simulation proposal validation
- explicit visitor acceptance
- separate Simulation accept and physical start transitions
- real job/status/progress/completion grounding
- canonical pre-start rejection synchronization
- safe Visit proposal/read API
- proposal/source handoffs to Memory and Assets
- full Stage 2 Communication regression coverage

Resume only for:
1. coordinator merge conflicts,
2. Assets integration questions about the proposal object,
3. Memory source-link clarification, or
4. a newly routed Communication milestone.

Before resuming, read `COORDINATION.md`, `communication/INBOX.md`, then this file.

## v0.9 Stage 1 — Recognition, Self-Assessment & Teaching Language

_Last updated: 2026-09-29_

**Branch:** `communication/v0.9-recognition-stage1`  
**Base:** published v0.8.7 `be617e6e870ec3f1914d76cdb85107a6efc294d7`  
**Final head:** `2b0b683086c03708d235fc2fefd08d64ed2d15d1`  
**Final green CI:** `36612304549`

### Purpose

Communication now converts source-backed continuity into natural perspective-safe language without creating a reputation, class, rank, or competence system.

New module:

`agent_city/continuity_language.py`

It consumes upstream v0.9 APIs when present and fails closed to no evidence when those modules are absent.

### Self-assessment

Own canonical Simulation `practice_events` may support statements about personal history.

Communication derives per-activity summaries such as:
- practice count
- completed count
- failed count
- latest practice/source

Language threshold:
- "I've done this several times" is permitted only with at least 3 real practice events for that activity.

This threshold is a language permission only.

It is not:
- XP
- level
- role
- class
- rank
- specialization
- expertise score
- competence guarantee

Self-assessment remains interpretation:
- "I feel more practiced"
- "I keep struggling with this"
- "I'm more comfortable with this now"

These are beliefs grounded in history, not objective Simulation capability truth.

### Perspective-safe recognition

Recognition of another citizen is derived only from Memory owned by the speaker.

Communication uses Memory's owner-scoped `causal_recall_snapshot(...)`, typically filtered by:
- counterparty
- optional activity facet

Communication does **not** read the other citizen's global `practice_events` and present those counts as speaker knowledge.

Therefore:
- Cato may recognize Bex only from information/experience that reached Cato.
- Noma cannot inherit Bex's practice history merely because Simulation stores it.
- repeated unverified reports remain unverified despite Memory reinforcement.

No universal reputation or expert/leader/title record is created.

### Teaching boundary

A citizen with source-backed practice may explain what they personally did, observed, tried, or learned.

Conversation/explanation alone creates:
- no learner practice event
- no competence gain
- no skill transfer
- no physical result
- no teaching credential

A future real teaching/guided-practice mechanism requires Simulation-owned action evidence.

### Persistent plans in dialogue

Communication may expose canonical Simulation plan state:
- plan ID
- status
- current intent
- next step
- unresolved question

Conversation may discuss/question/suggest changes.

Conversation does not itself:
- create
- revise
- pause
- resume
- abandon
- supersede
- complete

a canonical plan.

### Visitor continuity

Visitor familiarity/importance is grounded only in owner-scoped retained sources such as:
- visits
- durable exchanges
- completed shared activities

UI/account/coordinator status creates no social authority.

### Runtime integration

Citizen-to-citizen private context now includes:
- SELF-ASSESSMENT EVIDENCE
- PERSPECTIVE-SAFE RECOGNITION of the actual counterpart
- PERSISTENT PLAN DISCUSSION
- TEACHING / EXPLANATION BOUNDARY

Visitor dialogue includes:
- VISITOR CONTINUITY
- SELF-ASSESSMENT EVIDENCE
- PERSISTENT PLAN DISCUSSION
- TEACHING / EXPLANATION BOUNDARY

Safe debug/read endpoint:
- `GET /api/continuity-language/{citizen_id}`

This endpoint exposes evidence summaries and rule flags only. It exposes no recall score, reputation, XP, level, role, or expert score.

### Merge-order behavior

Communication's adapter dynamically imports:
- Memory `causal_recall_snapshot`
- Simulation `practice_snapshot_for`
- Simulation `plan_snapshot_for`

If an upstream module is absent, the adapter returns no continuity evidence rather than inventing it.

### Contract document

`docs/departments/communication/V090_RECOGNITION_TEACHING_CONTRACT.md`

### Validation

GitHub Actions `36612304549` passed:
- Python compile
- complete published v0.4 through v0.8.7 regression matrix
- `tests/smoke_v090_communication_stage1.py`

Temporary CI workflow was removed after the green run.

## Current v0.9 Communication Status

The recognition/self-assessment/teaching language layer is implementation-complete and ready for coordinator Stage 1 integration with Memory + Simulation.

No global reputation, competence score, skill-transfer mechanism, or authoritative title system was added.

## v0.9 Stage 1 Session Close — 2026-09-29

Communication v0.9 Stage 1 is closed for this session.

Final implementation:
- branch: `communication/v0.9-recognition-stage1`
- head: `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- final green CI: `36612304549`

Completed:
- perspective-safe recognition using speaker-owned Memory only
- own-practice self-assessment language from canonical physical practice history
- >=3 real practice events required before "I've done this several times" is permitted
- self-assessment remains interpretation rather than capability truth
- repeated unverified reports remain unverified despite recall reinforcement
- no universal reputation, expert/master/leader/rank/class/specialization identity
- teaching/explanation conversation creates no learner practice or competence
- canonical plans are discussable but read-only to Communication
- visitor continuity requires real retained interaction sources
- citizen-to-citizen and visitor dialogue contexts now consume the continuity-language layer
- safe continuity-language debug/read endpoint added
- Memory, Simulation, and Assets handoffs completed
- Communication moved to REVIEW in `COORDINATION.md`

No Communication-owned v0.9 Stage 1 implementation remains.

Resume only if:
1. coordinator reports an integration conflict,
2. Memory/Simulation merge changes the public recall/plan/practice interfaces,
3. Assets needs clarification on evidence vs interpretation presentation, or
4. a new v0.9 stage/milestone is routed.

Before resuming, read `COORDINATION.md`, `communication/INBOX.md`, this `STATE.md`, and `V090_RECOGNITION_TEACHING_CONTRACT.md`.

## v0.9 Recall-Bound Compatibility Resolution — 2026-09-29

Memory's final compatibility review identified that model-facing self-assessment and teaching still used the full durable Simulation practice ledger.

That is now fixed.

### Final split

**Objective/debug history only:**
- `own_practice_summary()`
- full Simulation `practice_events` ledger
- safe read/debug `GET /api/continuity-language/{citizen_id}`

**Model-facing autobiographical interpretation:**
- Memory `practice_recall_snapshot_for(...)`
- Memory `practice_recall_context_for(...)`
- bounded owner-scoped active recall with aging/salience applied

**Other-citizen recognition:**
- speaker-owned `causal_recall_snapshot(...)`
- source-backed recalled events only
- no numeric `reinforcement_count` exposed in natural-language evidence

### "Several times" final rule

Present model-facing wording such as "I've done extraction several times" is permitted only when active Memory currently recalls at least three source-backed practice experiences for that activity.

The durable archive may contain more events than the citizen currently recalls. Hidden/low-salience archive history must not be injected into present autobiographical language.

### Teaching final rule

Teaching/explanation context now uses active practice recall only.

A citizen may explain what they currently recall doing/observing/trying from real practice, but conversation still creates no learner practice or competence.

### Validation

Final compatibility CI:
- `36612304549` — PASS

Passed:
- Python compile
- full published v0.4 through v0.8.7 regression matrix
- corrected `tests/smoke_v090_communication_stage1.py`

Final branch:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`

Memory's blocking archive-vs-recall review is resolved.

Communication is ready for coordinator v0.9 Stage 1 integration.

## v0.9 Recall-Bound Final Session Close — 2026-09-29

Communication v0.9 Stage 1 is fully closed after Memory compatibility review.

Final branch:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- final compatibility CI `36612304549`

Final corrected semantics:
- full `practice_events` ledger is objective archive/debug history only
- model-facing self-assessment uses Memory bounded active practice recall
- model-facing teaching uses Memory bounded active practice recall
- "I've done this several times" requires at least 3 currently recalled source-backed practice experiences for that activity
- recognition of another citizen remains speaker-owned Memory only
- numeric `reinforcement_count` / `recall_score` never enter natural-language evidence
- repeated unverified reports remain unverified
- teaching conversation creates no learner competence
- canonical plans remain read-only to Communication

Cross-department handoffs are complete:
- Memory compatibility review marked resolved
- Assets notified that Communication recall-bound dependency is cleared
- coordinator integration gate reopened in `COORDINATION.md`

No Communication-owned v0.9 Stage 1 work remains.

Resume only for coordinator integration conflicts or a newly routed milestone.

## v0.9 Stage 2 — Guided Practice, Questions & Competence-Safe Language

_Last updated: 2026-09-29_

**Branch:** `communication/v0.9-guided-practice-stage2`  
**Integrated Stage 1 base:** `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`  
**Final head:** `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`  
**Final CI:** `36627237487` PASS

### Purpose

Communication now interprets real Stage 2 practice/competence/guided-practice evidence without creating expertise titles, reputation, hidden competence comparisons, or skill transfer from conversation.

Contract:
`docs/departments/communication/V090_STAGE2_GUIDED_PRACTICE_LANGUAGE_CONTRACT.md`

### Measured self-effect

New model-facing section:

`MEASURED PHYSICAL PRACTICE EFFECTS (SELF ONLY)`

Communication dynamically consumes Simulation `competence_snapshot(...)` for the speaker's own current state.

It exposes only bounded physical task-time effect, for example:
- extraction tasks currently receive about a 6% shorter duration from source-backed practice

It does not expose model-facing:
- weighted evidence math
- another citizen's competence snapshot
- hidden competence comparison
- expert/proficiency/rank labels

The measured effect is Simulation-owned physical state, not Memory and not social identity.

### Remembered experience remains separate

Stage 1 active-recall rules remain intact.

Present autobiographical self-assessment/teaching still use Memory:
- `practice_recall_snapshot_for(...)`
- `practice_recall_context_for(...)`

A measured physical effect may exist even when old practice is not currently recalled.

Communication must not reconstruct forgotten autobiographical history from the measured effect.

### Guided-practice Memory

Communication dynamically consumes Memory:
- `guided_practice_recall_snapshot_for(...)`
- `guided_practice_recall_context_for(...)`

Past teacher/learner roles are event-local.

Safe language:
- "Bex guided me through extraction practice."
- "I guided Cato through an extraction practice session."

Unsafe identity upgrade:
- mentor
- trainer
- expert
- master
- specialist
- leader
- senior/rank

### Current guided-practice availability

Communication may tell a citizen they can currently propose/start guided practice only when that citizen's own Simulation `possible_actions(citizen_id)` contains a legal `guided_practice` action.

This is a self-owned current capability surface.

Communication never queries another citizen's hidden/global competence ledger to tell the speaker who is "more experienced."

A legal guided-practice option proves only current physical action availability.

It does not prove a socially known competence comparison.

### Asking for help

New model-facing section:

`ASKING FOR HELP / EXPLANATION`

A citizen may ask another citizen about their experience even when they do not already know the answer.

Questions do not require a pre-existing competence claim.

Recognition claims still require speaker-owned Memory.

Safe:
- "Have you worked with this before?"
- "Could you show me your approach?"

Unsafe without source-backed recognition:
- "You're the best at this, so teach me."

### Ordinary explanation versus real guided practice

Ordinary conversation may transfer:
- claims
- instructions
- suggestions
- remembered experience

It creates no competence.

A real guided-practice session remains Simulation-owned:
- canonical `guided_practice_sessions.id`
- physical co-presence
- real timed job
- teacher/learner event roles
- one-use bounded guidance support on the learner's next matching real task

The guided session itself creates no learner practice event.

Only the learner's later real matching task creates new canonical practice evidence.

### Citizen-to-citizen dialogue

Private citizen dialogue context now includes:
- measured self physical effect
- active recalled guided-practice history
- legal current guidance options for the speaker
- help/question boundary
- existing self-assessment/recognition/teaching/plan sections

Strict rules preserve:
- no title/rank/reputation
- no ordinary-talk skill transfer
- no hidden other-citizen competence lookup
- guided-practice legality is not social recognition

### Visitor dialogue

Visitor chat receives:
- the citizen's own measured physical effect
- source-backed recalled guided-practice history
- no current citizen-to-citizen legal guidance-option list

Visitor explanation remains ordinary conversation and creates no visitor competence.

### Planner

Planner language now understands:
- `guided_practice` is a real physical legal action when Simulation exposes it
- the session itself creates no learner practice/competence
- ordinary talk/explanation creates no competence
- legal guidance does not create expert/mentor/trainer identity
- hidden/global competence data is not a social reason

Simulation remains authoritative for action start, duration, completion, guidance consumption, and later learner practice.

### Merge-order safety

If Stage 2 Memory/Simulation modules are absent:
- no measured competence effect is invented
- no guided-practice Memory is invented
- no current guided-practice option is invented

### Validation

CI `36627237487` passed:
- Python compile
- complete published v0.4-v0.8.7 regression matrix
- all four integrated v0.9 Stage 1 smokes
- `tests/smoke_v090_communication_stage2.py`

Temporary CI workflow was removed after the green run.

## Current v0.9 Stage 2 Communication Status

Implementation is complete and ready for coordinator Stage 2 integration.

No Communication-owned upstream dependency remains.


## Session Close — 2026-09-29 (Replacement Chat Recovery)

- Re-established direct GitHub access from the replacement Communication & Perception chat.
- Verified the live department inbox and shared coordination state on `main`.
- No new Communication-owned work, dependency, merge conflict, or downstream clarification request was present.
- v0.9 Stage 2 remains implementation-complete on `communication/v0.9-guided-practice-stage2` at `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`, CI `36627237487` PASS.
- Department status is unchanged: ready for coordinator integration; resume only under the existing Resume Rule.
