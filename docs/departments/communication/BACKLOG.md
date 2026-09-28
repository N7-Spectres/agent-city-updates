# Communication & Perception — Backlog

## v0.6 Integration Follow-Up

- integrate `communication/v0.6-knowledge-provenance` with Simulation's final v0.6 discovery/experiment branch
- preserve both modules during merge: Simulation `agent_city/knowledge.py` and Communication `agent_city/provenance.py`
- preserve Communication's idempotent sync from verified recipient-local `citizen_knowledge` / `discoveries` and `experiment_results`
- preserve authoritative Simulation discovery/result IDs and simulation minutes in receipts
- merged planner context must include both Simulation-validated property knowledge and Communication provenance/claims
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

## Resume Order

When Communication work resumes:

1. read `docs/departments/COORDINATION.md`
2. read `docs/departments/communication/INBOX.md`
3. confirm the integrated/runtime branch being targeted
4. verify both `agent_city/knowledge.py` and `agent_city/provenance.py` exist where expected
5. run the Communication regression suite before changing provenance behavior
6. inspect any new Simulation discovery/acquisition states before mapping them
7. keep unknown remote state unknown rather than falling back to raw Simulation state

Current v0.6 feature work is complete; remaining items above are integration/future-depth work only.


## Live v0.6 Talk Reliability Follow-up

Live v0.6 observation shows repeated citizen talk jobs reaching:
- "conversation attempt ... ended without a recorded exchange"

This is physically correct behavior for a failed generation/persistence path, but repeated occurrences may indicate the structured dialogue/claim generation path is too brittle.

Follow-up:
- inspect why multiple autonomous talks are failing to persist real exchanges
- distinguish Ollama generation failure, JSON/schema failure, transcript-claim validation failure, and post-generation physical invalidation
- keep the invariant: never fabricate a conversation merely to make chronology look successful
- improve reliability so successful same-location talks normally yield a durable exchange
- expose enough diagnostic reason internally for debugging without leaking implementation noise into citizen-facing UI
