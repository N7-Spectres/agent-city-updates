# Assets & Interface — State

_Last updated: 2026-09-28_
_Current shipped release: v0.6.0_
_Current department branch: `assets/v0.6-knowledge-ui`_
_Current branch head: `8a1c7e12a6727da7d05403b9a2ae553ccc4f1dea`_
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
- branch is 6 commits ahead / 0 behind the shipped v0.5.0 base
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

### Memory & Social — Consumed

Memory delivered `memory/v0.6-location-knowledge`.

Assets now consumes:
- `GET /api/knowledge/citizens/{citizen_id}`
- `GET /api/knowledge/locations/{location_id}`

Citizen knowledge stays bounded per citizen. Location notebook knowledge remains partitioned by citizen instead of being merged into a shared truth view. Verification/source/channel/time metadata is preserved when displayed.

## Current Status

Assets & Interface is **WAITING** only on Simulation and Communication v0.6 contracts.

Draft PR #3 contains the independent information-architecture work and should not be treated as the complete v0.6 UI until the safe knowledge models are consumed.

No `update.json`, release metadata, simulation rules, or hidden-state interfaces were changed by Assets.


## Work Session Closure — v0.6 Contracts Ready

This Assets work session is closed by user request.

Independent branch:
- `assets/v0.6-knowledge-ui`
- head `8a1c7e12a6727da7d05403b9a2ae553ccc4f1dea`
- draft PR #3

Implemented this session:
- Home / Citizens / Locations / Records information architecture
- compact Home citizen rows
- compact visitor map status
- dedicated Citizens character sheets
- dedicated Locations field notebook
- placeholder-safe citizen/location visuals
- backend-specific inaccessible Visit reason
- Memory bounded knowledge APIs consumed for Citizens and Locations

During final wrap-up, the remaining two upstream contracts became ready but were **not yet consumed** because the session was being stopped:

### Simulation ready
- branch: `simulation/v0.6-research-discovery`
- head: `d1ae3faf0095d22e7a730cf50b3ad6fdbcdc4b94`
- CI: `36419824468`
- ordinary `/api/state` is now knowledge-safe
- use `discoveries`, `citizen_knowledge`, `experiment_results`, `learned_processes`, and `locations[].known_facts`
- `deposits[]` now includes discovered deposits only and omits hidden reserve amount
- hidden `world_properties` must never be rendered

### Communication ready
- branch: `communication/v0.6-knowledge-provenance`
- head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- CI: `36421263078`
- `GET /api/visit/{citizen_id}` now returns `accessible`, `status`, `reason`, and structured `availability`
- status values: `available | remote | visitor_traveling | citizen_traveling | citizen_talking | citizen_busy | missing`
- remote access intentionally hides local busy/talk detail
- Memory's bounded APIs remain the preferred consumer surface for normal Citizens/Locations knowledge

## Exact Next Session Action

1. read Assets INBOX and COORDINATION
2. inspect Simulation's safe v0.6 state shape
3. replace any remaining raw v0.5 location/deposit assumptions with the safe v0.6 fields
4. add authoritative cargo capacity if Simulation exposes it in the final branch
5. consume Communication's structured `status/availability` in Visit UI
6. preserve Memory bounded knowledge as the notebook/character-sheet knowledge source
7. rerun static verification and hand off PR #3 for coordinator integration

Assets is not blocked anymore; all upstream contracts are ready. The remaining implementation simply belongs to the next Assets work session.


## Shipped v0.6.0 Integration

Assets v0.6 work is included in the published runtime:
`6092aeafd685a3ba4cb8e9d455e586771d3f6d26`.

The assembled release passed the full cross-department smoke suite. Coordinator integration preserved Simulation truth, Communication provenance, Memory bounded retrieval, and Assets safe presentation as distinct layers.
