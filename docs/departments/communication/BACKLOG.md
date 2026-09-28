# Communication & Perception — Backlog

## Integration / Follow-Up

- coordinator integration must preserve the v0.5 talk invariant when merging with `simulation/v0.5-making-building`:
  - `citizen_conversations.source_job_id` remains available
  - source-linked talk completion succeeds only when the conversation row exists
  - missing exchange causes failed talk, not a false successful transfer
- Assets may optionally cross-link successful talk-completion chronology to `citizen_conversations.id` / `source_id`
- legacy conversation rows may legitimately have `source_job_id = NULL`; do not fabricate a physical source link when ambiguous
- after integration, observe live autonomous talk for any unexpected failed attempts or model-generation reliability issues

## Deeper Provenance — Future Depth

- extract only specific facts actually spoken, not every fact implied by a summary
- store explicit claim/observation provenance records from `PROVENANCE_CONTRACT.md`
- formalize per-citizen last-known views derived from provenance records
- track information source and age in bounded Memory retrieval
- model claim verification/contradiction without treating retelling as verification
- add acceptance tests for the five claim-level provenance scenarios in `PROVENANCE_CONTRACT.md`

## Prompt / Perception Audits

- continue auditing visitor conversation prompts for accidental omniscience as new v0.5 project/building context is added
- continue auditing legal-action labels/reasons for hidden remote-state leakage
- ensure future project/building discussion remains conversation/intent unless Simulation exposes a validated physical outcome

## Speech / Hearing

- consider whether nearby third parties can overhear future conversations
- consider distance/noise/environment only if the world becomes detailed enough to justify it

Third-party overhearing does not exist yet.

## Physical Records

Potential future mechanisms if citizens create/use them:

- work logs
- notice boards
- signs
- written ledgers
- terminals

These must physically exist before becoming information channels.

## Future Invented Communication

Do not preselect the solution.

Possible outcomes might include:

- wired signaling
- optical relays
- encoded lights
- short-range transmitters
- radio-like systems
- world-specific alternatives

These remain possibilities, not planned unlocks.

## UI Requests for Assets

- show when a citizen is actively talking
- show communication events clearly in History
- distinguish failed talk attempts from stored conversations
- later distinguish direct vs last-known information visually if useful
