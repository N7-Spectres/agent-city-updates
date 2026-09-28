# Communication & Perception — Decisions

## Information Travel Rule

> **A citizen only knows what information could actually have reached them.**

Information can currently arrive through:

- direct observation at the same location
- face-to-face conversation
- personal experience
- persistent memory of those experiences

Future mechanisms may include physical records or invented signaling systems.

## No Free Remote Communication

Do not grant radios, phones, networks, telepathy, or live status feeds.

If long-distance communication appears, it must come from:

1. a real citizen need
2. relevant discovered knowledge
3. available materials/components
4. a valid fabrication/construction process
5. a physically existing communication system

The civilization may invent something other than radio.

## Last-Known Knowledge

Remote status should be represented as last-known information when appropriate.

Example:

> "Last I heard, Cato was surveying Resin Grove."

Not:

> "Cato is surveying Resin Grove right now."

unless the speaker has a real current information path.

Age is derived from simulation time and the receive/observe timestamp. A last-known record never silently upgrades itself to live truth.

## Claims Are Not Physical Truth

Information communicated by another citizen is a speaker claim unless independently verified through an authoritative physical event or direct observation.

Repeated retelling does not convert a claim into truth.

## Direct Observation

Physical co-location allows ordinary observation, but observation should not automatically expose hidden internal state.

Direct observation may expose externally visible presence and locally observable physical facts. It does not automatically reveal private plans, internal motives, energy, inventory contents, or remote destinations.

## Planner Boundary

A citizen planner may receive:

- that citizen's own validated state
- current local observations that the citizen could physically perceive
- bounded remembered information that reached that citizen through a valid mechanism
- legal actions from Simulation

It must not receive another citizen's live remote location/activity or globally discovered resources merely because the simulation knows them.

Simulation may use hidden truth to decide action legality, but human-readable labels/reasons supplied to the planner must not leak that hidden truth.

## Canonical Conversation Source

`citizen_conversations.id` is the canonical immutable source ID for a stored citizen-to-citizen exchange.

Existing Memory references using:

- `source_type = 'citizen_conversation'`
- `source_id = citizen_conversations.id`

must remain valid.

Any later transfer/provenance layer must map back to this canonical raw conversation source rather than replacing or renumbering it.

## Physical Talk Link

For new source-linked autonomous conversations:

- `citizen_conversations.source_job_id` references the physical `talk` job
- the field is nullable for legacy conversations
- when present, it is unique
- retries for the same physical talk return/reuse the same conversation record rather than creating duplicates
- a conversation may only be committed while the matching talk job and co-location are still valid

Do not retroactively invent a `source_job_id` for legacy rows when the physical source cannot be established unambiguously.

## Talk Completion Integrity

A physical `talk` job must not be recorded as successfully completed unless a source-linked stored conversation exists.

If the talk reaches its due time without that record:

- release the participants
- mark the job failed
- record that the attempt ended without a recorded exchange
- do not create a conversation or information-transfer record afterward from stale generated text

This preserves the boundary:

> **No stored information transfer without a real, valid face-to-face event.**

## Generation Failure

Model/network/JSON failure must not be converted into invented fallback dialogue and persisted as though the citizens actually said it.

A failed generation may result in a failed conversation attempt, but it does not create remembered claims.

## Memory Projection Boundary

The raw stored conversation is the durable communication source.

Memory is a derived projection. If Memory projection temporarily fails, that must not erase or invalidate the durable conversation record. Its idempotent migration/backfill can repair the projection later.

## Provenance Record

The deeper provenance contract remains defined in `PROVENANCE_CONTRACT.md`.

Important distinctions remain:

- `personal_experience`
- `direct_observation`
- `face_to_face_claim`
- `validated_observation` versus `speaker_claim`
- `unverified`, `verified`, and `contradicted`

Legacy conversation summaries remain participant-accessible historical text with unknown claim-level provenance. Do not fabricate precise fact transfers retroactively.

## Ownership Boundary

Communication determines what information can move.

Simulation determines what physically happened.

Memory determines how communicated/observed information persists and how bounded retrieval is presented later.

## Provenance Contract Authority

Until replaced by a later explicit architecture decision, `PROVENANCE_CONTRACT.md` is the Communication-owned interface for deeper information provenance.

Do not weaken the planner boundary to compensate for missing memory/provenance plumbing. Unknown remote state must remain unknown rather than falling back to simulation-global truth.

## v0.5 Integration Gate

A v0.5 integrated runtime is not acceptable if merging Simulation reintroduces the old conversation mismatch.

The integrated `db.py` / `simulation.py` must preserve **both** departments' physical schema additions:

- Simulation: equipment/projects/project materials/job outcomes/coordinates/structure placement
- Communication: nullable unique `citizen_conversations.source_job_id` and talk completion validation

Required combined invariant:

> A `talk` job may be physically complete only when its real stored conversation exists.

If no source-linked conversation exists at due time, the talk job fails and no information transfer is invented.

Combined integration testing must run both Simulation's v0.5 physical smoke coverage and Communication's v0.5 conversation-integrity smoke coverage before release.

## v0.6 Information Receipt Authority

Communication's minimum durable provenance primitive is an **information receipt**.

A receipt records that one specific citizen received one specific piece of information through one real mechanism. It does not assert that the information is globally true unless its assertion/verification fields say it came from an authoritative validated observation.

This layer remains separate from:

- Simulation hidden world truth
- Memory's retention/retrieval projections
- UI presentation

## Validated Versus Claimed Knowledge

Simulation-grounded observation, survey measurement, experiment result, or personal physical experience may enter Communication through `record_validated_information(...)`.

Such records require an authoritative physical event reference and are stored as verified observations.

Face-to-face statements are different:

- they are tied to the canonical stored conversation
- they are attributed to the actual speaker
- they are received only by the other participant
- they begin `unverified`
- retelling does not verify them

A later verified observation may coexist with an earlier claim. Do not erase the historical claim merely because later evidence differs.

## Transcript-Grounded Claim Rule

Structured claim extraction may classify or tag dialogue, but it may not invent the underlying assertion.

The persisted claim `value_text` must be a verbatim sentence/clause present in the durable stored text of the attributed speaker.

If the extracted value is not present in that transcript, no receipt is created.

This protects the provenance ledger from a second model-generated fiction layer.

## Knowledge Is Recipient-Local

A validated discovery has a physical truth source, but it becomes citizen knowledge only for recipients who actually observed/received it.

One citizen discovering a property does not populate all citizens' knowledge.

Any later propagation requires another valid Communication mechanism.

## Current Direct Observation Is Derived

A citizen's present physical location may be exposed as a current direct observation without fabricating a historical receipt.

Historical knowledge requires a real receipt/event source.

## Consumer Read Models

Communication's `GET /api/knowledge/{citizen_id}` is a low-level provenance-oriented view.

For ordinary v0.6 Citizen/Location UI, prefer Memory's bounded consumer knowledge endpoints after integration. This prevents Assets from depending directly on raw provenance internals and preserves Memory ownership of bounded retention/retrieval.

## Visitor Availability Privacy

Visit accessibility states are structured separately from human-readable messages.

When visitor and citizen are remote, the response should not reveal local busy/talk counterpart details merely to explain inaccessibility.

When co-located, busy/talking/traveling states may be reported accurately.

Talk counterpart identity must be resolved from both job roles, not by assuming the selected citizen is always the initiator.
