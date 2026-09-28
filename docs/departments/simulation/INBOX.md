# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The v0.6 Research/Discovery work packet was implemented and handed off._


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.6 provenance integration aligned to Simulation

**Need / Result:**
Communication inspected Simulation's final v0.6 contract and removed the independent module-name collision.

Final ownership:
- Simulation: `agent_city/knowledge.py`, `discoveries`, `citizen_knowledge`, `experiment_results`
- Communication: `agent_city/provenance.py`, `information_receipts`

**Integration behavior:**
Communication's `ensure_information_schema()` idempotently synchronizes:
- recipient-local `citizen_knowledge` rows where `verification_state = 'verified'`
- their `discoveries.id`, discovery time, subject, acquisition kind, and safe validated value/summary
- all persisted `experiment_results` as real experiment-experience receipts, including inconclusive outcomes

Communication does **not**:
- inspect `world_properties` by itself and grant knowledge
- promote `citizen_knowledge.verification_state = 'reported'` into verified receipts
- require Simulation to call back into Communication for every discovery

The generic `agent_city.provenance.record_validated_information(...)` remains available for future validated observation types that do not naturally fit Simulation's discovery tables.

**Acquisition mapping:**
- `direct_survey` -> `survey_measurement`
- `direct_experiment` -> `experiment_result`
- `direct_observation` -> `direct_observation`
- other verified personal acquisitions -> `personal_experience`

**Branch / test:**
- Communication head: `6a483fcc4d143606f3e401218002e06ae43076d1`
- final CI: `36421263078` passed all v0.4/v0.5 regressions + v0.6 Communication smoke

**Next action:**
No Simulation callback code is required. Coordinator should preserve both modules and both knowledge layers during merge.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
