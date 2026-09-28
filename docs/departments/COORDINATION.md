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

_None recorded at Memory & Social session close._

### STANDBY

_None recorded._

### WAITING

- [Memory & Social] Next social-memory layer waits for Communication provenance and Simulation validated-event interfaces

### READY

- [Communication & Perception] Full v0.3.0 runtime source located at commit `40f9704b7e84e2dd6279932223105ae93d9fef49`; provenance runtime work can resume from that lineage
- [World & Simulation] Full v0.3.0 runtime source located; Memory and Communication event/interface requests are in Simulation inbox

### REVIEW

- [Memory & Social] v0.4 social-memory core on `memory/v0.4-social-memory-core` at `eb1ccc17e2fc7a44a15fbb73c44fc2b87d47f997`; runtime migration/Ollama tests required before release
- [Communication & Perception] Planner anti-omniscience patch + v0.4 provenance contract
- [Assets & Interface] v0.4 Control Room + map readability pass on `assets-v0.4-control-room`; static checks passed, runtime UI test required

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
