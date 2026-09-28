# Agent City — Department Coordination Board

_Last updated: 2026-09-28_

This file is the shared coordination board for Agent City departments.

## Status Key

- **ACTIVE** — currently being worked
- **WAITING** — blocked on another department or coordinator integration
- **READY** — dependency or deliverable is ready for pickup
- **REVIEW** — department branch/work is complete enough for coordinator review
- **DONE** — finished and incorporated

## Current Board

### ACTIVE

_None. All department work sessions for the current v0.5 packet have stopped._

### WAITING

- [Coordinator / Integration] Merge `communication/v0.5-history-integrity` with `simulation/v0.5-making-building` without dropping Communication's `citizen_conversations.source_job_id` schema or talk-completion integrity. The independent Simulation branch currently lacks those changes.
- [Assets & Interface] Independent v0.5 layout/History branch is complete, but the Making & Building visual layer still needs the merged authoritative `equipment`, `projects`, `project_materials`, and extended `structures` state.

### READY

- [Communication & Perception] Conversation integrity branch ready: `communication/v0.5-history-integrity` @ `672f221c0a2e796ba30d685d2cad68a5552c8333`; CI run `36372479310` passed.
- [World & Simulation] Making & Building branch ready for integration review: `simulation/v0.5-making-building` @ `eadea56841469a29e8078f5eca23247b13317251`; CI run `36372834945` passed independently.
- [Assets & Interface] Layout/chat/History branch ready: `assets/v0.5-making-ui` @ `da3b579bb42fb86a171470dd93946c01a80b0fc1`.
- [Memory & Social] Project-continuity audit complete. Existing Memory source model is sufficient; Communication preserved canonical conversation IDs, and Simulation now exposes stable project/job outcome IDs in its branch.
- [Communication & Perception] Deeper claim-level `PROVENANCE_CONTRACT.md` remains ready for a later milestone.

### REVIEW

- [Communication & Perception] Final handoff audit complete. Conversation source continuity is compatible with Memory, and Assets' stored-conversation History renderer is compatible. Cross-branch Simulation conflict is explicitly documented.
- [World & Simulation] Physical v0.5 implementation is individually tested, but coordinator merge must preserve Communication's talk invariant.
- [Assets & Interface] Independent UI slice is complete; final physical-state visualization remains after merged state is available.
- [Memory & Social] No v0.5 runtime schema change needed yet; physical project/outcome memories can later reference integrated Simulation IDs.

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

1. combine Simulation's physical v0.5 schema/behavior with Communication's source-linked talk persistence
2. preserve canonical `citizen_conversations.id`
3. preserve nullable unique `citizen_conversations.source_job_id`
4. ensure a talk with no stored exchange fails rather than completing successfully
5. run `tests/smoke_v040.py`, `tests/smoke_v050.py`, and `tests/smoke_v050_communication.py`
6. expose the merged Making & Building state to Assets and finish the restrained physical-state UI
7. keep Memory project discussion distinct from validated physical project outcomes

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
