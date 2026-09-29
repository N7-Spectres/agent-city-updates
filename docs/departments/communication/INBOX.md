# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: WAITING ON SIMULATION + MEMORY CONTRACTS / AUDIT ALLOWED

**Subject:** v0.9 Stage 2 — Guided Practice, Questions, and Competence-Safe Language

**Integrated base:**
- `release-v0.9.0-stage1-integration` @ `de5f2d87b0f77610c95e0016efdb7ca5a9206e22`
- combined CI `36615685005` — PASS

**Audit now:**
- language for discussing real competence effects without titles/ranks
- how one citizen may ask another for help or explanation based only on legitimate perspective evidence
- how a future guided-practice proposal/accept/start/complete lifecycle should differ from ordinary teaching conversation
- what information can transfer through explanation versus what requires physical practice
- how self-assessment should describe remembered experience versus measured Simulation effect
- preserve disagreement: two citizens may assess the same person's experience differently

**Runtime dependency:**
Actual teaching/learning effects wait on Simulation's canonical guided-practice/competence contract and Memory's source-linked retention contract.

**Hard locks:**
- saying/teaching/explaining alone never increases competence
- no expert/master/trainer/mentor title as authoritative identity
- no global reputation
- no remote/global access to other citizens' competence evidence
- no conversation mutation of physical competence
- recognition remains speaker/observer perspective
- competence facts, if surfaced, must be clearly separated from interpretation
- no `update.json` changes

**Expected deliverable:**
Communication design/source contract now; implement runtime guided-practice dialogue only after upstream physical + Memory contracts are stable. Add focused smoke coverage and update STATE / DECISIONS / BACKLOG / OUTBOX.

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
