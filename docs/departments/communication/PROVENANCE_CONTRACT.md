# Communication provenance contract for v0.4

_Status: proposed interface; no runtime implementation in this repository branch._

## Verified audit (2026-09-28)

The checked-in `agent_city/planner.py` builds `citizen_context` from `snapshot()`. Its `Other citizens` string includes every other citizen's live `current_activity` and `location`, regardless of co-location. Its `Confirmed deposits known to the settlement` includes every discovered deposit without a per-citizen information path. Both expose remote facts to the planner. The file imports `agent_city.db` and `agent_city.simulation`, but those files, `agent_city/comms.py`, and the v0.3 conversation implementation are absent from the current default-branch tree. Documentation describes co-located talk and stored exchanges; the implementation and schema could not be inspected here.

## Minimum record

For each information item received by a citizen, retain:

- `recipient_id`, `subject_type`, `subject_id`, `topic`, `value`
- `channel`: `personal_experience`, `direct_observation`, or `face_to_face_claim`
- `source_actor_id` (nullable for direct environmental observation)
- `origin_event_id` (validated physical event when available), `transfer_event_id` (talk/exchange ID when communicated)
- `observed_at_sim_minute` (nullable for a claim with unknown original time), `received_at_sim_minute`
- `assertion_kind`: `validated_observation` or `speaker_claim`; `verification`: `unverified`, `verified`, or `contradicted`

An original timestamp reported by another speaker is part of the claim, not a trusted timestamp. Keep the archived event and transfer chain; Memory may derive a compact last-known view from these records. Do not turn a claim into verified world state merely because multiple citizens repeat it.

## Transfer rule

A validated same-location talk creates a transfer event with two participants, location, simulation time, and reference to the stored exchange. Extract only specific asserted facts actually expressed by a speaker; mark them as claims received by the listener. A mere conversation summary does not imply every fact in a speaker's memory was transferred. Both participants may remember their own utterances and what they heard, with separate recipient records. Third-party overhearing is deferred until a physical hearing model exists.

Direct observation uses a validated opportunity at the observer's current location and records only externally observable facts. It does not reveal private plans, energy, inventory contents, remote destinations, or internal state without an appropriate observable mechanism. Personal experience records the citizen's own validated actions and outcomes.

## Planner-facing view

Build context per citizen from their own state and legal actions, current validated local observations, and bounded Memory retrieval of their received records. A remote citizen's present location/activity is `unknown` unless a current permitted observation channel exists. An older record is phrased as `Last observed/heard at Day X... (source: ...)`; its age is calculated from current simulation time, and it never masquerades as live status. If no record exists, say `No known current status`. Shared settlement discoveries must be communicated or personally observed before entering an individual prompt. Legal action availability can use simulation truth, but labels/reasons must avoid leaking hidden remote information.

Visitor prompt context follows the same rule for face-to-face claims and observation. Admin/history UI may show wider truth if clearly outside the citizen's perspective; its content must not be copied into a citizen prompt.

## Integration and migration

- Communication owns eligibility and transfer records; Simulation supplies authoritative time, co-location, observable outcomes, and validated event IDs; Memory owns retention, retrieval, and interpretation.
- Add nullable provenance fields or a separate event table without rewriting old conversations as verified facts. Legacy summaries remain participant-accessible historical text with `unknown provenance`; do not backfill precise transfers that were never recorded.
- At decision time, recheck location/availability before talk, and derive local observations from the same authoritative snapshot/time. Revalidate before committing a transfer if participants moved during generation.
- Keep model context bounded and retain an immutable event chain in SQLite.

## Acceptance scenarios

1. Aris departs Seed Site. Bex at Seed Site cannot see Aris's live destination or activity; Bex can recall the last encounter with age/source.
2. Noma discovers resin alone. Cato cannot know the deposit until observing it or hearing a specific claim. A retelling stays a claim.
3. Noma tells Cato a plan while co-located. Cato knows what was said; Vale elsewhere does not. Vale learns only after a later valid transfer.
4. A claimed location conflicts with a later direct observation. Both records survive; the current direct observation takes precedence in the planner view without erasing the earlier claim.
5. A conversation is cancelled or invalidated by travel before completion; no transfer record is created.

## v0.6 Runtime Implementation

_Status: implemented on `communication/v0.6-knowledge-provenance`; pending coordinator integration._

The minimum contract is implemented as Communication-owned `information_receipts` in `agent_city/provenance.py`.

### Runtime mapping

Contract concepts map as follows:

- recipient -> `recipient_id`
- subject -> `subject_type` + `subject_id`
- fact/topic/value -> `topic` + `value_text`
- channel -> `channel`
- source actor -> `source_actor_id`
- authoritative physical source -> `origin_event_type` + `origin_event_id`
- communication transfer -> `transfer_event_type` + `transfer_event_id`
- canonical raw conversation -> `source_conversation_id`
- original observation time -> `observed_at_sim_minute`
- receipt time -> `received_at_sim_minute`
- assertion semantics -> `assertion_kind`
- verification -> `verification`

Every receipt also has a unique `source_key` for idempotent projection/migration.

### Validated physical ingestion

Simulation may create a receipt only through the validated ingestion surface for a specific recipient:

`record_validated_information(...)`

Communication does not query hidden Simulation truth and distribute it itself.

### Conversation claims

Claims are extracted only from a valid canonical stored face-to-face exchange.

The persisted `value_text` must appear verbatim in the attributed speaker's stored transcript. This is stricter than the original proposed contract and prevents model-generated claim metadata from introducing assertions that were never actually spoken.

Claims reach only the other participant and begin `unverified`.

### Consumer boundary

`GET /api/knowledge/{citizen_id}` exposes a bounded provenance view.

Memory may build higher-level bounded summaries/read models from receipts. Assets should normally consume Memory's safe consumer APIs rather than raw provenance internals.

### Still future

The receipt schema can represent contradiction/verification transitions, but automatic semantic reconciliation between old claims and later observations is not part of this slice.

Third-party overhearing also remains deferred.

## Final v0.6 Simulation Integration

Simulation's v0.6 implementation has its own `agent_city/knowledge.py`, which remains authoritative for validated `discoveries` and current `citizen_knowledge`.

Communication's implementation therefore lives in `agent_city/provenance.py`.

The layers are intentionally distinct:

- `discoveries` = validated physical discovery anchor
- `citizen_knowledge` = current possession/access to a validated Simulation discovery
- `information_receipts` = historical record of what reached a citizen, through what mechanism, from what source, and when
- Memory = bounded long-term retention/retrieval projection

Communication synchronizes only `citizen_knowledge.verification_state = 'verified'` into verified receipts.

A `reported` Simulation knowledge row is not upgraded to verified by synchronization.

`experiment_results` are also synchronized as real experience/result receipts. An inconclusive result verifies that the experiment was inconclusive; it does not imply an undiscovered hidden property.

This integration preserves the central rule: hidden world truth may exist without any citizen knowing it.
