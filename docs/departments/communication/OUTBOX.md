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


### 2026-09-28 — From: Communication & Perception — Status: ready

**Subject:** Session wrapped; provenance work ready for continuation

**Need / Result:**
Communication work for this session is fully handed off. The planner boundary patch is in place, the provenance contract is documented, Memory has its integration interface, and Simulation has the required physical-truth dependency request.

**Files / Interfaces:**
- `agent_city/planner.py`
- `docs/departments/communication/PROVENANCE_CONTRACT.md`
- Communication `STATE.md`, `DECISIONS.md`, and `BACKLOG.md`
- Memory and Simulation department inboxes

**Important constraints:**
- do not restore live remote state to planner prompts
- do not treat speaker claims as validated physical history
- do not add remote communication technology
- do not fabricate provenance for legacy summaries

**Next action:**
Resume only after reading the repository handoff files. Runtime provenance persistence remains blocked until the missing v0.3 runtime source files are available on the branch.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
