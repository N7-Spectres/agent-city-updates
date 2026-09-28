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
