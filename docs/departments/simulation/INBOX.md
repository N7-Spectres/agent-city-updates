# World & Simulation — Inbox

_Read this at the beginning of each World & Simulation work session._

## Open Messages

_None. The v0.6 Research/Discovery work packet was implemented and handed off._


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Communication v0.6 validated-discovery ingress ready

**Need / Result:**
Communication's per-citizen provenance ledger is implemented on `communication/v0.6-knowledge-provenance`.

Simulation remains authoritative for hidden truth, experiment outcomes, and discovery events. When a validated result becomes knowable to a citizen, the integration surface is:

`record_validated_information(...)` from `agent_city.knowledge`

**Arguments:**
- `recipient_id` — citizen who actually learned/observed it
- `subject_type`
- `subject_id` — stable subject/location/material/process ID when available
- `topic`
- `value_text` — validated finding suitable for citizen knowledge
- `channel` — one of:
  - `direct_observation`
  - `survey_measurement`
  - `experiment_result`
  - `personal_experience`
- `origin_event_type`
- `origin_event_id` — stable authoritative Simulation event/job/discovery ID
- `observed_at_sim_minute`
- optional `received_at_sim_minute`
- optional stable `source_key`

**Result semantics:**
Validated Simulation facts are stored as:
- `assertion_kind = validated_observation`
- `verification = verified`

The function returns the Communication receipt ID and is idempotent when the same stable source key is reused.

**Important constraints:**
- call once per citizen who actually receives/observes the result
- do not broadcast a discovery to all citizens automatically
- failed/no-result experiments may produce a validated experience/result receipt if Simulation says that outcome is knowable, but must not invent a successful property finding
- Communication does not inspect hidden truth and decide who knows it

**Branch / tests:**
- Communication head: `0cd9642c720e2950cb2a50728e19c08092408591`
- final green CI: `36420188139`

**Next action:**
Hand the final v0.6 discovery/experiment event fields to the coordinator and wire successful/failed knowable results to this ingress during integration.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
