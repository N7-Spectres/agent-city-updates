# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 1 — Seeded spatial world foundation

**Runtime base / branch:**
- base: `release-v0.7.0` / immutable commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- create/use: `simulation/v0.8-seeded-world-stage1`

**Stage 1 goal:**
Lay the authoritative hidden-world substrate needed for continuous exploration without yet attempting the entire Living World milestone.

**Required implementation:**
- persistent planet/body seed stored in the save
- deterministic local hidden-world query derived from seed + coordinate/chunk
- meter-scale local x/y position foundation compatible with later global lat/lon
- spatially correlated terrain/geology/resource generation, not independent random rolls per scan
- stable physical IDs for generated deposits/bodies plus enough spatial extent/geometry to recognize the same vein from nearby coordinates
- querying the same coordinate later must return the same hidden truth
- lazy generation is allowed if it remains deterministic
- preserve existing named locations/routes as known landmarks inside the new coordinate world rather than deleting/resetting them
- preserve all existing v0.7 saves additively
- expose only safe/validated results through ordinary state; raw seed/chunk truth remains hidden
- provide a minimal Simulation-owned query/action contract that later scanner/survey/shared-exploration systems can call

**Do NOT yet:**
- build the full globe renderer
- add arbitrary new citizen technologies
- invent scanners for citizens who do not own one
- expose hidden seed/world tables to UI/LLM
- implement the entire asset-worker pipeline
- publish `update.json`

**Acceptance direction:**
- two queries at the same coordinate are stable
- nearby points show coherent spatial variation
- moving 1 meter may remain in the same deposit or cross an edge, not automatically create a new deposit
- existing Resin Grove / Seed Site etc. remain physically anchored and migrate safely
- undiscovered generated resources remain invisible to ordinary citizen/UI state

**Handoff needed:**
Send Communication/Memory/Assets the exact coordinate, hidden-world-query, stable-deposit, and validated-observation interfaces they may safely consume.

**Next action:**
Implement/test Stage 1, update Simulation STATE/DECISIONS/BACKLOG/OUTBOX, route contracts to dependent departments, then stop for coordinator review.


_None. The active v0.7 Maintenance & Consequences work packet was implemented and handed off._

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
