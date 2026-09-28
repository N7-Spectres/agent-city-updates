# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-28 — From: Main Coordinator — Status: request

**Subject:** v0.7.0 — Autonomous talk reliability

**Runtime base / branch:**
- base: `release-v0.6.0` / immutable commit `6092aeafd685a3ba4cb8e9d455e586771d3f6d26`
- create/use: `communication/v0.7-talk-reliability`

**Need / Result:**
Investigate repeated valid same-location citizen talk attempts ending without a durable recorded exchange.

**Required scope:**
- distinguish failure causes internally:
  - Ollama/network failure
  - malformed/incomplete structured JSON
  - dialogue schema/claim extraction issue
  - physical talk invalidated before persistence
  - persistence/database failure
- preserve source-linked physical talk integrity
- never fabricate fallback dialogue
- improve normal valid talk success rate
- claim/provenance extraction failure should not unnecessarily erase an otherwise valid durable raw exchange if the raw exchange itself satisfies the physical conversation contract
- preserve v0.6 provenance boundaries and anti-omniscience
- expose concise internal diagnostic outcome/reason sufficient for History/debugging without dumping implementation noise into citizen-facing UI

**Acceptance direction:**
- ordinary co-located valid talks normally produce durable exchanges
- failed talks remain explicitly failed
- no fake transcripts
- canonical conversation IDs/source-job links remain stable
- existing v0.6 Communication smoke remains green

**Next action:**
Trace live failure paths, implement/test reliability fixes, update Communication STATE/DECISIONS/BACKLOG/OUTBOX, and hand any History/status interface changes to Assets.


_None currently for the active v0.6 Communication slice._

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.6 discovery/claim provenance + visitor availability

**Result:**
Implemented/tested on `communication/v0.6-knowledge-provenance`.

Final branch head: `6a483fcc4d143606f3e401218002e06ae43076d1`  
Final green CI: `36421263078`.

### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** Final v0.6 discovery/knowledge contract

**Result:**
Simulation's final contract was inspected and aligned.

Simulation owns:
- `agent_city/knowledge.py`
- `discoveries`
- `citizen_knowledge`
- `experiment_results`
- hidden world truth

Communication owns:
- `agent_city/provenance.py`
- `information_receipts`
- face-to-face claim provenance
- source/time/age / transfer history

Communication's provenance layer now synchronizes only verified recipient-local Simulation knowledge and experiment results; it does not turn hidden truth or merely reported Simulation rows into verified receipts.

The earlier module-name collision was removed and the complete regression suite passed afterward.

## Deferred / Future Depth

- richer verified/contradicted claim reconciliation
- evidence-derived source reliability
- third-party overhearing
- physical written/recorded information channels
- invented long-distance communication, only if civilization development earns it

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
