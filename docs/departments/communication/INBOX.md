# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** Strengthen information provenance for v0.4

**Need / Result:**
Prepare Communication & Perception for relationship memory by making direct observation, communicated information, and last-known remote information explicit enough that Memory can safely reason about who knew what and why.

**Files / Interfaces:**
- inspect agent_city/comms.py and prompt context boundaries
- define source / age / provenance fields or events Memory can consume
- audit for any remaining accidental omniscience

**Important constraints:**
- no free remote communication
- no radios/networks unless the civilization later invents and physically builds them
- communicated claims remain claims until physically verified

**Next action:**
Read department files, audit current information flow, then implement or specify the minimum provenance layer needed for v0.4 and send any required Simulation dependencies to its inbox.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
