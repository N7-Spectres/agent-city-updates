# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** v0.5 project/event IDs for Memory continuity

**Need / Result:**
Memory does not need a new table for v0.5, but it needs stable Simulation-owned identifiers before it can record project intentions/outcomes safely.

Please expose/confirm:
- stable project_id
- stable project event or completed job ID
- simulation minute
- project state transition (planned/reserved/underway/completed/failed/cancelled, or your final equivalent)
- validated outcome type
- participant/owner citizen IDs where relevant

Memory will keep "citizens discussed/planned X" sourced to conversation and create a separate physical-outcome memory only from these authoritative IDs.

**Files / Interfaces:**
- future project table/event table or durable jobs
- `memory_events.source_type/source_id/metadata_json` will reference the Simulation IDs

**Important constraints:**
- please do not create fields solely to satisfy Memory if existing durable project/job IDs already cover them
- project discussion is not physical project state
- promise/cooperation success remains disabled until a validated outcome exists

**Next action:**
Send the final minimal project/event record shape to Memory INBOX/Simulation OUTBOX when the v0.5 schema is settled.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.5.0 lead — Making & Building / energy-safe field work

**Need / Result:**
Implement the physical core of v0.5.0 from the shipped v0.4.1 runtime lineage. This department is the lead because fabrication, construction, tools, cargo capacity, project state, energy feasibility, and structure placement are physical truth.

**Runtime base / branch:**
- base: `release-v0.4.1` / immutable commit `4181cbb69809205ae575b3f576836e5ca72c8dce`
- create/use department branch: `simulation/v0.5-making-building`

**Required v0.5 scope:**
- fabrication jobs that consume validated materials/time and produce real stored tools/components
- construction jobs/projects that consume validated materials/time and produce real structures
- simple multi-step project lifecycle sufficient for planning/reservation/underway/completion
- tools may alter extraction speed and/or usable yield through explicit physical modifiers
- carrying equipment may raise cargo capacity through real fabricated equipment
- preserve simple understandable rules; no sprawling crafting simulator
- keep "return cargo home" as a citizen choice rather than hard-coded automatic behavior
- add return-energy reserve validation: do not allow remote work/outbound travel that would leave insufficient energy to reach a known charger plus a modest safety margin
- future chargers/outposts should be representable as valid recharge destinations
- lay minimal coordinate groundwork so structures can later exist between original landmarks; do not implement full free-roam globe exploration yet
- preserve existing visitor travel, citizen talk, memory, and updater behavior

**Important constraints:**
- AI chooses intent; Simulation decides reality
- no fabricated object/structure exists because the LLM merely said so
- no arbitrary level-up bonuses
- no new communication technology
- do not publish `update.json`
- preserve existing saves/migrations

**Acceptance checks:**
- materials cannot go negative
- a completed fabrication creates a real object/equipment record
- a completed construction creates a real structure record at a validated location/site
- tool/carry effects are derived from owned/available equipment
- an unsafe energy-expending action is rejected before start
- a citizen can still choose to return/deposit normally
- old v0.4.1 saves migrate safely

**Next action:**
Implement, test, update Simulation STATE/DECISIONS/BACKLOG/OUTBOX, send cross-department schema/UI needs directly to their inboxes, then stop for coordinator integration.


### 2026-09-28 — From: Memory & Social — Status: ready

**Subject:** Verified v0.3.0 runtime source for event-interface work

**Need / Result:**
The complete shipped runtime is available at commit `40f9704b7e84e2dd6279932223105ae93d9fef49`, despite key modules being absent from the current default-branch tree.

This commit contains the full `simulation.py`, `db.py`, jobs schema, conversation system, visitor system, and planner needed to answer the event-interface requests below.

**Files / Interfaces:**
- runtime base commit: `40f9704b7e84e2dd6279932223105ae93d9fef49`
- Memory branch: `memory/v0.4-social-memory-core`

**Important constraints:**
- prefer confirming/reusing stable completed job IDs before inventing a parallel event system
- do not modify release metadata

**Next action:**
Inspect the verified runtime lineage and answer the outstanding Memory/Communication event-interface requests through Simulation OUTBOX and the relevant department inboxes.


### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Stable event references for physical social outcomes

**Need / Result:**
Memory's v0.4 core can now store event-backed social memories. For cooperation, help, commitment outcomes, and later reliability verification, Memory needs stable references to validated physical outcomes.

**Files / Interfaces:**
Please identify or expose a minimal event interface containing:
- stable action/job/event ID
- sim_minute
- participant citizen IDs where multiple citizens are involved
- action/outcome type
- validated success/failure or resulting state where applicable

Existing job IDs may be sufficient if they remain stable and preserve enough completed-event history; please confirm rather than creating a parallel event system unnecessarily.

**Important constraints:**
- Simulation remains physical authority
- Memory will reference outcomes, not create them
- no need to redesign physical rules solely for Memory

**Next action:**
Reply through Simulation OUTBOX and/or Memory INBOX with the recommended stable interface.


### 2026-09-28 — From: Communication & Perception — Status: request

**Subject:** Authoritative event/time inputs for information provenance

**Need / Result:**
Communication's v0.4 provenance layer needs authoritative physical inputs from Simulation so observations and transfers can be grounded without treating conversation claims as reality.

**Files / Interfaces:**
- authoritative current simulation minute
- authoritative participant location / co-location check
- validated event ID for observable action/outcome when available
- clear traveling/availability state for talk validation
- legal-action labels/reasons that do not reveal hidden remote state to the planner

**Important constraints:**
- Simulation decides what physically happened
- Communication decides whether information could reach someone
- no new remote communication mechanism is requested

**Next action:**
When the runtime source is synchronized, expose or confirm the smallest stable interfaces/fields above so Communication can persist provenance records safely.


### 2026-09-28 — From: Assets & Interface — Status: request

**Subject:** v0.5 Making & Building UI state contract

**Need / Result:**
Assets is implementing the independent v0.5 layout/history work now. For the physical Making & Building visual layer, please hand off the final authoritative state shape once Simulation's schema is stable.

**Files / Interfaces:**
Prefer fields exposed through `/api/state` (or a clearly named companion endpoint) for:
- projects: stable ID, type, name/label, status/lifecycle stage, location/site ID, involved citizen IDs, progress/time when authoritative, reserved/consumed material summary
- equipment/tools: stable ID, type/name, owner or storage/location, condition if tracked, validated physical modifiers such as cargo-capacity or extraction effects
- structures: stable ID, type/name, validated location/site (and coordinates if v0.5 exposes them), condition, construction/project source when available
- any explicit capability/effect fields the UI may safely display without re-deriving simulation rules

**Important constraints:**
- Assets will visualize these fields only; it will not infer completion, bonuses, material consumption, coordinates, or legality
- please distinguish active/reserved project state from completed physical objects
- preserve stable IDs so future map/history views can link to real projects and outcomes

**Next action:**
When the Simulation schema is stable, reply through Simulation OUTBOX and/or Assets INBOX with the exact field names and lifecycle values. Assets can then add the restrained project/tool/structure UI without touching physical rules.


## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
