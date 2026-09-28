# Communication & Perception — Backlog

## v0.6 Integration Follow-Up

- integrate `communication/v0.6-knowledge-provenance` with Simulation's final v0.6 discovery/experiment branch
- ensure each Simulation discovery calls `record_validated_information(...)` only for the citizen(s) who physically learned the result
- preserve authoritative Simulation event IDs and simulation minutes in receipts
- integrate with Memory's v0.6 bounded knowledge read model without duplicating or globally merging citizen knowledge
- ensure Assets consumes structured Visit `status/availability` instead of generic inaccessible-location wording
- run combined v0.6 smoke suites after all department branches merge
- live-test autonomous conversation claim extraction for false positives/empty claim arrays after integration

## Claim Reconciliation / Reliability — Future Depth

The v0.6 ledger can represent `verified`, `unverified`, and `contradicted`, but richer reconciliation is not yet implemented.

Future work:

- compare later validated observations with earlier speaker claims when subject/topic semantics match safely
- preserve both old claim and later evidence
- derive source reliability from real verified/contradicted history only when enough evidence exists
- avoid reputation scores that collapse nuanced history into a game stat
- distinguish outdated-but-once-correct information from genuinely contradicted claims

## Last-Known Remote State

- extend structured receipts for citizen location/activity reports where those facts are actually spoken or observed
- expire nothing silently; expose source/time/age so consumers can treat old status as last-known
- do not convert last-known into current truth without a current channel

## Speech / Hearing

- third-party overhearing remains unimplemented
- only add hearing radius/noise/environment constraints when world detail justifies a real physical model
- no one receives a conversation they did not participate in unless an explicit hearing mechanism is implemented

## Physical Records

Possible future physical channels, only after citizens create/use them:

- work logs
- notice boards
- signs
- written ledgers
- terminals

A physical record must exist at a place and be encountered/read before it transfers information.

## Future Invented Communication

Do not preselect a technology.

Possible eventual mechanisms may include:

- wired signaling
- optical relays
- encoded lights
- short-range transmitters
- radio-like systems
- world-specific alternatives

They remain possibilities, not planned unlocks.

## UI / Audit Follow-Up

- periodically audit new planner/visitor prompts for raw Simulation truth leakage as Research & Discovery expands
- unknown properties/resources should remain absent, not presented as hidden locked secrets
- preserve distinction between admin truth views and citizen/visitor knowledge views
