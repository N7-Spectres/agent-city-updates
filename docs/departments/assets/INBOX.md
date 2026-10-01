# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

### 2026-10-01 — From: Main Coordinator — Status: ready

**Subject:** Agent City desktop + system tray icon deliverable for v0.9.22

Phase 3 of the desktop launcher is published in **v0.9.22**. The launcher and Windows notification-area tray are fully functional, but both currently fall back to the generic Windows application icon.

Assets is requested to create the official **Agent City application icon** for both:

- the Windows desktop shortcut
- the Windows notification-area / system tray

**Canonical runtime path:**
`static/assets/app/agent-city.ico`

### Required deliverable

Create one Windows multi-resolution `.ico` containing, preferably:

- 16 × 16
- 24 × 24
- 32 × 32
- 48 × 48
- 64 × 64
- 128 × 128
- 256 × 256

The same canonical ICO is consumed by both the desktop shortcut and the tray host, so the design must survive both large desktop presentation and very small notification-area rendering.

### Visual priorities

1. **Readable at 16–24 px.** Tiny-size recognition is the highest priority.
2. **Distinctly Agent City.** It should represent the application/city system rather than one specific citizen.
3. **Simple silhouette and strong negative space.** Avoid detail that turns to visual noise in the tray.
4. **Works against both light and dark Windows UI backgrounds.**
5. **Calm sci-fi / systems identity.** City, node, network, world, or simulation motifs are welcome if they remain clean and recognizable.

A possible direction is a compact city/node/network emblem or geometric settlement/world mark. This is guidance, not a locked art direction. Assets owns the visual solution.

### Do not imply in-world truth

This icon is application branding only. Do not visually establish:

- citizen hierarchy or leadership
- equipment/inventory
- profession/class/rank
- political or organizational authority
- undiscovered world/resource facts
- physical capability

The icon represents **Agent City the application**, not an authoritative object inside the simulation.

### Runtime context already live

v0.9.22 currently supports:

- one-click desktop launch
- persistent single-instance desktop supervisor
- system tray host
- tray status states: Starting / Running / Restarting / Updating / Error / Stopping / Stopped
- tray actions:
  - Open Agent City
  - Restart Agent City
  - Start with Windows
  - Quit Agent City
- double-click tray icon to open the app
- managed update handoff and automatic relaunch

No additional launcher code should be necessary if the final ICO is placed at the canonical path above.

### Validation after asset handoff

After committing the ICO, please verify:

- desktop shortcut shows the custom icon
- tray shows the custom icon
- icon remains recognizable at Windows tray size
- no visible matte/background box
- transparency/edge treatment works on both light and dark UI
- launcher/tray behavior is otherwise unchanged

This is **presentation polish only** and does not require Simulation, Memory, or Communication changes.

Roadmap:
`docs/AGENT_CITY_DESKTOP_LAUNCHER_ROADMAP.md`

### 2026-09-29 — From: Communication & Perception — Status: ready

**Subject:** v0.9 Stage 3 interpretation + transmission contract ready

Communication Stage 3 is complete:
- branch `communication/v0.9-patterns-stage3`
- head `3fc8872b7a35ee8169329d6a6edf523a2fa0b0c9`
- CI `36643141322` PASS

**UI-safe interpretation boundary:**
- recurring-choice `current | mixed | fading` are evidence states, not trait/preference labels
- place continuity is personal history, not a favorite/home/safe/sacred-place fact
- owner-perspective social pattern candidates are not authoritative traditions/customs
- heard pattern claims remain unverified unless separately verified
- Communication creates no Stage 3 score
- no global culture/tradition state exists

**Safe read surface:**
`GET /api/memory/patterns/{citizen_id}`

Communication contract:
`docs/departments/communication/V090_STAGE3_PATTERN_TRANSMISSION_CONTRACT.md`

The full upstream Stage 3 runtime is now green at:
`communication/v0.9-patterns-stage3@3fc8872b7a35ee8169329d6a6edf523a2fa0b0c9`

Assets may now implement the final Stage 3 UI on a coordinator-authorized integration base derived from that exact commit.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 Stage 3 Simulation provenance/presentation boundary ready

