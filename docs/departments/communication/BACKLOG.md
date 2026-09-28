# Communication & Perception — Backlog

## v0.8 Stage 2 Integration / Coordinator Assembly

Communication Stage 2 runtime work is complete.

Final branch:
- `communication/v0.8-shared-actions-stage2`
- head `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- CI `36457633293`

Coordinator merge must preserve:

- `agent_city/shared_actions.py`
- Communication shared-action endpoints/context in `main.py`
- Simulation's final `agent_city/exploration.py` lifecycle
- Memory Stage 2 retained/shared-exploration context in `main.py`
- Assets proposal/continuous-movement UI contract
- `tests/smoke_v080_communication_stage2.py`

## Final Stage 2 Source Chain

1. `conversations.id` — durable social exchange
2. `shared_action_proposals.id` — Communication proposal/UI projection
3. `shared_activities.id` — canonical Simulation shared event
4. `jobs.id` — real active physical movement job
5. `spatial_observations.id` — validated exploration evidence

## Post-Integration Observation

After assembled v0.8 testing/release, observe:

- false-positive proposal extraction frequency
- visitor requests phrased without explicit meter/cardinal targets
- accept succeeds but start fails cases
- rejected/expired proposal UI behavior
- status/progress freshness during long shared movement
- repeated proposal spam in a single visit

Tune only measured problems.

## Future Shared-Action Depth

- additional Simulation-owned shared activity types
- safe target semantics beyond explicit cardinal meter requests
- tool-assisted inspection only from real equipped capabilities
- physical action cancellation after start as a separate Simulation design
- richer visitor-claim provenance if later justified

## Existing Deferred Communication Depth

- claim contradiction/source reliability
- third-party overhearing
- physical records / notice boards
- emergent place-name propagation
- invented long-distance communication only after actual physical invention

## Ongoing Safety Rules

- no hidden world query in prompts
- no concept-art capability
- no remote live-state leakage
- no LLM-invented coordinates
- proposal != accepted != started != completed
- preserve v0.7 raw-exchange-first conversation reliability
