# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Canonical conversation source preserved in v0.5

**Need / Result:**
The v0.5 conversation-integrity implementation preserves `citizen_conversations.id` exactly as Memory's canonical immutable source ID.

Existing `memory_events` references remain valid:
- `source_type = 'citizen_conversation'`
- `source_id = citizen_conversations.id`

New autonomous conversation rows additionally expose:
- `source_job_id`: unique physical talk job ID, nullable for legacy rows
- `source_type = 'citizen_conversation'`
- `source_id = id`
- `transfer_event_id = id`
- authoritative source-linked `sim_minute` / location / participants
- original initiator text, target text, and concise summary

**Integrity behavior:**
- no conversation row is created for a failed/invalidated talk
- retries of the same physical talk do not duplicate the raw conversation source
- model-generation failure no longer persists fabricated fallback dialogue
- a talk job cannot finish successfully unless its conversation source exists
- Memory projection failure cannot erase the durable conversation row; normal idempotent backfill can repair projection later

**Important constraints:**
- `source_job_id` is a supplementary physical anchor, not a replacement canonical source ID
- conversation content remains claims/discussion
- claim-level provenance/verification is not implemented in this v0.5 slice

**Next action:**
No Memory migration change is required for the canonical conversation source. Memory may consume `source_job_id` later where a physical talk-job anchor is useful.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.5.0 memory support for projects and conversation source continuity

**Result:**
Memory's project-continuity audit is complete; Communication has now delivered the final conversation-source shape. Remaining project outcome hooks still depend on Simulation's stable project/event IDs.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
