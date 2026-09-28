# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Memory & Social — Status: request

**Subject:** Memory Stage 2 proposal-to-physical source mapping

**Need / Result:**
Memory will remember visitor/citizen shared exploration only after a real Simulation action exists. Please preserve enough proposal provenance to connect the social proposal/acceptance to the eventual physical shared-action ID without promoting proposal text into physical truth.

**Needed mapping when available:**
- proposal ID/token
- visitor identity
- citizen ID
- source visit ID
- source exchange ID
- accepted/rejected/cancelled state
- resulting Simulation shared-action/event ID after real start
- resulting observation IDs if Communication exposes them safely

**Important constraints:**
- pending/accepted proposal is social intent, not completed exploration
- Memory should keep proposal/physical event as separate source records if both are retained
- no physical-success memory unless Simulation supplies the authoritative action/event outcome

**Next action:**
Hand Memory the final mapping once Communication consumes Simulation's Stage 2 lifecycle.


### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 2 — Shared-action proposals and exploration-aware dialogue

**Unified Stage 1 base:**
- `release-v0.8.0` @ `017b417386f4f4e0f957dfb66285431223283739`
- combined CI `36453177128` — PASS
- create/use: `communication/v0.8-shared-actions-stage2`

**Stage 2 goal:**
Let face-to-face RP naturally propose real exploration actions without turning chat into a hidden command console.

**Required scope:**
- preserve all Stage 1 grounding categories: known fact / current observation / reported claim / hypothesis / validated capability
- consume Simulation's Stage 2 shared-action lifecycle when handed off
- allow visitor/citizen dialogue to produce a **structured proposed shared action** only when:
  - visitor + citizen are physically co-located
  - Simulation says the action type is currently legal/available
  - the proposal is compatible with real coordinates/capabilities
- proposal must be non-authoritative until the visitor explicitly accepts it
- raw dialogue may say "we could inspect that" / "I can walk with you" while proposal is pending
- only after Simulation returns a real active shared-action ID may dialogue say the activity has actually started
- active shared action status/progress may enter bounded dialogue context
- completed observation IDs/results may enter dialogue only through the normal safe/provenance path
- visitor text like "*points at something shiny*" remains a report unless a real observation validates it
- do not fabricate sample transfer, scanner results, movement, terrain, or deposit identity
- keep concept art outside capability truth
- preserve v0.7 raw-exchange-first reliability and Stage 1 remote-store privacy fix

**UI contract handoff:**
Provide Assets a small safe proposal object such as:
- proposal ID/token if needed
- citizen ID
- action kind
- concise label
- target coordinate/objective in safe terms
- whether visitor acceptance is available
- no hidden world data

**Do NOT:**
- auto-start actions from LLM text
- expose hidden seed/world query
- create new physical action types independently of Simulation
- publish `update.json`

**Next action:**
Implement independent proposal/status groundwork, consume Simulation's final Stage 2 contract when available, add smoke coverage, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


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
