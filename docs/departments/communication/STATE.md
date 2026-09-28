# Communication & Perception — State

_Last updated: 2026-09-28_
_Current release: v0.7.0_
_Active milestone: v0.8.0 Stage 1 — Living World Foundations_

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
**Branch head:** `7f40053233d0408b315ed6e9840267650503b63b`  
**Final green CI:** `36456134638`

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

### Remaining blocker: canonical proposal cancellation

Simulation currently lacks a cancellation/rejection primitive for an unstarted canonical `shared_activities.status='proposed'` row.

Communication therefore fails closed:

- it does not mark a proposal rejected/expired if Simulation still reports the canonical proposal as proposed
- visitor rejection/leave needs Simulation to cancel the canonical row first

Requested Simulation primitive:

`cancel_shared_activity(conn, activity_id, visitor, now=..., reason=...)`

This blocker affects reject/expiry finalization only. Proposal creation, explicit acceptance, active status/progress, completion and observation linking are implemented/tested.

### Validation

GitHub Actions `36456134638` passed:

- Python compile
- all v0.4-v0.7 regression suites
- all unified v0.8 Stage 1 Simulation/Communication/Memory/Assets smokes
- `tests/smoke_v080_communication_stage2.py`

Temporary CI workflow was removed after the green run.

## Current Stage 2 Status

Communication proposal/start/status implementation is ready.

Communication remains **WAITING** only on Simulation's canonical proposal-cancellation primitive before reject/expiry can be considered fully integrated.
