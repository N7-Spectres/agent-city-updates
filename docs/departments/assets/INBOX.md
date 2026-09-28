# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

_None._

The v0.8 Stage 1 coordinator request is complete on:
- branch `assets/v0.8-visual-stage1`
- head `af2e058780103755360d143ca964855145e2254a`
- PR #11, ready for review

World & Simulation's Stage 1 spatial contract has been received and recorded in Assets STATE/DECISIONS/BACKLOG. Do not begin continuous-world UI wiring until the coordinator authorizes the next stage.

Optional v0.7 Memory maintenance-history API remains available for future citizen-history enrichment but is not required for current physical-state presentation.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
