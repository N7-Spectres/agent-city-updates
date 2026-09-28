# Agent City — Department Coordination Board

_Last updated: 2026-09-28_

This file is the shared project task board.

## Status Key

- **ACTIVE** — currently being worked
- **WAITING** — blocked on another department or coordinator integration
- **READY** — dependency or deliverable is ready for pickup
- **REVIEW** — department branch/work is complete enough for coordinator review
- **DONE** — finished and incorporated

## Current Board

### ACTIVE

- [World & Simulation] v0.6.0 lead: hidden material/world properties, experiments, persistent discoveries, knowledge-filtered world state
- [Communication & Perception] v0.6.0: discovery/claim provenance, local information flow, anti-omniscience audits, visitor busy/talk status fix

### WAITING

- [Assets & Interface] independent Home/Citizens/Locations/Records shell is ready in draft PR #3; waiting on final Simulation, Communication, and Memory knowledge/read-model contracts to finish data-driven views
- [Memory & Social] core branch is complete; richer ingestion waits for final Simulation discovery/experiment IDs and Communication transfer provenance

### READY

- [Communication & Perception] Deeper claim-level `PROVENANCE_CONTRACT.md` remains ready for a later milestone.

### REVIEW

- [Memory & Social] v0.6 per-citizen knowledge core on `memory/v0.6-location-knowledge` at `89c0a3e2d49c4c9236342c10559f92b93b1b7601`; CI run `36419352645` passed all regressions + v0.6 Memory smoke

### DONE

- [Coordinator] v0.5.0 assembled on `release-v0.5.0`, full smoke suite passed, versioned, and published from `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`
- [World & Simulation] v0.5 Making & Building physical core + energy reserve + coordinate groundwork
- [Assets & Interface] v0.5 bounded Visit/History + Making state UI
- [Communication & Perception] v0.5 source-linked talk integrity
- [Memory & Social] v0.5 project/source continuity audit, no schema change required
- [Coordinator] v0.4.0 assembled on `release-v0.4.0`, tested, versioned, and published
- [Coordinator] v0.4.1 blank-reply conversation hotfix tested and published
- [Memory & Social] Durable directional conversation memory + bounded social context
- [Assets & Interface] Control Room redesign + distance-aware map readability pass
- [Communication & Perception] Information-boundary rules / anti-omniscience architecture preserved; provenance contract documented
- [Communication & Perception] Same-location citizen talk system
- [World & Simulation] Visitor physical presence and travel
- [Assets & Interface] v0.3.0 live job progress and moving map markers
- [Memory & Social] Persistent visitor visits and bounded conversation context

## v0.6 Coordination Goal

v0.6.0 is the active coordinated milestone.

Primary rule:
> **The UI may show what the civilization knows, not everything the Simulation secretly knows.**

Department order does not need to be strictly serial, but the integration dependency is:

1. Simulation defines hidden world truth + validated discovery/experiment records.
2. Communication defines how discoveries/claims can move between citizens and fixes visit-status wording.
3. Memory retains/retrieves per-citizen knowledge without creating a global omniscient encyclopedia.
4. Assets renders Home/Citizens/Locations only from the safe known-state interfaces.
5. Coordinator assembles all branches and runs regression + v0.6 smoke tests before publication.

No department should publish `update.json`.

## v0.5 Integration Result

v0.5.0 passed the assembled release gate on `release-v0.5.0`.

Preserved invariants:
1. canonical `citizen_conversations.id` and nullable unique `source_job_id`
2. talk with no stored exchange fails instead of falsely completing
3. project/equipment/structure UI comes only from Simulation state
4. Memory keeps project discussion separate from validated physical outcomes
5. v0.4 regression, v0.5 Simulation, v0.5 Communication, and v0.5 UI integration smoke suites all passed

## Handoff Protocol

When Department A needs Department B:

1. Department A writes a concise request to Department B's `INBOX.md`.
2. Department A records itself as **WAITING** here if the dependency blocks progress.
3. Department B reads its INBOX at the beginning of its next work session.
4. Department B completes the work or records why it cannot.
5. Department B writes the result to its own `OUTBOX.md` and, when useful, directly to Department A's `INBOX.md`.
6. The main coordinator reviews the handoff and updates this board.

## Coordinator Rule

Departments own systems, not reality.

Cross-department integration must preserve:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

A green department branch is not sufficient if merging it would silently remove another department's invariant.
