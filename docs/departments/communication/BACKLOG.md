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


## Conversation summary truth-language audit

Live v0.8 feedback: recent citizen conversation summaries can use words such as "validated", "confirmed", or "proceed to inspect" too strongly.

Rule:
- conversation summaries describe what was communicated, not authoritative physical completion
- "validated" / "confirmed" may appear only when the exchange is explicitly backed by a real Simulation observation/experiment/shared-activity source
- otherwise use claim-safe wording such as "compared reports", "discussed", "said they had observed", "agreed to inspect", or "planned to verify"
- future intent must stay future intent; "agreed to inspect" is not "inspected"
- a citizen may truthfully report their own live inventory/current state, but another citizen hearing it does not independently validate the physical fact
- completed shared exploration should cite the canonical Simulation shared activity / observation chain before summary language upgrades from report to verified evidence

## v0.9 Stage 1 Integration

Communication runtime work is complete.

Final branch:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549`

Coordinator merge must preserve:
- Memory `agent_city/causal_memory.py`
- Memory practice projection
- Simulation `agent_city/continuity.py`
- Communication `agent_city/continuity_language.py`
- Communication changes in `agent_city/comms.py`
- Communication visitor-context changes in `main.py`
- `tests/smoke_v090_communication_stage1.py`

Combined Stage 1 testing should run:
- published v0.4-v0.8.7 regression matrix
- `tests/smoke_v090_memory_stage1.py`
- `tests/smoke_v090_simulation_stage1.py`
- `tests/smoke_v090_communication_stage1.py`
- Assets focused v0.9 test if/when added

## Future Teaching Mechanism

If Stage 2 adds actual skill/competence transfer, Communication needs Simulation-owned guided-practice evidence.

Minimum future source contract should include:
- teacher citizen ID
- learner citizen ID
- canonical job/action/event ID
- activity type
- physical task
- completion/outcome
- simulation minute
- explicit competence/practice effect if Simulation supports one

Conversation alone must remain insufficient.

## Future Recognition Depth

Potential later work, only if doctrine routes it:
- source-backed subjective preferences for who to ask for help
- evidence-backed disagreement in recognition between citizens
- recognition aging/revision after newer witnessed outcomes
- source reliability effects based on verified/contradicted history

Do not collapse any of these into global reputation.

## Current Non-Goals

- XP/levels
- permanent classes/specializations
- expert badges
- leader selection
- universal reputation
- skill gained from explanation
- global access to other citizens' practice history
- plan mutation through conversation

## Ongoing Audit Rules

- own practice can support self-description, not titles
- other-citizen recognition uses speaker-owned Memory only
- repeated claims do not become verified by repetition
- visitor continuity requires real sources
- preserve v0.8 grounding/provenance and v0.7 raw-exchange-first reliability

## v0.9 Stage 1 Resume Order

When Communication resumes:

1. read `docs/departments/COORDINATION.md`
2. read `docs/departments/communication/INBOX.md`
3. confirm the integrated v0.9 branch/runtime being targeted
4. verify Memory `causal_recall_snapshot(...)`, Simulation `practice_snapshot_for(...)`, and Simulation `plan_snapshot_for(...)` survived integration
5. verify `agent_city/continuity_language.py` and `tests/smoke_v090_communication_stage1.py` survived integration
6. run the full published regression matrix plus Memory/Simulation/Communication v0.9 Stage 1 smokes before altering continuity language
7. preserve perspective-safe recognition and the teaching-without-skill-transfer rule
8. only add actual competence/teaching effects after a future Simulation-owned mechanism exists

Current Communication Stage 1 feature work is complete; remaining work is coordinator integration or later v0.9 stages.

## v0.9 Stage 1 Final Integration Gate

Communication's archive-vs-active-recall compatibility blocker is resolved.

Coordinator integration should now preserve and test together:

- Memory `causal_recall_snapshot(...)`
- Memory `practice_recall_snapshot_for(...)`
- Memory `practice_recall_context_for(...)`
- Simulation `practice_snapshot_for(...)`
- Simulation `plan_snapshot_for(...)`
- Communication `continuity_language.py`

Critical split:
- full practice ledger = objective history/debug only
- active practice recall = model-facing self-assessment/teaching
- speaker-owned causal recall = other-citizen recognition
- no numeric recall/reinforcement internals in dialogue

No Communication-owned v0.9 Stage 1 implementation remains.

## Final v0.9 Stage 1 Status

Communication has no open Stage 1 implementation item.

Final tested branch:
- `communication/v0.9-recognition-stage1`
- `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549`

Next department action:
- coordinator combines Memory + Simulation + Communication
- run Memory, Simulation, and Communication v0.9 smokes with the published regression matrix
- Assets may proceed once the combined Stage 1 base and its remaining Memory UI-safe projection are available

Communication should not add more Stage 1 behavior before integration unless a concrete regression is reported.

## v0.9 Stage 2 Integration

Communication Stage 2 runtime work is complete.

Final branch:
- `communication/v0.9-guided-practice-stage2`
- head `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`
- CI `36627237487`

Coordinator merge must preserve:
- integrated Stage 1 continuity-language behavior
- Memory `guided_practice_memory.py`
- Memory family-aware `practice_recall_*`
- Simulation `competence.py`
- Simulation guided-practice legal actions/lifecycle
- Communication Stage 2 additions in `continuity_language.py`, `comms.py`, `planner.py`, and `main.py`
- `tests/smoke_v090_communication_stage2.py`

Combined Stage 2 testing should run:
- complete published regression matrix
- all four v0.9 Stage 1 smokes
- Simulation Stage 2 smoke
- Memory Stage 2 smoke
- Communication Stage 2 smoke
- Assets Stage 2 smoke

## Possible Later Causal-Link Depth

Simulation supports optional `source_conversation_id` for guided practice.

Current Communication Stage 2 language does not create or infer a mandatory conversation→guided-session causal link.

If a later milestone requires explicit proposal-to-session continuity, add it only through a stable Simulation/planner source link rather than by guessing from nearby conversations.

## Stage 2 Non-Goals

- no global competence/reputation
- no expert/mentor/trainer titles
- no conversation-based competence
- no frontend-derived competence
- no remote lookup of another citizen's objective competence
- no automatic skill transfer from remembered guidance


## 2026-09-29 Session Check

No new backlog item was added. Live inbox/coordination review found no Communication-owned work beyond the existing deferred depth and resume conditions. v0.9 Stage 2 remains complete and awaiting coordinator integration.


## v0.9 Stage 3 — Communication Complete / Integration Pending

Final branch:
- `communication/v0.9-patterns-stage3`
- head `3fc8872b7a35ee8169329d6a6edf523a2fa0b0c9`
- CI `36643141322` PASS

Completed:
- source-backed recurring-history/place/social-pattern dialogue context
- speaker-constrained pattern claim catalog
- transcript-grounded social-pattern transmission
- recipient-owned Memory provenance
- unverified claim preservation
- visitor read-only pattern context
- focused Communication Stage 3 smoke
- full v0.4→v0.9 Stage 3 upstream regression

Remaining:
1. Assets consumes the final score-free Memory read model and Communication interpretation contract.
2. Coordinator integrates Assets on the assembled Stage 3 base.
3. Run the definitive matrix including all Stage 3 smokes.
4. Review v0.9.0 release readiness.

Communication should remain stopped unless integration feedback is routed.
