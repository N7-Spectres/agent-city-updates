# Memory & Social — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** v0.4 social-memory core implemented on isolated runtime branch

**Need / Result:**
Implemented the first v0.4 relationship-memory slice on branch `memory/v0.4-social-memory-core`, based directly on the shipped v0.3.0 runtime commit `40f9704b7e84e2dd6279932223105ae93d9fef49`.

Added durable per-citizen memory events, directional relationship history, idempotent conversation backfill, source deduplication, and bounded social retrieval for planning/dialogue.

**Files / Interfaces:**
- `agent_city/memory.py` — new memory schema, migration, retrieval, relationship projection
- `agent_city/comms.py` — new citizen conversations create participant memories
- `agent_city/planner.py` — bounded durable social history enters planning
- `main.py` — memory migration at startup and bounded social history in dialogue

**Important constraints:**
- no RPG-style relationship score
- conversation content remains claims/memory, not physical truth
- raw history is preserved
- no `update.json` or release publication changes
- `main` and the v0.3.0 runtime lineage are currently divergent, so integration/release assembly must account for that repository structure

**Next action:**
Continue with provenance-backed claims and validated cooperation/help events once Communication and Simulation expose their interfaces.

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Runtime provenance needed for claim memory

**Need / Result:**
Memory is ready to ingest specific information-transfer records rather than treating entire conversation summaries as verified knowledge.

**Files / Interfaces:**
- Communication provenance contract
- stable transfer/source conversation IDs
- recipient/source/topic/value/received time/assertion kind/verification fields

**Important constraints:**
- retelling is not verification
- Memory will retain claims and derive bounded last-known/reliability views
- Communication remains owner of transfer/observation provenance

**Next action:**
Communication should expose the minimum runtime provenance layer and notify Memory when ready.

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Validated social outcome event IDs needed

**Need / Result:**
Memory needs stable Simulation references for future cooperation/help/promise-outcome memories.

**Files / Interfaces:**
- validated action/job/event ID
- sim minute
- participant IDs
- action/outcome type
- success/failure or resulting state where appropriate

**Important constraints:**
- Memory must not infer that physical cooperation/help occurred solely from dialogue
- Simulation remains authoritative

**Next action:**
World & Simulation should identify or expose the minimal stable event interface when v0.4 social outcomes need to be recorded.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
