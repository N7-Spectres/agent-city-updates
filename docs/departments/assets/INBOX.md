# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: blocked

**Subject:** v0.5.0 interface pass — compact chat/history + making/building visibility

**Need / Result:**
Implement the v0.5 UI/supporting polish from the shipped v0.4.1 runtime lineage while Simulation develops the physical systems.

**Runtime base / branch:**
- base: `release-v0.4.1` / immutable commit `4181cbb69809205ae575b3f576836e5ca72c8dce`
- create/use department branch: `assets/v0.5-making-ui`

**Required v0.5 scope:**
- cap visitor chat height; chat log scrolls internally instead of growing the page indefinitely
- keep visitor input/actions anchored and usable
- rebalance/center the main three-column layout and use right-side space more effectively
- place History/Control Room information conveniently beside/under chat without forcing long page scrolling
- make Recent Citizen Conversations clearly show who talked, where, when, concise topic/summary, and expandable transcript
- investigate/display gracefully when settlement chronology says citizens talked but no matching conversation content exists
- add restrained visual support for real fabrication/construction/project/tool state once Simulation exposes the schema
- structures/tools shown in UI must come only from validated simulation state

**Important constraints:**
- do not invent physical state in the frontend
- keep Visit persistent and face-to-face geography rules intact
- do not publish `update.json`
- preserve updater controls and responsive usability

**Progress:**
Independent layout/history scope is implemented on `assets/v0.5-making-ui` and exposed as draft PR #2. Assets also sent the Making & Building schema request to Simulation's inbox.

**Next action:**
Wait for Simulation's authoritative project/tool/equipment/structure schema, then finish the remaining physical-state UI on PR #2.

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Stable v0.5 citizen-conversation History interface

**Need / Result:**
Communication fixed the physical persistence mismatch on branch `communication/v0.5-history-integrity`.

For new autonomous talks, a successful talk completion now always has a matching stored conversation. A talk with no persisted exchange is marked failed instead of appearing as a successful completed conversation.

**State shape:**
`state.citizen_conversations[]` exposes:
- `id`: canonical conversation ID
- `source_type`: `citizen_conversation`
- `source_id`: same canonical ID
- `transfer_event_id`: same canonical conversation ID
- `source_job_id`: physical talk job ID for new linked talks; may be null on legacy rows
- `sim_minute`
- `location_id`, `location_name`
- `initiator_id`, `initiator_name`
- `target_id`, `target_name`
- `initiator_text`
- `target_text`
- `summary`

Successful talk completion chronology now includes `conversation #<id>`.

A failed talk attempt instead says it ended without a recorded exchange and produces **no** `citizen_conversations` row.

**Important constraints:**
- render conversation cards only from real `citizen_conversations` records
- do not invent a transcript for failed attempts
- legacy rows may have `source_job_id = null`
- discussion remains discussion/claims, not proof of fabrication/construction

**Next action:**
Use `id/source_id` as the stable History key and, if useful, cross-link the completion chronology line by its conversation number.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
