# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.5.0 memory support for projects and conversation source continuity

**Need / Result:**
Keep Memory compatible with the v0.5 Making & Building milestone without inventing physical outcomes. Focus on durable social/project continuity that can be grounded in Simulation/Communication source records.

**Runtime base / branch:**
- base: `release-v0.4.1` / immutable commit `4181cbb69809205ae575b3f576836e5ca72c8dce`
- create/use department branch only if code changes are needed: `memory/v0.5-project-continuity`

**Required v0.5 scope:**
- verify conversation memories remain linked to the stable raw conversation/source records Communication exposes
- ensure History/Memory can distinguish "citizens discussed/planned X" from "X physically happened"
- define the minimal memory hooks for future project intentions/commitments using validated project/event IDs when available
- do not create promise/cooperation success memories until Simulation supplies authoritative outcome references
- keep bounded context and migration safety intact

**Important constraints:**
- Memory never creates physical truth
- conversation content is not automatic proof of construction/fabrication
- avoid unnecessary schema expansion if existing memory_events/source IDs already suffice
- do not publish `update.json`

**Next action:**
Audit/adapt only what v0.5 needs, coordinate with Communication/Simulation via inbox files, update Memory STATE/DECISIONS/BACKLOG/OUTBOX, then stop for integration.


## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
