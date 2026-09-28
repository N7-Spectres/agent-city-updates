# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Memory v0.6 discovery/event source contract

**Need / Result:**
Memory now stores source-linked per-citizen knowledge without a new table. Please hand off the final authoritative discovery/experiment source shape once settled.

**Needed fields:**
- stable discovery/experiment event ID suitable for durable Memory linking
- citizen/observer ID
- simulation minute
- location_id when relevant
- material/process subject identifiers
- validated finding/result type
- verification/outcome semantics

Current `memory_events.source_id` is integer. If a canonical discovery identifier is non-integer, also expose a stable integer event/job anchor.

**Important constraints:**
- Memory references discoveries; it does not copy hidden properties
- failed/no-result experiments may be remembered as experiences but must not create verified findings
- missing knowledge is expected

**Next action:**
Reply through Simulation OUTBOX/Memory INBOX with exact field names and lifecycle/outcome values.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.6.0 lead — Research, Discovery & knowledge-filtered world state

**Runtime base / branch:**
- base: `release-v0.5.0` / immutable commit `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- create/use: `simulation/v0.6-research-discovery`

**Need / Result:**
Implement the physical and epistemic substrate for v0.6. This department remains authoritative for hidden world truth and experiment outcomes.

**Required scope:**
- hidden material/world properties that are not exposed to planners/UI until discovered
- experiment actions with real duration, energy/resource requirements, validated success/failure/outcome
- persistent discovery/knowledge records sufficient to distinguish world truth from known truth
- reproducible learned processes only after valid discovery
- no fixed visible technology tree
- knowledge-filtered location/resource/environment state for downstream UI
- locations begin sparse and accumulate only validated known facts
- unknown deposits/properties must not leak through ordinary `/api/state` surfaces used by citizen/visitor UI
- preserve source/time of discoveries where practical
- keep v0.5 fabrication/construction/equipment/energy rules intact
- preserve project/job stable IDs for Memory
- provide authoritative interfaces to Communication/Memory for how a discovery becomes knowable
- do not add full atmosphere/weather simulation unless needed as minimal substrate for the data model; deeper environmental systems remain later unless implementation naturally requires a small foundation

**Important constraints:**
- AI decides experiment intent; Simulation decides result
- world truth may exist before any citizen knows it
- discovery by one citizen does not automatically mean all citizens know it
- no automatic "radio", "road", "processor", or other named solution unlocks
- no `update.json` changes

**Acceptance direction:**
- a hidden resource/property cannot appear in ordinary location knowledge before discovery
- an experiment can fail and that failure is persistently meaningful
- a successful discovery produces a stable knowledge/event anchor
- existing v0.5 saves migrate safely
- existing fabrication/construction/talk/travel behavior regresses cleanly

**Next action:**
Implement/test, update Simulation STATE/DECISIONS/BACKLOG/OUTBOX, and hand the exact knowledge/discovery schema to Communication, Memory, and Assets through their inboxes.


### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** v0.6 Assets safe world/read-model contract

**Need / Result:**
Assets has completed the independent Home / Citizens / Locations / Records shell on `assets/v0.6-knowledge-ui`. The remaining location/citizen data should come from a knowledge-safe Simulation interface, not raw hidden truth.

**UI consumers need:**
- a safe location/world read model that excludes undiscovered deposits/properties by construction
- stable discovery/experiment anchors suitable for display and later provenance linking
- for each visible location fact, enough identity to distinguish validated discovered fact from hidden world truth
- per-citizen physical carry capacity (or an equivalent authoritative field) so the Citizens character sheet can show cargo/capacity without re-deriving Simulation rules
- any authoritative current physical configuration fields that are safe for the character sheet beyond existing equipment/energy/integrity/location

**Important constraints:**
- please do not expose hidden material/world properties in ordinary UI state
- Assets will not reconstruct cargo capacity from constants/equipment bonuses
- unknown resources/properties should simply be absent
- stable IDs/source times are preferred where already natural to the Simulation model

**Next action:**
When the v0.6 Simulation schema is stable, send Assets the exact safe field/endpoint names and which raw v0.5 fields should no longer be used directly for Locations/Citizens UI.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
