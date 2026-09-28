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

- [Memory & Social] Lead v0.4.0 relationship-memory architecture and implementation
- [Assets & Interface] v0.4 Control Room + map readability pass
- [Communication & Perception] Information provenance / last-known knowledge support for v0.4

### STANDBY

- [World & Simulation] Wait for concrete dependencies from Memory, Communication, or Assets before changing core physical rules

### WAITING

_None recorded yet._

### READY

_None recorded yet._

### REVIEW

_None recorded yet._

### DONE

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
