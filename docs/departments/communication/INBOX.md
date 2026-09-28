# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.8.0 Stage 1 — Grounded visitor RP and capability language

**Runtime base / branch:**
- base: `release-v0.7.0` / immutable commit `d81a85bf03b69b969532016f59bbbed2233949ee`
- create/use: `communication/v0.8-grounding-stage1`

**Stage 1 goal:**
Tighten dialogue grounding now that visitors are naturally roleplaying exploration and citizens are beginning to propose processes/actions that Simulation cannot yet perform.

**Required implementation:**
- visitor-described physical details remain visitor claims/observations until Simulation validates them
- citizen replies should distinguish:
  - known fact
  - remembered/reported claim
  - current observation
  - hypothesis/proposal
  - validated capability/action
- prevent unsupported confident statements about:
  - material microstructure/properties
  - economic/value judgments
  - invented landmarks/terrain names/site history
  - weather/environment effects
  - structure/tool capabilities not present in Simulation
- preserve natural RP instead of rigid refusals
- citizen may propose using a tool only if authoritative state says that tool/capability is actually available
- concept-art equipment never counts as runtime equipment
- citizen may agree to a shared visitor activity conversationally, but must not imply the physical action has started unless Simulation creates a real action
- retain existing v0.7 raw-exchange-first persistence, provenance, and no-fake-dialogue rules

**Stage 1 shared-action work:**
Define the minimum Communication-side contract for future visitor-linked physical actions, but do not invent the physical action yourself. Wait for Simulation's Stage 1 spatial/action contract before wiring any real shared movement/survey behavior.

**Important constraints:**
- personality may improvise style; factual nouns/claims require evidence
- uncertainty wording is not permission to invent supporting facts
- no radio/network/remote knowledge
- no `update.json` changes

**Next action:**
Implement the independent grounding layer, document the future shared-action interface, consume Simulation's coordinate/action contract if it arrives during the session, run regressions, update STATE/DECISIONS/BACKLOG/OUTBOX, then stop.


_None currently for the active v0.7 Communication slice._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.7 autonomous talk reliability

**Result:**
Implemented and tested on `communication/v0.7-talk-reliability`.

Delivered:
- raw-exchange-first two-phase conversation flow
- one bounded retry for raw structured dialogue
- tolerant JSON-object recovery without synthetic fallback text
- non-fatal claim/provenance enrichment
- `talk_diagnostics` failure/retry/degraded/success ledger
- separate concise History diagnostic for hard failed talks
- failure-code separation for model/network/schema/physical/persistence/claim paths
- lock-safe diagnostic lookup during Simulation completion

Final branch head: `61eecc4c047dd3fd22b71612251769a8cb456737`  
Final green CI: `36428495003`.

All v0.4/v0.5/v0.6 regression suites plus `tests/smoke_v070_communication.py` passed.

## Deferred / Future Depth

- live diagnostic aggregation/admin summary
- claim-enrichment retry/backfill after degraded projection
- measured model/timeout tuning based on post-release diagnostics
- claim contradiction/reliability semantics
- overhearing / physical records / invented remote communication

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
