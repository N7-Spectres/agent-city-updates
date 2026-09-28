# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The active v0.8 Stage 1 seeded-spatial-world work packet was implemented and handed off._


### 2026-09-28 — From: Communication & Perception — Status: request

**Subject:** Stage 2 visitor-linked physical action lifecycle

**Need / Result:**
Communication Stage 1 is complete and aligned to Simulation's `seed_site_local` coordinates and `spatial_observations.id`.

No real shared visitor movement/survey was wired in Stage 1 because Simulation correctly exposes no visitor-linked shared action yet.

For Stage 2, Communication needs a Simulation-owned action interface/lifecycle sufficient for conversationally proposed activities such as:
- move/walk a short local distance together
- inspect/survey a nearby point
- use an actually available tool on a nearby subject
- perform a shared local observation

**Communication can supply:**
- visitor identity
- citizen identity
- source visit ID
- source exchange ID
- requested objective/direction/point
- requested tool/equipment ID when applicable
- visitor request text
- citizen response/intention

**Simulation must decide:**
- participant/co-location/proximity legality
- whether the action exists/is legal
- authoritative path/point
- duration
- energy/tool requirements
- start/status/failure/completion
- participant positions
- physical outcome
- stable action/event ID
- any validated `spatial_observations.id` created by the activity

**Important constraints:**
- chat agreement must never directly mutate coordinates or create observations
- hidden world query output remains Simulation-only
- concept art never satisfies tool/equipment requirements
- Stage 1 review is not blocked by this request

**Next action:**
Define this lifecycle only when Stage 2 is authorized. Communication will then bind conversational proposals to real Simulation actions without making chat an admin console.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
