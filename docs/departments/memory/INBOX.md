# Memory & Social — Inbox

_Read this at the beginning of each Memory & Social work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** Lead v0.4.0 Memory & Relationships architecture

**Need / Result:**
Design the core v0.4.0 social-memory system around behavior already emerging naturally. Focus on durable interaction history, familiarity, cooperation, disagreement, promises, help, and information-source reliability without turning relationships into arbitrary RPG scores.

**Files / Interfaces:**
- inspect current conversations / citizen_conversations / visits schema
- propose or implement a bounded event-memory model
- identify the exact simulation/communication fields needed from other departments

**Important constraints:**
- conversation claims are not physical truth
- full history may remain archived, but LLM context must stay bounded
- preserve current citizen continuity and existing v0.3.0 data

**Next action:**
Read department state/decisions/backlog, inspect the current implementation, then produce the recommended v0.4 architecture and write any cross-department dependencies to the relevant inboxes.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
