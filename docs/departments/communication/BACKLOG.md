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


## v0.8 Proposal vs capability language

Live v0.7 observation: a citizen discussing newly gathered Native Resin described the Crude Smelter as if it were specifically configured for resin and mentioned controlled extraction/distillation, even though those processing capabilities are not currently validated Simulation actions.

Treat this as a useful provenance/grounding case:
- citizens may hypothesize, propose, speculate, or suggest experiments
- dialogue must not present an unvalidated process/tool capability as already established fact
- when a process is not a known validated capability, prefer language such as "we could test whether..." / "I suspect..." / "we would need to develop..."
- conversation remains allowed to generate invention ideas; those ideas become physical truth only after Simulation validates a design/process
- preserve the distinction between a structure physically existing and that structure being capable of a particular unvalidated operation


## v0.8 Visitor-citizen shared-action grounding

Live v0.7 observation: during a face-to-face visit, a citizen accepted a visitor suggestion to "walk the perimeter" and spoke as though a shared physical activity was about to begin ("Ready when you are"), even though visitor chat currently does not create a joint Simulation action.

Needed grounding:
- distinguish conversational agreement/intention from an active physical co-action
- citizens may say they are willing to do something with the visitor, but should not imply it has begun until Simulation creates a valid shared/visitor-linked action
- preserve natural language such as "we could" / "I can do that" when capability exists but no action has started
- once visitor-linked physical actions exist, dialogue may reference their real state/progress


## v0.7.1 Visitor roleplay grounding

Live testing showed the visitor naturally roleplaying actions such as pointing out or handing over a possible mineral sample. Keep this interaction style, but tighten physical-truth boundaries.

Required behavior:
- visitor text may describe the visitor's own gestures, questions, suspicions, and suggestions
- visitor text does not create an authoritative object/deposit/sample/transfer merely by saying it exists
- citizen dialogue should interpret unvalidated visitor-described physical details as a claim/observation to inspect
- prefer uncertainty-aware language when Simulation has not validated the fact
- do not invent site history, prior operations, weather effects, or material properties as settled truth unless that information has a valid source
- keep the conversation natural and roleplay-friendly rather than replacing it with rigid refusals
- any later real pickup/transfer/inspection/shared-action mechanic must be Simulation-owned


## v0.7.1 Unsupported comparison/world-detail confidence

Live RP test showed improved uncertainty language ("my best guess", "perhaps..."), but the citizen still inserted unsupported specifics while reasoning.

Examples observed:
- describing Native Resin as having a porous structure without validated knowledge
- describing Conductive Wire as having a crystalline lattice without a source
- calling an unverified deposit "high-value"
- referring to a "northern scrub" that is not an authoritative known map feature

Refinement:
- keep natural comparative reasoning and uncertainty
- only compare against properties the speaking citizen actually knows
- do not invent material microstructure, economic value, terrain labels, landmarks, or site history
- when a comparison basis is not known, use neutral language such as "doesn't match materials I've verified" or "I can't identify it from appearance alone"
- spatial suggestions should reference real mapped/known locations or clearly remain hypothetical
- personality may improvise style; factual nouns and physical claims need provenance
