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

### Direct observation

A citizen can directly observe other citizens at the same location.

Traveling citizens are not treated as still locally visible at their origin.

### Citizen-to-citizen talk

Same-location available citizens may autonomously choose a face-to-face `talk` action.

A talk action:

- requires physical co-location
- occupies both citizens
- generates a short two-way exchange through Ollama
- stores the exchange and summary in SQLite
- becomes something both participants can later remember

### Visitor conversation

v0.3.0 gives N7 a physical location.

Face-to-face visitor conversation requires the visitor and citizen to be physically co-located.

A visitor cannot converse face-to-face while traveling.

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
