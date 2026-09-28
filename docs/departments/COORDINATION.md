# Agent City — Department Coordination Board

_Last updated: 2026-09-28_

This file is the shared coordination board for Agent City departments.

The main coordinator may update this file to route dependencies, record active work, and show what is ready for another department.

Departments should read this file at the beginning of a work session in addition to their own INBOX.

## Status Key

- **ACTIVE** — currently being worked
- **WAITING** — blocked on another department
- **READY** — dependency or deliverable is ready for pickup
- **REVIEW** — work is complete enough for coordinator review
- **DONE** — finished and incorporated

## Current Board

### ACTIVE

- [World & Simulation] v0.5.0 lead: fabrication, construction, project state, physical tool/carry effects, energy-return reserve, coordinate groundwork

### STANDBY

_None. v0.5.0 work packet is active._

### WAITING

- [Memory & Social] conversation-source audit dependency is satisfied by Communication; still waiting for Simulation stable project/event IDs before any project-outcome runtime hooks
- [Assets & Interface] independent v0.5 chat/layout/History slice is ready in draft PR #2; Communication History shape is now available, but Assets still waits on World & Simulation's final project/tool/equipment/structure schema for Making & Building UI

### READY

- [Assets & Interface] Communication delivered stable citizen-conversation History shape and success/failure semantics
- [Memory & Social] Communication preserved canonical `citizen_conversations.id` and added optional physical `source_job_id`
- [World & Simulation] Communication talk-completion invariant is ready to preserve during `simulation.py` integration
- [Communication & Perception] Provenance contract remains ready for a later deeper claim/last-known pass
- [World & Simulation] Stable completed job IDs remain candidate authoritative event references for later cooperation/help memories

### REVIEW

- [Communication & Perception] v0.5 conversation-history integrity ready on `communication/v0.5-history-integrity` head `672f221c0a2e796ba30d685d2cad68a5552c8333`; CI run `36372479310` passed
- [Memory & Social] v0.5 project-continuity contract/audit ready for coordinator review; no runtime branch required yet

### DONE

- [Coordinator] v0.4.0 assembled on `release-v0.4.0`, tested, versioned, and published
- [Coordinator] v0.4.1 blank-reply conversation hotfix tested and published
- [Memory & Social] Durable directional conversation memory + bounded social context
- [Assets & Interface] Control Room redesign + distance-aware map readability pass
- [Communication & Perception] Information-boundary rules / anti-omniscience architecture preserved; provenance contract documented
- [World & Simulation] Existing validated jobs/physical state preserved unchanged for this milestone
- [Communication & Perception] Same-location citizen talk system
- [World & Simulation] Visitor physical presence and travel
- [Assets & Interface] v0.3.0 live job progress and moving map markers
- [Memory & Social] Persistent visitor visits and bounded conversation context

## Handoff Protocol

When Department A needs Department B:

1. Department A writes a concise request to Department B's `INBOX.md`.
2. Department A records itself as **WAITING** here if the dependency blocks progress.
3. Department B reads its INBOX at the beginning of its next work session.
4. Department B completes the work or records why it cannot.
5. Department B writes the result to its own `OUTBOX.md` and, when useful, directly to Department A's `INBOX.md`.
6. The main coordinator reviews the handoff and updates this board.

## Message Format

Use this compact format for inbox/outbox entries:

### YYYY-MM-DD — From: <department> — Status: <request|ready|blocked|note>

**Subject:** short title

**Need / Result:**
Concise description.

**Files / Interfaces:**
- relevant file
- relevant field/API/schema

**Important constraints:**
- rule that must not be violated

**Next action:**
What the receiving department should do.

## Coordinator Rule

The coordinator may route work between departments through these files, but no department should silently redefine another department's core rules.

Cross-department changes must still obey:

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**
