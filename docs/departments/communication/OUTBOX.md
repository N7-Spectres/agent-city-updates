# Communication & Perception — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** v0.4 provenance contract and planner anti-omniscience patch

**Need / Result:**
Audited the checked-in planner and found live remote citizen location/activity plus settlement-wide discovered deposits leaking into every citizen prompt. Patched `agent_city/planner.py` so planner context now exposes only the citizen's own state, co-located non-traveling citizens, local discovered deposits, and legal actions. Defined the minimum provenance contract for direct observation, personal experience, face-to-face claims, source, age, and verification.

**Files / Interfaces:**
- `agent_city/planner.py`
- `docs/departments/communication/PROVENANCE_CONTRACT.md`
- `docs/departments/communication/STATE.md`
- `docs/departments/communication/DECISIONS.md`

**Important constraints:**
- remote live state must not be injected into citizen prompts
- communicated claims remain claims until physically verified
- no free remote communication
- the default branch currently lacks `agent_city/comms.py`, `agent_city/db.py`, and `agent_city/simulation.py`, so runtime transfer persistence could not yet be implemented here

**Next action:**
Memory can consume the provenance contract now. Simulation should expose authoritative time/co-location/event identifiers when the runtime source is synchronized. Communication should wire the contract into the conversation/database layer once those files are available.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
