# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Memory Stage 2 shared exploration event source

**Need / Result:**
Memory has completed the independent Stage 2 work that surfaces retained nearby exploration memories in planning/dialogue. The remaining visitor-participation continuity must bind to a real Simulation-owned shared action, never chat agreement.

**Needed stable fields:**
- shared action/event ID
- citizen participant ID
- visitor participant identity
- source visit ID / exchange ID if Simulation stores them
- action kind / objective
- authoritative start and completion simulation minute
- start/target/final coordinate or safe objective reference
- status / outcome
- any resulting `spatial_observations.id` values
- stable job/action ID if distinct from shared-event ID

**Important constraints:**
- Memory will not create a shared exploration memory from a proposal or acceptance token alone
- only physically started/completed Simulation records can become shared-event continuity
- no bystander propagation
- observation memories remain sourced to `spatial_observations.id`
- shared-event memory may reference those observations but must not replace their evidence identity

**Next action:**
When the Stage 2 shared-action lifecycle stabilizes, hand Memory the exact table/field names and completion semantics.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 2 — Continuous local exploration + shared physical activity

**Unified Stage 1 base:**
- branch: `release-v0.8.0`
- commit: `017b417386f4f4e0f957dfb66285431223283739`
- combined CI: `36453177128` — PASS
- create/use: `simulation/v0.8-exploration-stage2`

**Stage 2 goal:**
Turn the seeded spatial substrate into a real exploration lifecycle. Citizens and visitors should be able to move through local meter-space and create validated observations without dialogue creating reality.

**Required scope:**
- add a Simulation-owned local movement/exploration action targeting a real `seed_site_local` x/y coordinate
- persist authoritative movement start/target coordinates and job lifecycle
- position during active local movement must be derivable from the real job, not UI guesswork
- movement duration/energy should use real distance and hidden terrain/traversal cost as appropriate
- preserve the energy-return reserve so citizens are not allowed to begin local exploration that strands them from a known operational charger
- keep existing landmark route travel working; do not break legacy saves/routes
- add a validated local inspect/field-observation action that records `spatial_observations` at the actual coordinate
- observation result must reveal only the level supported by the physical action/tool; do not expose hidden richness/body geometry
- same seeded deposit body must retain the same stable `deposit_id`
- no independent reroll per observation
- define a narrow **visitor-linked shared activity** lifecycle for physically co-located visitor + citizen:
  - proposal/acceptance is separate from physical start
  - Simulation validates participants, coordinate/path, duration, energy/tool requirements, status, outcome, and observation IDs
  - chat text alone never starts movement
- include an explicit way for the visitor to accept/start a valid shared activity after Communication/UI presents it
- shared activity should support at minimum a short local walk/inspect objective
- add stable IDs/source links so Communication/Memory/History can follow the action
- migrate v0.7/Stage 1 saves additively

**Tool/scanner boundary:**
- do not grant a scanner
- if a future/real equipped tool exposes a validated capability, the action contract may accept that capability
- ordinary local inspection may use only baseline direct observation and must not infer chemistry/material properties beyond what the action can physically reveal

**Do NOT yet:**
- implement planetary globe travel
- replace the entire route network
- add citizen-created place naming
- add emergent invention recipes
- publish `update.json`

**Acceptance direction:**
- citizen can move to a nearby arbitrary coordinate and their authoritative position updates over time
- visitor can explicitly accept a citizen's valid shared local walk/inspection and both participants follow one Simulation-owned lifecycle
- an observation at arrival/inspection produces safe stable evidence
- same coordinate remains deterministic
- same deposit encountered nearby retains same subject ID
- closing/reopening preserves positions/jobs safely
- old named locations remain intact

**Handoff needed:**
Send Communication the shared-action proposal/start/status contract, Memory the action/observation source IDs, and Assets the authoritative movement/position interpolation fields.

**Next action:**
Implement/test Stage 2 physical exploration, update Simulation STATE/DECISIONS/BACKLOG/OUTBOX and dependent INBOXes, then stop for coordinator review.


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
