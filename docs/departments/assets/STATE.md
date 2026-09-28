# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.5.0_
_Current department branch: `assets/v0.6-knowledge-ui`_
_Current branch head: `280417e7361d888c7bd740c80f436493a13d85a1`_
_Current review surface: draft PR #3_

## Mission

Make Agent City visually understandable and increasingly feel like a living place while never allowing the visual layer to invent physical reality or hidden knowledge.

## v0.6 Independent Information Architecture — Implemented

Branch base:
`release-v0.5.0` / `d5bb929ef8def630afcbfbc07d90a51dd6c80cc8`

### Home

Home is simplified to the core visit experience:

- compact citizen quick list
- central world map remains primary
- selected-citizen Visit remains immediately accessible
- visitor physical location is a compact map-corner status
- duplicate region strip is removed from Home
- permanent Making / Stores / History / Updates console is removed from Home

Quick citizen rows now emphasize only high-value live state:

- name
- activity
- location / travel destination
- carried cargo
- compact energy / integrity

### Citizens

Dedicated character-sheet page added.

Current safe v0.5-backed fields include:

- placeholder-safe full-body identity slot
- aptitude
- location / travel state
- activity / active job
- energy / integrity
- carried cargo
- validated personal equipment
- explicit equipment modifiers
- projects created by the citizen
- personally confirmed discoveries only
- recent authoritative chronology

Appearance art and richer configuration remain placeholder-safe until an authoritative source exists.

### Locations

Dedicated field-notebook page added.

Current safe v0.5-backed fields include:

- placeholder-safe scene slot
- survey state
- discovered resources only
- physically present citizens
- validated structures
- validated projects
- known routes

Unknown resources/properties are omitted rather than shown as locked secrets.

### Records

Making / Stores / History / Region / Updates are now moved to a dedicated top-level Records page.

### Visit status polish

When a visit is inaccessible, the UI now shows the backend's actual reason instead of always displaying the generic "Not at the same location" label.

## Verification

Static verification on `assets/v0.6-knowledge-ui`:

- 65 HTML IDs
- 60 JavaScript `getElementById` references
- zero missing referenced IDs
- zero duplicate IDs
- JavaScript parses successfully
- branch is 4 commits ahead / 0 behind the shipped v0.5.0 base
- changed runtime files are only:
  - `static/index.html`
  - `static/app.js`
  - `static/styles.css`

## Waiting Dependencies

The independent UI shell is complete. Remaining v0.6 data-driven work is waiting on three owner contracts.

### World & Simulation

Requested:
- knowledge-safe world/location read model
- discovery/experiment anchors
- authoritative per-citizen cargo capacity
- guidance on which raw v0.5 fields must no longer be used directly once hidden truth exists

### Communication & Perception

Requested:
- stable structured visit accessibility semantics
- display-safe provenance/source/age fields
- distinction between direct observation/discovery and communicated claim

### Memory & Social

Requested:
- bounded per-citizen known-fact read model
- location/material/research/process knowledge
- source/time/verification metadata
- no global omniscient encyclopedia

All three requests are recorded directly in the owning department INBOX files.

## Current Status

Assets & Interface is **WAITING** on those v0.6 contracts.

Draft PR #3 contains the independent information-architecture work and should not be treated as the complete v0.6 UI until the safe knowledge models are consumed.

No `update.json`, release metadata, simulation rules, or hidden-state interfaces were changed by Assets.
