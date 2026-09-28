# Assets & Interface — State

_Last updated: 2026-09-28_
_Current release: v0.4.1_
_Current department branch: `assets/v0.5-making-ui`_
_Current branch head: `71e30d3ca02edc97f5286436bc5ef03f93b77088`_
_Current review surface: draft PR #2_

## Mission

Make Agent City visually understandable and increasingly feel like a living place while never allowing the visual layer to invent physical reality.

## v0.5 Assets Scope — Complete

The v0.5 Assets branch is based from immutable runtime commit:
`4181cbb69809205ae575b3f576836e5ca72c8dce`.

It now contains the full requested Assets work.

### Compact Visit / layout

- bounded Visit panel
- internally scrolling chat log
- anchored visitor input / Talk controls
- capped Previous Visits region
- centered, rebalanced three-column desktop layout
- more usable right-side width
- responsive fixed-height interaction layout

### Conversation History

History is the default Control Room companion beneath Visit.

Conversation cards are rendered only from real `state.citizen_conversations[]` records and show:

- canonical conversation ID
- physical talk `source_job_id` when available
- participants
- location
- simulation time
- stored summary
- expandable transcript

Successful v0.5 talk completion chronology is correlated by its `conversation #<id>` reference.

Failed talk attempts remain settlement chronology only and do not receive synthetic conversation cards or transcripts.

Legacy chronology-only conversation records may still be shown explicitly when the actual exchange is outside the current state snapshot.

### Making & Building

The Control Room tab previously labeled Structures is now **Making**.

It consumes only Simulation's authoritative v0.5 snapshot state:

#### Projects — `state.projects[]`

Displayed:
- stable project ID
- exposed lifecycle status: `planned | reserved | underway | complete`
- name / blueprint-derived label
- validated location
- local x/y site coordinates when exposed
- creating citizen
- active physical job ID when exposed
- resulting structure ID after Simulation exposes it

#### Project materials — `state.project_materials[]`

Displayed:
- material
- reserved amount
- required amount

The UI does not calculate material reservation itself.

#### Equipment — `state.equipment[]`

Displayed:
- stable equipment ID
- name / kind
- owner or settlement ownership
- location
- condition
- fabrication source job ID
- explicit Simulation modifiers:
  - `cargo_bonus`
  - `extraction_speed_multiplier`

The UI does not derive bonuses from item names.

#### Structures — extended `state.structures[]`

Displayed:
- stable structure ID
- name / kind
- validated location
- condition
- local x/y coordinates when exposed
- `provides_charging`
- source project ID when exposed

Local x/y is presented as local site data only, not as free-roam world geography.

## Cross-Department Contracts Consumed

World & Simulation:
- `simulation/v0.5-making-building`
- authoritative head `773299189d22d214b3376c72b396015a4a7a762e`

Communication contract preserved through the integrated Simulation branch:
- canonical `citizen_conversations.id/source_id`
- nullable unique `source_job_id`
- successful physical talk completion requires a stored exchange
- missing exchange => failed talk, not successful conversation

Memory boundary preserved:
- conversation/project discussion is not proof of physical project progress or completion

## Verification Performed

Static branch verification:

- 47 HTML IDs
- 47 JavaScript `getElementById` references
- zero missing IDs
- zero duplicate IDs
- zero stale bottom-drawer hooks
- JavaScript parsed successfully
- branch is 7 commits ahead / 0 behind pinned v0.4.1 base
- changed runtime files are only:
  - `static/index.html`
  - `static/app.js`
  - `static/styles.css`
- Simulation branch changes no `static/` files, so there is no direct frontend file overlap during coordinator integration

## Integration Status

Assets & Interface is now **REVIEW**, not ACTIVE or WAITING.

Draft PR #2:
**Assets: v0.5 compact interaction, History, and Making UI**

Next action belongs to coordinator integration:

1. combine `simulation/v0.5-making-building` with `assets/v0.5-making-ui`
2. smoke-test the assembled runtime with real v0.5 state
3. verify Making tab against actual projects/equipment/structures
4. preserve canonical conversation-source invariants
5. keep `update.json` untouched unless the human explicitly requests release publication

No simulation rules or release metadata were changed by Assets.