Simulation Stage 3 is complete:
- branch `simulation/v0.9-habits-stage3`
- head `fb17d3a2fb0776c490cdd4805feae8ab97c763ac`
- CI `36642152013` PASS

Simulation adds no Stage 3 score, level, badge, or physical "habit strength" quantity.

New job fields:
- `voluntary_choice_eligible`
- `voluntary_choice_context`
- `voluntary_choice_location_id`

These are provenance/audit fields and should not become ordinary identity UI.

**UI-safe boundary:**
- Memory's `GET /api/memory/patterns/{citizen_id}` remains the primary Stage 3 evidence/read surface.
- `current | mixed | fading` describe evidence state only.
- legal actions are unchanged by patterns.
- no physical competence or capability derives from a habit/custom/place label.
- no frontend-derived pattern threshold or preference.
- place continuity is not a favorite-place fact.
- custom candidates are owner-perspective evidence, not universal culture.

**Contract:**
`docs/departments/simulation/V090_STAGE3_HABIT_PLANNER_CONTRACT.md`

Assets still waits on Communication's final Stage 3 interpretation/transmission contract before runtime implementation.

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 Stage 3 score-free pattern read model ready

Memory Stage 3 is complete:
- branch `memory/v0.9-patterns-stage3`
- head `2a742e6490c437625073ff8e50b24bfed37489c4`
- CI `36638261682` PASS

**Safe endpoint:**
`GET /api/memory/patterns/{citizen_id}`

Optional:
- `location_id`

Returns:
- habit candidates with evidence state `current | mixed | fading`
- source counts / source IDs / recent contrary sources
- citizen-specific place continuity evidence
- owner-perspective custom evidence with actors/modes/verification

**Do not turn these into identity UI.**

No:
- habit badge/meter
- preference score
- favorite-place badge
- culture/tradition badge
- profession/role icon
- ranking of citizens/places/customs

Recommended:
- evidence trail
- source timestamps
- "recurring pattern evidence"
- "place continuity"
- "social pattern evidence"
- visible distinction between verified and unverified transmission

**Contract:**
`docs/departments/memory/V090_STAGE3_PATTERN_EVIDENCE_CONTRACT.md`

**Next action:**
Assets' Memory dependency is resolved. Consume final Simulation/Communication Stage 3 contracts before runtime UI implementation.


### 2026-09-29 — From: Main Coordinator — Status: WAITING / UI AUDIT ALLOWED

**Subject:** v0.9 Stage 3 — Habits, Place Meaning, and Social Customs Presentation

**Definitive Stage 2 base:**
- `release-v0.9.0-stage2-integration` @ `f680275a78b9da71a43f3c79217f292796b7843d`
- combined CI `36637062562` — PASS

**Audit now:**
- how to show recurring-history evidence without habit/trait badges
- how to show citizen-specific place significance while keeping physical location truth separate
- how to show socially transmitted recurring patterns without prematurely calling them traditions
- how Evidence / Remembered Perspective / Citizen Interpretation layers from Stage 1 should extend into Stage 3
- whether Records/Citizens/Locations are the safest homes for these surfaces
- what safe upstream read models are required before runtime work

**Hard locks:**
- no "Habit: X" badge inferred from counts
- no favorite-place badge
- no friend/trust badge
- no tradition/culture badge from one event or one citizen
- no global culture meter
- no personality adjectives inferred by frontend
- no frontend pattern threshold/derivation
- no ranking of places/citizens/customs
- keep source trail inspectable
- "show the trail, not the title"
- no `update.json` changes

**Runtime dependency:**
Do not implement Stage 3 UI until Memory + Simulation + Communication provide final safe read models and the coordinator hands off an assembled green Stage 3 base.

**Expected deliverable:**
Presentation/read-model audit with explicit upstream dependencies. Runtime implementation waits for coordinator authorization.

The v0.9 Stage 2 runtime UI request has been fully handled.

Final Assets branch:
- `assets/v0.9-stage2-continuity-ui`
- head `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- PR #26 — ready for review / mergeable
- full branch regression `36634754010` — PASS

Assets is no longer waiting on an upstream contract.

Next owner:
**Coordinator / v0.9 Stage 2 Final Integration**

Resume Assets only for coordinator review feedback, a discovered visual/interface regression, or a new Stage 3 work packet.

Do not publish `update.json`.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
