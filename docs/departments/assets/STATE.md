# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.6.0_
_Current department branch: `assets/v0.7-home-avatars`_
_Current branch head: `f1b356100711a53ab2d7884009f84308b95ce5ce`_
_Current review surface: draft PR #7_

## Mission

Make Agent City visually understandable and alive while never allowing presentation to invent physical state, hidden knowledge, wear, damage, equipment, or outcomes.

## v0.7 Independent Assets Work — Implemented

Branch base:
`release-v0.6.0` / `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`

### Home scaling

Desktop Home now uses one shared height budget for:

- citizen rail
- center world panel
- Visit/chat rail

Citizen rail:
- internal scrolling
- citizen name search/filter
- future-population-ready layout

Visit rail:
- full-height desktop panel
- internal chat scrolling
- anchored visitor input/actions

Smaller screens keep the existing stacked/responsive behavior.

### Recent Activity

Home now includes a compact five-item Recent Activity surface beside the focused-location card.

It combines:

- meaningful chronology events
- concise summaries from real stored `citizen_conversations`

Rules:

- successful conversation begin/completion chronology is filtered when the stored exchange summary exists
- failed talk attempts remain ordinary events
- routine observe/wait churn is filtered from the Home summary
- "View all history" opens Records → History

No conversation summary is synthesized from a failed or missing exchange.

### Avatar first stage

Added lightweight 2D/static identity infrastructure without Mixamo or 3D.

Supported surfaces:

- Citizens page full-body identity area
- Home citizen quick rows
- Citizens directory
- map citizen markers

The avatar manifest supports future full/token art without redesign.

Current fallback:

- neutral mechanical silhouette / token
- initials
- per-citizen interface accent hue

The accent hue is UI identity, not physical paint or appearance.

State animation derives only from validated active jobs:

- idle
- traveling
- charging
- talking
- working

Reduced-motion user preference disables animation.

No equipment, wear, or damage is drawn unless an authoritative physical state supports it.

## Verification

Static verification on `assets/v0.7-home-avatars`:

- 69 HTML IDs
- 65 JavaScript `getElementById` references
- zero missing referenced IDs
- zero duplicate IDs
- JavaScript parsed successfully
- branch is 3 commits ahead / 0 behind shipped v0.6.0
- changed runtime files only:
  - `static/index.html`
  - `static/app.js`
  - `static/styles.css`

## Waiting Dependency — Maintenance

Assets sent a direct request to World & Simulation for the final v0.7 maintenance presentation contract.

Needed before condition UI is completed:

- equipment wear/condition/service fields
- structure wear/condition/service fields
- battery / power-storage health
- explicit degraded / maintenance-needed / failed semantics if owned by Simulation
- maintenance/service/repair/replacement timestamps or event/job IDs
- guidance on meaningful Home alert thresholds

Memory guidance is already recorded:

- show current condition from Simulation
- do not render every wear tick as Recent Activity
- later maintenance history should include meaningful validated service/failure/repair/replacement only
- admin physical state does not imply a citizen remembers the event

## Current Status

Assets & Interface is **WAITING** on World & Simulation's v0.7 maintenance schema.

Draft PR #7 contains the complete independent Home/avatar/Recent Activity slice.

No `update.json`, release metadata, hidden knowledge rules, or physical simulation rules were changed by Assets.
