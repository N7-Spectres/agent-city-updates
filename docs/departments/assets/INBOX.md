# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

_None. The v0.8 Stage 1 independent Assets request has been implemented and handed off through PR #11._

Continuous-world UI has an outgoing dependency request in World & Simulation INBOX. Resume that work only after Simulation returns its safe seeded spatial read model.

The optional v0.7 Memory maintenance-history API remains available for future enrichment but is not required for current physical-state presentation.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
