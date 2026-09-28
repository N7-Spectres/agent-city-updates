# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None currently for Communication Stage 1._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 1 — Grounded visitor RP and capability language

**Result:**
Implemented/tested on `communication/v0.8-grounding-stage1`.

Delivered:
- evidence-status grounding vocabulary
- visitor-claim treatment
- authoritative runtime capability context
- concept-art/non-runtime equipment boundary
- shared-action intention vs physical-start boundary
- remote Seed Site inventory live-state leak fix
- planner/autonomous dialogue grounding
- safe Simulation Stage 1 spatial context
- future shared-action contract

Final branch head:
`a95e7af23eddaeb018bd6b2b6f19681a227e92af`

Final green CI:
`36450386273`

### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** v0.8 Stage 1 spatial/shared-action contract

**Result:**
Communication aligned to:
- `seed_site_local`
- meter coordinates
- `spatial_observations.id`
- observation `radius_m` precision semantics
- stable deposit subjects after validated exposure

Hidden spatial query output remains forbidden as dialogue evidence.

Simulation confirms Stage 1 intentionally contains no visitor-linked shared physical action or arbitrary meter/free-roam/scan action.

## Waiting for a Future Stage 2 Contract

Real visitor-linked physical actions require Simulation to define:
- participant binding
- co-location/proximity legality
- movement/path/point legality
- duration/energy/tool requirements
- action lifecycle
- stable action/event IDs
- resulting observation IDs

This does not block Stage 1 review.

## Deferred Communication Depth

- structured visitor-claim extraction if later justified
- shared visitor/citizen actions after Simulation Stage 2
- spatial last-known movement propagation
- social place naming/alias propagation
- claim contradiction/reliability
- overhearing / physical records / invented long-distance communication

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
