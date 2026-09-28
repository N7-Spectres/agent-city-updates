# Communication & Perception — State

_Last updated: 2026-09-28_
_Current release: v0.5.0_
_Active milestone: v0.6.0 — Research & Discovery_

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
**Branch head:** `0fc75220610f52f9701b19df1a22caaaa60c341a`

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

`36420788364`

Passed:

- Python compile
- `tests/smoke_v040.py`
- `tests/smoke_v050.py`
- `tests/smoke_v050_communication.py`
- `tests/smoke_v060_communication.py`

The temporary branch CI workflow was removed after the green run.

## Current Integration Dependencies

### Simulation

Simulation should call Communication's validated ingress once per citizen who actually receives/observes a discovery or experiment result.

Communication does not decide experiment truth.

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
