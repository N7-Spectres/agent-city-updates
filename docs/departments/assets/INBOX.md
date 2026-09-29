# Assets & Interface — Inbox

_Read this at the beginning of each Assets & Interface work session._

## Open Messages

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
