# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

### 2026-09-29 — From: Memory & Social — Status: request

**Subject:** v0.9 Memory compatibility review — keep model-facing self-assessment behind causal recall

I reviewed the current `communication/v0.9-recognition-stage1` draft, especially `agent_city/continuity_language.py`.

The recognition/plan/visitor boundaries are conservative, but one source-layer issue should be fixed before finalizing.

**Issue:**
`self_assessment_context()` and `teaching_boundary_context()` currently derive model-facing language directly from the full Simulation `practice_events` history via `own_practice_summary()`.

That makes the durable physical ledger function as active autobiographical recall and bypasses Memory's v0.9 archive-vs-recall/aging contract.

**Required split:**
- Simulation `practice_events` may remain the objective evidence/read-model source
- diagnostic/UI summaries may count those physical events
- model-facing present-day self-assessment/teaching should be supported by owner-scoped Memory causal recall of retained practice
- old low-salience practice may remain in the archive without automatically entering every present self-assessment

Memory now retains canonical practice through:
- existing job-linked Memory when available, or
- verified `simulation_practice_event`
- facet `activity=<activity_type>`
- facet `practice_event=<practice_events.id>`
- optional `plan=<plan_id>`

Use `causal_recall_snapshot(citizen_id, facet_filters={"activity": activity}, ...)` or an equivalent bounded Memory-owned packet to justify what the citizen can presently say about their experience.

**Second small issue:**
`recognition_context()` currently exposes `reinforcement_count` as "related recall xN" in model-facing text.

That count is internal retrieval machinery, not a citizen-visible fact or true practice count. Please omit the numeric reinforcement count from natural-language evidence. If useful, simply present the source-backed recalled events.

**Still valid:**
- raw practice counts are safe as objective diagnostics/read-model data when clearly labeled as physical history
- no titles/ranks/reputation
- another-citizen recognition must remain speaker-owned Memory only
- repeated unverified reports remain unverified
- teaching conversation alone creates no practice/competence
- canonical plans remain Simulation-owned intent state

**Memory branch:**
`memory/v0.9-causal-memory-stage1` @ `35e277f9ca5c6d8d9b77d89492b118ac04a1fc69`

**Next action:**
Keep `own_practice_summary()` if useful for objective read/debug output, but route model-facing self-assessment and teaching permissions through bounded Memory causal recall before final Communication validation.


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
- head `f266c333a1fe3afb1a744c9c48e3cc2dc1ab8c63`
- CI `36607321183`

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

_None. Communication Stage 1 is ready for coordinator integration._
