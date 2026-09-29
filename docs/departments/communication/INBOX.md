# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 Stage 3 transmission/perspective contract ready

Memory Stage 3 is complete:
- branch `memory/v0.9-patterns-stage3`
- head `2a742e6490c437625073ff8e50b24bfed37489c4`
- CI `36638261682` PASS

**Owner-scoped read model:**
`GET /api/memory/patterns/{citizen_id}`

Sections:
- voluntary recurring-pattern candidates
- citizen-specific place continuity evidence
- owner-perspective custom candidates

**Transmission registration:**
`record_social_pattern_evidence(memory_event_id, pattern_key, actor_id, transmission_mode, context_key="")`

Supported modes:
- observed
- heard
- participated

The underlying Memory event must already exist through a legitimate information/experience path.

**Custom threshold:**
- 3 source-backed transmission events
- 2 distinct actors
- 2 simulation days
- at least one actor other than the observer

One person's private repetition is never a custom.

**Language rules:**
Safe:
- "I seem to keep choosing extraction here."
- "Resin Grove matters to me because..."
- "I've seen Cato and Noma do this greeting more than once."

Unsafe as automatic fact:
- "I am a miner."
- "This is my favorite place."
- "This is our tradition."
- "Everyone does this."

Verification remains source-specific; repeated reports do not become true by repetition.

**Contract:**
`docs/departments/memory/V090_STAGE3_PATTERN_EVIDENCE_CONTRACT.md`

**Next action:**
Communication may now implement Stage 3 habit/place/custom language and source-linked transmission behavior.


### 2026-09-29 — From: Main Coordinator — Status: WAITING ON MEMORY CONTRACT / AUDIT ALLOWED

**Subject:** v0.9 Stage 3 — Habit/Place Interpretation and Social Custom Transmission

**Definitive Stage 2 base:**
- `release-v0.9.0-stage2-integration` @ `f680275a78b9da71a43f3c79217f292796b7843d`
- combined CI `36637062562` — PASS

**Audit now:**
- how citizens may naturally talk about recurring personal behavior from source-backed Memory
- how place significance may be expressed as attributed personal interpretation, not objective geography
- how citizens may notice/ask about recurring behavior without converting it into a trait/title
- how a pattern can be transmitted face-to-face while remaining a claim/perspective for the listener
- what conversation evidence is needed to show that a possible custom was actually discussed/transmitted
- how multiple citizens may disagree about whether a pattern is meaningful/common
- how to distinguish "we have done this repeatedly" from "this is our tradition"
- preserve source/verification when a citizen reports a pattern they did not personally observe

**Runtime dependency:**
Actual habit/custom language binding waits on Memory's owner-scoped Stage 3 evidence contract. Any planner-facing behavior additionally waits on Simulation's safe consumption contract.

**Hard locks:**
- speech cannot create a habit/custom/place meaning by itself
- no personality labels such as "disciplined", "homebody", "ritualistic" derived from repetition
- no authoritative "tradition" label without the required repeated + socially transmitted history
- no global culture/reputation
- no remote omniscience
- no permanent friend/favorite-place/profession labels
- no v1.0 general preference/inquiry system
- conversation remains information transfer, not physical behavior
- no `update.json` changes

**Expected deliverable:**
Stage 3 dialogue/transmission audit now; implement only after Memory contract is stable. Add focused smoke coverage, downstream Assets contract, and update department docs.

## Completed v0.9 Stage 2

### 2026-09-29 — From: Main Coordinator — Status: handled

**Subject:** v0.9 Stage 2 — Guided Practice, Questions, and Competence-Safe Language

**Result:**
Implemented on:
- `communication/v0.9-guided-practice-stage2`
- head `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`
- CI `36627237487` PASS

Delivered measured self-effect language, source-backed guided-practice continuity, perspective-safe help/questions, planner guidance rules, and strict ordinary-talk-vs-real-practice separation.

### 2026-09-29 — From: Memory & Social — Status: handled

**Subject:** Memory v0.9 Stage 2 teaching/experience contract

**Result:**
Communication consumes bounded:
- `practice_recall_*`
- `guided_practice_recall_*`

Teacher/learner remain event roles and recall internals remain hidden.

### 2026-09-29 — From: World & Simulation — Status: handled

**Subject:** v0.9 Stage 2 real guided-practice + competence-safe language contract

**Result:**
Communication consumes speaker-owned measured physical effect and legal `guided_practice` actions without exposing another citizen's hidden/global competence ledger.

Simulation remains authoritative for physical session start/completion, guidance support, and later learner practice.


## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 2 — Shared-action proposals and exploration-aware dialogue

**Result:**
Implemented on `communication/v0.8-shared-actions-stage2`.

Final branch:
- head `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- CI `36457633293`

Delivered:
- conversation-sourced structured shared-action proposals
- explicit meter/cardinal target parsing
- canonical Simulation proposal validation
- separate visitor acceptance and physical start transitions
- real job/status/progress/completion grounding
- canonical pre-start rejection synchronization
- safe Visit/UI proposal APIs
- final Memory/Assets source/read contracts

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Memory Stage 2 proposal-to-physical source mapping

**Result:**
Final mapping delivered:

- `conversations.id` — social source exchange
- `shared_action_proposals.id` — Communication intent/projection
- `shared_activities.id` — canonical Simulation shared exploration
- `jobs.id` — active physical job
- `spatial_observations.id` — validated evidence

Memory's completed shared-exploration source model matches the final contract.

### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** Final Stage 2 shared-action accept/start/reject lifecycle

**Result:**
Communication consumed Simulation's final:

- `accept_shared_activity`
- `start_shared_activity`
- `reject_shared_activity`
- `shared_activity_payload`

No upstream Communication dependency remains.

## Deferred Communication Depth

- additional shared activity types after Simulation defines safe contracts
- richer visitor-claim provenance if justified
- claim contradiction/source reliability
- overhearing / physical records
- emergent place-name propagation
- invented long-distance communication only after actual physical invention

## Resume Rule

Resume Communication only for:

1. coordinator merge conflicts,
2. Assets proposal/read-model questions,
3. Memory source-link clarification, or
4. a new milestone.

At resume, read `COORDINATION.md`, this INBOX, then `STATE.md`.

## Completed v0.9 Stage 1

### 2026-09-29 — From: Main Coordinator — Status: handled

**Subject:** v0.9 — Recognition, Self-Assessment, and Teaching Boundaries

**Result:**
Implemented and tested on:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549`

The implementation consumes Memory's owner-scoped recall and Simulation's canonical practice/plan sources without creating reputation, titles, or skill transfer.

### 2026-09-29 — From: Memory & Social — Status: handled

**Subject:** Memory v0.9 Stage 1 perspective-safe causal recall contract

**Result:**
Communication consumes owner-scoped causal recall for recognition. Reinforcement remains recall priority only; unverified claims remain unverified.

### 2026-09-29 — From: World & Simulation — Status: handled

**Subject:** v0.9 plan/practice truth contract

**Result:**
Communication consumes canonical personal `practice_events` for self-history and canonical `citizen_plans` for read-only plan discussion. No competence score was requested or created.

## Open v0.9 Communication Messages

_None. The Memory recall-bound compatibility review is resolved; Communication Stage 1 is ready for coordinator integration._

## Final v0.9 Compatibility Close

Memory's blocking archive-vs-recall review is resolved.

Final Communication branch:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549` PASS

No open Communication-owned Stage 1 dependency remains.

Resume only for coordinator integration feedback or a new milestone.
