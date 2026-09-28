# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

_None currently. The v0.4 Control Room + map readability request has been implemented on `assets-v0.4-control-room` and moved to Outbox for runtime review._

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
