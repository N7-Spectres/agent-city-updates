# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.4 Control Room + map readability pass

**Need / Result:**
Design and implement the next substantial UI pass: move core secondary views out of the bottom drawer into an easier right-side Control Room layout, and refine the world map so route distance, location spacing, travelers, citizen clusters, visitor position, and labels are easier to read.

**Files / Interfaces:**
- static/index.html
- static/app.js
- static/styles.css
- use existing validated simulation state only

**Important constraints:**
- visuals must never invent physical state
- preserve current visitor/chat functionality
- route geometry should communicate relative travel distance more clearly
- avoid micro-patch styling; treat this as one coherent UI milestone

**Next action:**
Read department files, inspect current v0.3.0 UI, create a concrete layout/map plan, then implement on a department branch or coordinated release branch without publishing update.json unless asked.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
