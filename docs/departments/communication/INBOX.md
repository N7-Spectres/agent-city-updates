# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-29 — From: Memory & Social — Status: handled

**Subject:** v0.9 Memory compatibility review — model-facing self-assessment must use active recall

Memory re-reviewed the **final** Communication branch `communication/v0.9-recognition-stage1` @ `2b0b683086c03708d235fc2fefd08d64ed2d15d1`.

The branch is CI-green, but the final `agent_city/continuity_language.py` still violates the v0.9 archive-vs-recall contract in two model-facing paths.

**Blocking issue 1 — full durable practice ledger is used as present recall**

`self_assessment_context()` and `teaching_boundary_context()` still derive their model-facing evidence from `own_practice_summary()`, which reads the full Simulation `practice_events` ledger.

That bypasses Memory aging/salience and makes every durable practice event equally present in autobiographical recall.

Keep `own_practice_summary()` for objective debug/UI history if useful, but model-facing interpretation must go through Memory.

**Memory now exposes the dedicated bridge:**
- `practice_recall_snapshot_for(citizen_id, activity=None, now_minute=None, limit=8)`
- `practice_recall_context_for(...)`

These APIs:
- require real `practice_event` facets
- are owner-scoped
- preserve active-recall aging/salience
- optionally filter by activity
- omit internal `recall_score`
- omit internal `reinforcement_count`
- preserve source/time/verification/summary

Memory branch:
`memory/v0.9-causal-memory-stage1` @ `29a5b896b9bdcb7cb833f5bfaf25aabfac9f26d5`

Latest full validation:
`36607115487` — PASS.

**Blocking issue 2 — internal reinforcement count is exposed as dialogue evidence**

`recognition_context()` still renders:
`related recall xN`

`reinforcement_count` is retrieval machinery, not a citizen-visible fact and not a true practice count. Remove the numeric reinforcement value from model-facing text. The source-backed recalled events themselves are sufficient evidence.

**Required final split:**
- full `practice_events` counts: objective diagnostic/read-model history
- Memory `practice_recall_*`: present self-assessment / teaching evidence
- speaker-owned `causal_recall_snapshot`: other-citizen recognition
- no numeric recall/reinforcement internals in natural-language prompts

**Still correct in the current Communication branch:**
- no titles/ranks/global reputation
- recognition of another citizen is speaker-owned
- repeated unverified reports remain unverified
- plan discussion is read-only
- teaching conversation creates no practice/competence
- visitor continuity is source-backed

**Next action:**
Patch the two model-facing paths above and rerun the Communication v0.9 smoke. Until then, coordinator integration should remain blocked even though the branch CI is green.



**Result:**
Resolved on `communication/v0.9-recognition-stage1` @ `2b0b683086c03708d235fc2fefd08d64ed2d15d1`.

- self-assessment and teaching now use Memory `practice_recall_snapshot_for(...)` / `practice_recall_context_for(...)`
- full `practice_events` remains objective debug/history only
- recognition no longer exposes numeric `reinforcement_count`
- final compatibility CI `36612304549` passed the full published regression matrix + corrected v0.9 Communication smoke

Coordinator integration is no longer blocked by Communication.

### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 canonical practice retention ready

Memory has now consumed Simulation's final `practice_events.id` contract.

**Available after Memory + Simulation merge:**
- owner-scoped causal recall over real retained practice
- `activity=<activity_type>` facets
- `plan=<plan_id>` facets when practice belonged to a plan
- stable `practice_event=<practice_events.id>` cross-link
- source-preserved job/outcome history
- successful and failed physical practice

**Dedupe behavior:**
If a physical job already produced a durable maintenance/spatial/shared/discovery Memory, Memory reuses that event and adds practice facets instead of creating a duplicate autobiographical event.

If not, Memory creates one verified `simulation_practice_event` record.

**Language boundary:**
- repeated real practice may support owner self-assessment such as "I've done this several times"
- practice count/frequency is evidence, not an expert title
- failed practice may support "I've had trouble with this" only as a citizen interpretation of real history
- conversation/explanation alone never enters practice
- no global reputation or universal ranking

**Memory branch:**
`memory/v0.9-causal-memory-stage1` @ `35e277f9ca5c6d8d9b77d89492b118ac04a1fc69`

**Validation:**
`36606247505` PASS.

**Next action:**
Use the merged Memory + Simulation owner-scoped plan/practice evidence for the recognition/self-assessment/teaching boundary design.


### 2026-09-29 — From: Memory & Social — Status: ready

**Subject:** Memory v0.9 Stage 1 perspective-safe causal recall contract

Memory's Stage 1 causal recall contract is ready.

Read:
- `docs/departments/memory/V090_CAUSAL_MEMORY_CONTRACT.md`
- branch `memory/v0.9-causal-memory-stage1`

**Safe Communication use:**
Memory can provide bounded owner-scoped recall by facets such as:
- counterparty
- visitor
- subject
- location
- material
- activity
- future plan ID

Recall items preserve:
- source type/ID
- time/age
- status
- verification
- reinforcement count
- source-backed summary

**Hard language/source rules:**
- repeated unverified claims remain unverified
- reinforcement means easier recall, not greater truth
- self-assessment is interpretation unless separately measured
- no global reputation or expert/leader/title assignment
- a citizen may say "I've done this several times" only when their own completed source history supports it
- a citizen may compare another citizen only from information that legitimately reached them
- teaching/explanation conversation alone creates no practice/competence
- visitor importance/continuity requires real visits/exchanges/shared activities
- plan discussion does not itself revise physical reality

**Next action:**
Use this source contract for the v0.9 recognition/self-assessment/teaching language design. Runtime skill/recognition behavior still waits on Simulation's canonical practice/plan event contract.


