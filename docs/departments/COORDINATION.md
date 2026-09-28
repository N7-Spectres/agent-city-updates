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

_None. v0.4.0 integration/release is complete._

### STANDBY

- [All departments] Await next coordinated milestone.

### WAITING

_None blocking the v0.4.0 release._

### READY

- [Communication & Perception] Provenance contract is ready for a later deeper social-memory pass.
- [World & Simulation] Stable completed job IDs remain available as candidate authoritative event references for later cooperation/help memories.

### REVIEW

_None. Coordinator integration smoke test passed for v0.4.0._

### DONE

- [Coordinator] v0.4.0 assembled on `release-v0.4.0`, tested, versioned, and published
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
