# Communication & Perception — Backlog

## v0.7 Integration / Observation

- coordinator integrates `communication/v0.7-talk-reliability` from v0.6.0 base
- preserve `agent_city/talk_diagnostics.py`
- preserve two-phase talk flow: raw exchange first, claim enrichment second
- preserve v0.6 source-linked talk completion invariant
- run full v0.4-v0.7 Communication regression matrix after cross-department merge
- observe live autonomous talks after release for real-world frequency of:
  - `dialogue_malformed_json`
  - `dialogue_schema_incomplete`
  - `ollama_network_failure`
  - claim-enrichment degraded outcomes
- if failures remain frequent, tune only measured dominant causes rather than adding synthetic fallback dialogue

## Future Reliability Depth

- optional bounded diagnostic summary/admin view if live debugging needs it
- retry/backfill claim enrichment for durable conversations whose raw exchange succeeded but claim projection degraded
- aggregate diagnostic counts over time without exposing them as citizen knowledge
- consider separate model/timeout tuning for raw dialogue vs claim extraction based on observed latency/failure data

## Provenance / Information Depth

Still future unless routed:

- semantic reconciliation of verified/contradicted claims
- evidence-derived source reliability
- last-known citizen state receipts with explicit source/age
- third-party overhearing
- physical notice boards/logs/records
- invented long-distance communication after real research/material/fabrication prerequisites

## Safety Boundaries

- no radio/network/telepathy exists
- failed model generation creates no transcript
- claim extraction cannot upgrade claims to verified truth
- unknown remote state remains unknown
- diagnostics never become citizen knowledge

## Resume Order

When Communication resumes:

1. read `docs/departments/COORDINATION.md`
2. read `docs/departments/communication/INBOX.md`
3. confirm the integrated/runtime branch being targeted
4. verify `agent_city/talk_diagnostics.py` and the two-phase `generate_dialogue` flow survived integration
5. run `tests/smoke_v070_communication.py` plus prior Communication regressions before making changes
6. inspect live diagnostic frequencies before tuning retry/timeout/model settings
7. prefer measured targeted fixes over broader retries or synthetic fallback behavior

Current v0.7 feature work is complete; remaining items are integration observation or future-depth work.
