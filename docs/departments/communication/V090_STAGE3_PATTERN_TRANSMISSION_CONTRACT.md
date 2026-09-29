# v0.9 Stage 3 — Communication Pattern / Place / Social Transmission Contract

_Status: ready for downstream consumption_  
_Runtime branch: `communication/v0.9-patterns-stage3`_  
_Final clean head: `3fc8872b7a35ee8169329d6a6edf523a2fa0b0c9`_  
_Validation: GitHub Actions `36643141322` — PASS_

## Purpose

Communication turns source-backed Stage 3 continuity into natural language without turning history into identity, preference, or universal culture.

It also provides the only Stage 3 citizen-to-citizen transmission bridge:

**raw exchange → transcript-grounded claim receipt → owner-scoped Memory event → social-pattern evidence**

Every later step is best-effort. Failure never erases or invalidates the raw stored conversation.

## Pattern Language Surface

`pattern_continuity_context(citizen_id, location_id=None)` consumes Memory's:

- recurring voluntary-choice candidates,
- citizen-specific place continuity,
- owner-perspective social custom candidates.

Safe interpretations include:

- current recurring evidence: “I seem to keep choosing this here.”
- mixed/fading evidence: historical/changing language rather than a standing preference.
- place continuity: “This place matters in my history because …” when the cited source trail supports that interpretation.
- social pattern: “I’ve seen/heard this more than once.”

Unsafe automatic conclusions include:

- personality traits,
- permanent roles/professions,
- “favorite place,”
- “home/safe/sacred place” without separate evidence,
- “our tradition,”
- “everyone does this,”
- universal custom/culture truth.

## Transmittable Pattern Catalog

`transmittable_pattern_catalog(citizen_id)` returns only patterns already supported by that speaker's own Stage 3 Memory evidence.

For recurring choices, Communication derives a stable key:

`habit:<action_key>|<context_key>`

For existing owner-perspective social patterns, the Memory pattern key is reused.

The dialogue claim classifier may select one of these keys. It may not create an arbitrary key.

## Grounded Face-to-Face Transmission

The claim extractor may emit:

- `subject_type = social_pattern`
- an exact `pattern_key` from that speaker's allowed catalog
- a verbatim `value` copied from the stored speaker transcript

A pattern transmission is retained only when all are true:

1. a durable face-to-face `citizen_conversations.id` exists,
2. the literal claim text appears in the attributed speaker transcript,
3. provenance creates an unverified `information_receipts.id` for the listener,
4. the selected pattern key exists in the speaker's source-backed catalog,
5. Communication creates a recipient-owned Memory event sourced by that receipt,
6. Memory `record_social_pattern_evidence(..., transmission_mode="heard")` accepts it.

The actor recorded for heard evidence is the real source speaker.

The transmission remains unverified unless later physical evidence separately verifies it.

## Custom Threshold Boundary

One conversation never creates a custom.

Memory still requires its canonical threshold:

- at least 3 source-backed social evidence events,
- at least 2 distinct actors,
- at least 2 simulation days,
- at least one actor other than the observer.

Communication does not weaken or recreate that threshold.

## Visitor Boundary

Visitor dialogue receives the citizen's own pattern/place/social continuity context for conversation.

Visitor chatter does **not** register citizen-to-citizen social custom transmission and does not create custom evidence.

## Reliability Boundary

Pattern projection is downstream of the raw exchange and generic claim receipt.

If pattern extraction/projection fails:

- the durable conversation remains,
- valid generic claim receipts remain,
- no physical state changes,
- no pattern is invented to “repair” continuity.

## Regression Contract

Preserve:

- all prior Communication provenance/raw-exchange-first smokes,
- `tests/smoke_v090_memory_stage3.py`,
- `tests/smoke_v090_simulation_stage3.py`,
- `tests/smoke_v090_communication_stage3.py`.

Communication Stage 3 smoke verifies:

- source-backed personal recurring patterns are discussable,
- only catalog-backed pattern keys transmit,
- invented pattern keys create no Stage 3 evidence,
- one or two reports do not create a custom,
- three reports from two real speakers across two days may create only the recipient's owner-perspective custom candidate,
- verification remains unverified,
- unrelated citizens inherit nothing,
- no global culture/tradition table exists.

No `update.json` or release metadata change is authorized.
