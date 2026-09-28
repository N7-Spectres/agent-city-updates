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

- [Assets & Interface] Finish v0.5 Making & Building visualization using Simulation's stable authoritative state contract.

### WAITING

- [Coordinator / Integration] Final milestone assembly still needs the completed Simulation branch plus Assets' finished UI branch integrated and smoke-tested together.

### READY

- [World & Simulation] Integrated Making & Building + Communication physical-talk invariant ready: `simulation/v0.5-making-building` @ `773299189d22d214b3376c72b396015a4a7a762e`.
- [World & Simulation] Integrated CI run `36372991331` passed Python compile, JavaScript syntax, `tests/smoke_v040.py`, `tests/smoke_v050.py`, and `tests/smoke_v050_communication.py`.
- [Assets & Interface] Simulation's authoritative `projects`, `project_materials`, `equipment`, and extended `structures` schema is ready for UI consumption.
- [Communication & Perception] Canonical conversation source and physical talk-job integrity are already preserved inside the Simulation branch; no separate conflict-resolution step remains for those changes.
- [Memory & Social] Stable Simulation project/job/equipment/structure anchors are confirmed; no v0.5 Memory schema change is required.
- [Communication & Perception] Deeper claim-level `PROVENANCE_CONTRACT.md` remains ready for a later milestone.

### REVIEW

- [World & Simulation] v0.5 physical core complete and cross-department talk invariant integrated. Ready for coordinator review.
- [Communication & Perception] Conversation-history integrity complete and incorporated into Simulation's integrated branch.
- [Memory & Social] Project-continuity audit complete; physical outcome references are stable.
- [Assets & Interface] Independent compact layout/chat/History slice exists on `assets/v0.5-making-ui`; final physical-state visualization remains active.

### DONE

- [Coordinator] v0.4.0 assembled on `release-v0.4.0`, tested, versioned, and published
- [Coordinator] v0.4.1 blank-reply conversation hotfix tested and published
- [Memory & Social] Durable directional conversation memory + bounded social context
- [Assets & Interface] Control Room redesign + distance-aware map readability pass
- [Communication & Perception] Information-boundary rules / anti-omniscience architecture preserved; provenance contract documented
- [Communication & Perception] Same-location citizen talk system
- [World & Simulation] Visitor physical presence and travel
- [Assets & Interface] v0.3.0 live job progress and moving map markers
- [Memory & Social] Persistent visitor visits and bounded conversation context

## Final v0.5 Integration Gate

Before v0.5 can be treated as one coherent milestone:

1. Assets consumes Simulation's authoritative Making & Building state and finishes the physical-state UI.
2. Coordinator integrates `simulation/v0.5-making-building` with the finished Assets branch.
3. Preserve canonical `citizen_conversations.id` and nullable unique `citizen_conversations.source_job_id`.
4. Preserve the rule that a talk with no stored exchange fails rather than completing successfully.
5. Preserve Simulation's project/equipment/structure state without frontend-derived physical facts.
6. Run the v0.4 regression smoke, v0.5 Simulation smoke, and v0.5 Communication integrity smoke on the assembled milestone.
7. Keep Memory project discussion distinct from validated physical project outcomes.
8. Do not publish or alter `update.json` until the human explicitly requests release publication.

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
