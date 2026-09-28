# Communication & Perception — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_

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

## Current Implementation

### Citizen awareness

Citizens know the other five citizens exist.

They do **not** receive live omniscient status for remote citizens.

The checked-in planner previously leaked every citizen's live location/activity and all discovered deposits into every citizen prompt. That leak has now been removed from `agent_city/planner.py`.

Planner context now exposes:

- the citizen's own state
- co-located, non-traveling citizens as directly observable presence
- discovered deposits at the citizen's current location only
- legal actions supplied by Simulation

Remote live status is not injected into the prompt.

### Direct observation

A citizen can directly observe other citizens at the same location.

Traveling citizens are not treated as still locally visible at their origin.

Direct observation does not expose private plans, hidden internal state, or remote knowledge.

### Citizen-to-citizen talk

Same-location available citizens may autonomously choose a face-to-face `talk` action.

A talk action:

- requires physical co-location
- occupies both citizens
- generates a short two-way exchange through Ollama
- stores the exchange and summary in SQLite
- becomes something both participants can later remember

The default branch does not currently contain `agent_city/comms.py`, `agent_city/db.py`, or `agent_city/simulation.py`, so the live v0.3 conversation schema and transfer implementation could not be audited or patched here.

### Provenance contract

`docs/departments/communication/PROVENANCE_CONTRACT.md` defines the minimum v0.4 information-transfer record for:

- direct observation
- personal experience
- face-to-face claims
- source actor
- origin event
- transfer event
- observed / received simulation time
- assertion kind
- verification state

Memory may derive compact last-known views from those records.

### Visitor conversation

v0.3.0 gives N7 a physical location.

Face-to-face visitor conversation requires the visitor and citizen to be physically co-located.

A visitor cannot converse face-to-face while traveling.

Visitor prompt context should obey the same provenance boundary as citizen prompts once the v0.3 conversation source is available in the repository.

## Current Communication Technology

**None.**

There is currently:

- no radio
- no network
- no telepathy
- no shared live status channel
- no automatic remote messaging

Long-distance communication must be invented by the civilization if its research, materials, fabrication capability, and perceived need eventually support it.

## Current Observation

Citizens are already using conversation strategically as part of autonomous planning.

The next implementation step is wiring the provenance contract into the actual conversation/database runtime once those source files are available on the branch.
