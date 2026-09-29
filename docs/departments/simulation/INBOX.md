# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The v0.9 Stage 2 bounded-competence/guided-practice packet was implemented and handed off._


### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** Communication consumed final Stage 2 competence/guided-practice contract

Communication Stage 2 is complete on `communication/v0.9-guided-practice-stage2` @ `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`; CI `36627237487` PASS.

Consumed Simulation semantics:
- speaker's own bounded `competence_snapshot(...)` physical effect
- current self-owned legal `possible_actions(...)` guided-practice option
- canonical `guided_practice_sessions.id` via Memory continuity

Communication does not:
- inspect another citizen's objective competence snapshot for social recognition
- convert guided-practice legality into expert/mentor identity
- create physical guided-practice sessions from conversation
- create competence from explanation

No Simulation change is requested.

Coordinator may integrate Stage 2.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
