# Communication & Perception — Backlog

## Near-Term

- wire `PROVENANCE_CONTRACT.md` into the actual v0.3 conversation/database runtime once `comms.py`, `db.py`, and `simulation.py` are present on the branch
- store explicit transfer events for same-location conversations
- extract only facts actually spoken, not every fact implied by a summary
- formalize per-citizen last-known views derived from provenance records
- track information source and age in bounded Memory retrieval
- audit visitor conversation prompts for the same anti-omniscience boundary
- audit legal-action labels/reasons for hidden remote-state leakage
- add tests for the five provenance acceptance scenarios in `PROVENANCE_CONTRACT.md`

## Speech / Hearing

- model local speech as an explicit information-transfer event
- consider whether nearby third parties can overhear future conversations
- consider distance/noise/environment only if the world becomes detailed enough to justify it

## Physical Records

Potential future mechanisms if citizens create/use them:

- work logs
- notice boards
- signs
- written ledgers
- terminals

These should exist physically before they become information channels.

## Future Invented Communication

Do not preselect the solution.

Possible outcomes might include:

- wired signaling
- optical relays
- encoded lights
- short-range transmitters
- radio-like systems
- world-specific alternatives

But these remain possibilities, not planned unlocks.

## UI Requests for Assets

- show when a citizen is actively talking
- show communication events clearly in History
- later distinguish direct vs last-known information visually if useful

## Resume Order

When work resumes:

1. read Communication `INBOX.md` and `COORDINATION.md`
2. check for responses from Memory and Simulation
3. confirm whether `comms.py`, `db.py`, and `simulation.py` are now present on the default branch
4. if present, audit the real talk/visitor prompt/database paths before changing them
5. implement provenance persistence and bounded last-known retrieval against the documented contract
6. run the five acceptance scenarios in `PROVENANCE_CONTRACT.md`
