# Communication & Perception — State

_Last updated: 2026-09-28_
_Current release: v0.4.1_

## Mission

Model how information can physically reach a citizen.

This department covers:

- speech
- hearing
- direct observation
- local presence
- information transfer
- last-known knowledge
- future signaling / communication systems

## Current Shipped Behavior

### Citizen awareness

Citizens know the other five citizens exist.

They do **not** receive live omniscient status for remote citizens.

Planner context exposes:

- the citizen's own state
- co-located citizens as directly observable presence
- personally known/local information permitted by the communication boundary
- legal actions supplied by Simulation
- bounded social history sourced from real stored encounters

Remote live status is not injected into citizen prompts.

### Direct observation

A citizen can directly observe other citizens at the same location.

Traveling citizens are not treated as still locally visible at their origin.

Direct observation does not expose private plans, hidden internal state, or remote knowledge.

### Citizen-to-citizen talk

Same-location available citizens may autonomously choose a face-to-face `talk` action.

The shipped v0.4.1 runtime creates a physical talk job, generates a short exchange, stores `citizen_conversations`, and later completes the job.

## v0.5 Conversation-History Integrity Slice

**Branch:** `communication/v0.5-history-integrity`  
**Base:** shipped v0.4.1 commit `4181cbb69809205ae575b3f576836e5ca72c8dce`  
**Branch head after cleanup:** `672f221c0a2e796ba30d685d2cad68a5552c8333`

The observed mismatch was traced to the talk job and dialogue record not being physically linked. A talk job could exist in chronology even when dialogue generation/persistence failed before `citizen_conversations` was created.

The v0.5 branch now enforces:

- every new stored autonomous citizen conversation may carry `source_job_id`, the physical talk job that produced it
- `source_job_id` is unique when present, so retries cannot duplicate the same exchange
- before a generated exchange is committed, Communication revalidates:
  - the source job still exists
  - it is an active `talk` job
  - initiator/target match the job
  - both citizens are still bound to that job
  - both are still physically co-located
- the authoritative conversation `sim_minute` and `location_id` come from the validated talk job/current physical state, not untrusted generated text
- model/network/JSON failure no longer creates a fabricated fallback exchange
- a talk job is marked `complete` only if a source-linked conversation exists
- a talk job that reaches completion without a stored exchange is marked `failed`, releases both citizens, and records that the attempt ended without a recorded exchange
- stale generated text cannot be inserted after a talk has failed/invalidated
- Memory projection failure cannot erase an already durable conversation record

### Stable conversation / History record shape

`snapshot()["citizen_conversations"]` exposes:

- `id` — canonical immutable conversation source ID
- `source_type` — `citizen_conversation`
- `source_id` — alias of canonical `id`
- `transfer_event_id` — alias of canonical conversation `id`
- `source_job_id` — physical talk job ID for new source-linked records; nullable for legacy rows
- `sim_minute`
- `location_id`, `location_name`
- `initiator_id`, `initiator_name`
- `target_id`, `target_name`
- `initiator_text`
- `target_text`
- `summary`

Successful talk-completion chronology also includes the canonical conversation number, allowing the UI to connect a physical talk completion to the corresponding discussion record.

### Test status

A branch-only CI check passed:

- Python compilation
- existing `tests/smoke_v040.py`
- new `tests/smoke_v050_communication.py`

GitHub Actions run: `36372479310`.

The temporary branch-only workflow was removed after the green run, so the final branch contains only runtime/test changes.

## Provenance Contract

`docs/departments/communication/PROVENANCE_CONTRACT.md` remains the deeper Communication-owned provenance interface for future claim-level work.

v0.5 conversation integrity adds a stable physical source link, but it does **not** yet extract individual claims/topics into separate provenance records.

Memory may continue treating conversation content as remembered claims rather than authoritative physical truth.

## Visitor Conversation

Face-to-face visitor conversation still requires the visitor and citizen to be physically co-located.

A visitor cannot converse face-to-face while traveling.

The v0.4.1 blank-reply hotfix remains intact.

## Current Communication Technology

**None.**

There is currently:

- no radio
- no network
- no telepathy
- no shared live status channel
- no automatic remote messaging

Long-distance communication must be invented by the civilization if research, materials, fabrication capability, physical construction, and actual need eventually support it.

## Current Status

The v0.5 conversation-history integrity slice is ready for coordinator integration/review.

The next deeper Communication work is claim-level provenance / last-known propagation, which is intentionally outside this v0.5 integrity slice unless the coordinator reactivates it.

## Final Cross-Department Handoff Audit — 2026-09-28

All department branches were inspected after their work sessions ended.

### Communication branch
- `communication/v0.5-history-integrity`
- head: `672f221c0a2e796ba30d685d2cad68a5552c8333`
- status: implementation complete and tested

### Simulation branch
- `simulation/v0.5-making-building`
- head: `eadea56841469a29e8078f5eca23247b13317251`
- Simulation's own CI run `36372834945` is green.
- The branch exposes real v0.5 physical state through `equipment`, `projects`, `project_materials`, extended `structures`, and completed `jobs` with stable IDs/outcomes.
- **Integration conflict found:** this branch was developed independently from the v0.4.1 base and does not contain Communication's `citizen_conversations.source_job_id` migration or talk-completion integrity logic. Its talk completion still marks a physical talk as successfully finished without checking for a stored exchange.

Therefore the Simulation branch is individually complete but cannot replace/overwrite Communication's `db.py` / `simulation.py` changes during integration.

### Assets branch
- `assets/v0.5-making-ui`
- head: `da3b579bb42fb86a171470dd93946c01a80b0fc1`
- The branch contains the independent compact chat/layout/History improvements.
- Its conversation History renderer is compatible with real stored `citizen_conversations`.
- **Remaining integration gap:** it does not yet render Simulation's new `projects`, `equipment`, or `project_materials` state, so the Making & Building visual layer is not complete.

### Memory
Memory's v0.5 audit requires no new schema for conversation continuity. Communication preserved canonical `citizen_conversations.id`. Simulation's finished branch now demonstrates stable physical references:
- `projects.id`
- completed `jobs.id`
- `jobs.outcome`
- `jobs.project_id`
- project lifecycle timestamps/status
- resulting structure/equipment source IDs

These are suitable physical anchors after coordinator integration, but claim-level Communication provenance remains future depth.

### Overall integration status

Communication department work is finished.

The v0.5 milestone packet still requires coordinator-level integration work:
1. merge Simulation and Communication without losing the talk-source invariant
2. expose the merged Simulation state to Assets
3. finish the Making & Building UI against authoritative merged state
4. run combined smoke tests including both `smoke_v050.py` and `smoke_v050_communication.py`
