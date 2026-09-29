# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-29 — From: Main Coordinator — Status: WAITING / DESIGN AUDIT ALLOWED

**Subject:** v0.9 — Recognition, Self-Assessment, and Teaching Boundaries

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

**Audit now:**
- how citizens may naturally talk about repeated experience without creating authoritative titles
- language for self-assessment vs objective physical capability
- citizen-to-citizen recognition as perspective, not global reputation
- source requirements for statements such as "Bex has done this more than I have"
- future teaching conversation vs actual skill-transfer boundary
- how plans may be discussed without conversation itself completing/revising physical reality

**Hard locks:**
- no universal reputation
- no automatic expert/leader/rank designation
- no skill transfer merely because someone explains something
- no conversation summary may become competence evidence by itself
- recognition requires information that actually reached the speaker
- self-assessment remains interpretation unless separately measured

**Dependencies:**
- Memory Stage 1 retrieval/source contract
- Simulation canonical plan/practice event contract

**Expected next deliverable:**
Communication design contract and source-language rules. Runtime implementation waits for upstream contracts.

Do not publish `update.json`.

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
