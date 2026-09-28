# Memory & Social — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_

## Mission

Preserve citizen continuity across long-running simulation time without overloading the local model context or confusing remembered claims with physical truth.

## Current Implementation

### Visitor conversation persistence

v0.2.7 introduced persistent visits:

- browser refresh restores the active visit
- Leave Visit explicitly ends a session
- raw visitor/citizen exchanges are archived in SQLite
- current visit uses a bounded recent window
- older parts of a long visit are summarized
- previous visit summaries can be viewed
- Ollama receives bounded recent context plus summaries, not an unbounded lifetime transcript

### Citizen conversation memory

v0.2.8 introduced stored citizen-to-citizen conversation records.

Citizens can later receive summaries of conversations they actually participated in.

Conversation memory is informational, not authoritative physical history.

## Current Emergent Social Behavior

Observed before a formal relationship system exists:

- Noma sought Cato at Resin Grove
- Noma later initiated conversation with Cato
- Bex initiated conversation with Aris before distant travel
- Iri sought Vale as a possible information source

This is proto-v0.4 behavior.

## Missing Pieces

There is no durable relationship model yet.

Citizens do not yet maintain robust long-term concepts such as:

- familiarity
- trust
- reliability
- repeated cooperation
- disagreement history
- promises
- favors/help
- social preference
- remembered verification that information was correct/incorrect

## Current Direction

v0.4.0 should deepen behavior already emerging naturally rather than adding scripted social events.
