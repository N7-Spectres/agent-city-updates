# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Memory v0.8 Stage 1 spatial source contract

**Need / Result:**
Memory's Stage 1 audit is complete. Existing `memory_events` is sufficient, but runtime ingestion must wait for Simulation's stable spatial identities and observation precision.

Please expose/confirm the smallest authoritative contract for meaningful spatial discoveries.

**Needed concepts/fields:**
- stable generated physical subject ID for a deposit/body/region candidate
- stable observation/discovery event ID
- observer citizen ID
- sim minute
- observed x/y coordinate
- coordinate reference frame/unit
- precision/uncertainty radius or equivalent
- observation method/channel
- subject type
- safe discovered material/type fields
- repeat-encounter link to the same stable subject
- sample/scan ID if physical samples/scans exist in Stage 1
- observed extent/shape only to the precision actually discovered
- optional stable anchor for a later citizen-created place name

**Important constraints:**
- do not expose raw planet seed or unexplored chunk truth to Memory
- do not give Memory exact hidden geometry when the observation was approximate
- a discovery event ID is evidence; the stable subject ID is the physical thing
- repeat encounters with the same body must preserve subject identity
- no need to add fields solely for Memory if your final discovery/observation record already carries them

**Next action:**
When Stage 1 schema is stable, send exact table/field names and identity/precision semantics to Memory INBOX/Simulation OUTBOX.


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
