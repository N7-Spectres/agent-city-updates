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


## Natural dialogue surface

Live v0.8 feedback: grounded replies can expose too much planner/system vocabulary and sound stilted.

Examples to avoid in ordinary citizen speech unless personality/context specifically calls for them:
- "my current intent is..."
- "there's no active job queued..."
- "cross-reference with my records..."
- "propose a short local walk..."

Desired rule:
- keep authoritative status/action semantics in structured context, not in the citizen's phrasing
- translate those facts into natural character speech
- citizens may state exact energy/condition when it is plausible for a mechanical self-monitoring body, but should not narrate internal planner/job machinery
- shared-action availability should sound conversational ("we could take a quick look together") while the actual proposal/accept/start lifecycle remains structured and Simulation-owned
- retain each citizen's voice/personality instead of converging on operational-assistant diction

Noma target tone:
curious, thoughtful, observational, concise; research-minded without sounding like a diagnostic terminal.