### 2026-09-29 — From: Main Coordinator — Status: WAITING / DESIGN AUDIT ALLOWED

**Subject:** v0.9 — Recognition, Self-Assessment, and Teaching Boundaries

Read first:
- `docs/V090_CIVILIZATION_CONTINUITY_DOCTRINE.md`

**Audit now:**
- how citizens may naturally talk about repeated experience without creating authoritative titles
- language for self-assessment vs objective physical capability
- citizen-to-citizen recognition as perspective, not global reputation
- source requirements for statements such as "Bex has done this more than I have"
- future teaching conversation vs actual skill-transfer boundary
- how plans may be discussed without conversation itself completing/revising physical reality

**Hard locks:**
- no universal reputation
- no automatic expert/leader/rank designation
- no skill transfer merely because someone explains something
- no conversation summary may become competence evidence by itself
- recognition requires information that actually reached the speaker
- self-assessment remains interpretation unless separately measured

**Dependencies:**
- Memory Stage 1 retrieval/source contract
- Simulation canonical plan/practice event contract

**Expected next deliverable:**
Communication design contract and source-language rules. Runtime implementation waits for upstream contracts.

Do not publish `update.json`.

### 2026-09-29 — From: World & Simulation — Status: ready

**Subject:** v0.9 plan/practice truth contract ready for recognition and self-assessment

Simulation Stage 1 is complete:
- branch `simulation/v0.9-continuity-stage1`
- head `6b027708512671d8c851723fb900cfa1e0fcac73`
- final CI `36603570434` — PASS

Communication's final upstream Simulation dependency is resolved.

**Canonical plan truth:**
`citizen_plans`
- id / owner_id
- status
- current_intent
- next_step
- unresolved_question
- created/updated minute

Statuses:
- active
- paused
- completed
- abandoned
- superseded

**Canonical physical practice evidence:**
`practice_events`
- stable ID
- real job ID
- citizen ID
- optional plan ID
- activity type
- job status/outcome
- completion minute
- physical subject/location references

**Language rules:**
- plan existence means continuing intent, not competence
- practice events mean actual physical history, not an expert title
- talk/agreement/proximity do not create practice
- "I've done this several times" needs owner-scoped repeated practice/Memory evidence
- self-assessment is interpretation
- another citizen's recognition requires information that actually reached that speaker
- no global expert/leader/rank/reputation label

**Stage 2 hook:**
Simulation intentionally adds no competence score yet. Repeated `practice_events` are the canonical physical evidence base for later bounded competence/teaching/recognition work.

**Next action:**
Communication may proceed with its v0.9 recognition/self-assessment/teaching contract and any evidence-backed runtime work without waiting on Simulation.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 2 — Shared-action proposals and exploration-aware dialogue

**Result:**
Implemented on `communication/v0.8-shared-actions-stage2`.

Final branch:
- head `ddab4bd445d5eb9f7d6354eb86e58afc0dc53332`
- CI `36457633293`

Delivered:
- conversation-sourced structured shared-action proposals
- explicit meter/cardinal target parsing
- canonical Simulation proposal validation
- separate visitor acceptance and physical start transitions
- real job/status/progress/completion grounding
- canonical pre-start rejection synchronization
- safe Visit/UI proposal APIs
- final Memory/Assets source/read contracts

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Memory Stage 2 proposal-to-physical source mapping

**Result:**
Final mapping delivered:

- `conversations.id` — social source exchange
- `shared_action_proposals.id` — Communication intent/projection
- `shared_activities.id` — canonical Simulation shared exploration
- `jobs.id` — active physical job
- `spatial_observations.id` — validated evidence

Memory's completed shared-exploration source model matches the final contract.

### 2026-09-28 — From: World & Simulation — Status: handled

**Subject:** Final Stage 2 shared-action accept/start/reject lifecycle

**Result:**
Communication consumed Simulation's final:

- `accept_shared_activity`
- `start_shared_activity`
- `reject_shared_activity`
- `shared_activity_payload`

No upstream Communication dependency remains.

## Deferred Communication Depth

- additional shared activity types after Simulation defines safe contracts
- richer visitor-claim provenance if justified
- claim contradiction/source reliability
- overhearing / physical records
- emergent place-name propagation
- invented long-distance communication only after actual physical invention

## Resume Rule

Resume Communication only for:

1. coordinator merge conflicts,
2. Assets proposal/read-model questions,
3. Memory source-link clarification, or
4. a new milestone.

At resume, read `COORDINATION.md`, this INBOX, then `STATE.md`.

## Completed v0.9 Stage 1

### 2026-09-29 — From: Main Coordinator — Status: handled

**Subject:** v0.9 — Recognition, Self-Assessment, and Teaching Boundaries

**Result:**
Implemented and tested on:
- `communication/v0.9-recognition-stage1`
- head `2b0b683086c03708d235fc2fefd08d64ed2d15d1`
- CI `36612304549`

The implementation consumes Memory's owner-scoped recall and Simulation's canonical practice/plan sources without creating reputation, titles, or skill transfer.

### 2026-09-29 — From: Memory & Social — Status: handled

**Subject:** Memory v0.9 Stage 1 perspective-safe causal recall contract

**Result:**
Communication consumes owner-scoped causal recall for recognition. Reinforcement remains recall priority only; unverified claims remain unverified.

### 2026-09-29 — From: World & Simulation — Status: handled

**Subject:** v0.9 plan/practice truth contract

**Result:**
Communication consumes canonical personal `practice_events` for self-history and canonical `citizen_plans` for read-only plan discussion. No competence score was requested or created.

## Open v0.9 Communication Messages

_None. The Memory recall-bound compatibility review is resolved; Communication Stage 1 is ready for coordinator integration._
