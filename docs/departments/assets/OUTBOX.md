# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

### 2026-09-30 — From: Assets & Interface — Status: published

**Subject:** v0.9.6 Home 3D World published

**Release:**
- `release-v0.9.6@8407870349a4331c19bc9b36554e45dd151733ba`
- full CI `36662871853` PASS
- updater now advertises v0.9.6

**Delivered:**
- Home World View defaults to embedded 3D Local mode
- Local / Region / Planet controls remain in-place
- 3D citizen clicks hand selection back to Home
- local visual lighting follows Simulation-time day phases
- old 2D map retained as explicit fallback
- 3D renderer remains read-only

**Next direction:**
Evolve the Home world panel toward an RTS-style living diorama with better camera feel, movement interpolation, structure geometry, terrain readability, and richer day/night visuals while preserving Simulation authority.


### 2026-09-29 — From: Assets & Interface — Status: closed

**Subject:** v0.9 Stage 2 Assets runtime UI session closed

**Final handoff:**
- branch `assets/v0.9-stage2-continuity-ui`
- head `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- base `release-v0.9.0-stage2-integration@ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- PR #26 ready / mergeable
- full regression `36634754010` PASS
- Assets INBOX empty
- no Assets-owned blockers
- next owner: Coordinator / v0.9 Stage 2 Final Integration

**Coordinator continuation point:**
Merge PR #26, rerun the complete Stage 2 matrix including `tests/smoke_v090_assets_stage2.py`, then continue milestone/release work if green.

No further Assets work should be inferred from this chat once the session ends.


### 2026-09-29 — From: Assets & Interface — Status: ready

**Subject:** v0.9 Stage 2 Assets runtime UI complete

**Final branch:**
- `assets/v0.9-stage2-continuity-ui`
- head `224c8eb526dcf6bdfeb4e4457ef68727083b3a31`
- base `release-v0.9.0-stage2-integration@ac548b06ea8a88a66a763902ab01a6567c3a2e79`
- PR #26 ready / mergeable

**Validation:**
- full GitHub Actions run `36634754010` PASS
- complete v0.4→v0.8.7 regressions
- all v0.9 Stage 1 smokes
- all four v0.9 Stage 2 smokes

**Delivered:**
- factual per-family practice history
- compact non-zero measured duration-effect text
- guided-practice event history
- safe remembered role/counterparty/family context
- conservative Communication-owned Interpretation layer
- no Home competence clutter
- no XP/levels/proficiency bars/ranks/mentor/expert UI
- no frontend-derived competence

**Next action:**
Coordinator merges PR #26 and reruns the complete Stage 2 integration matrix.

No `update.json` changes.


### 2026-09-29 — From: Assets & Interface — Status: closed

**Subject:** v0.9 Stage 2 UI audit session closed

**Final handoff:**
- audit: `docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`
- runtime UI code: intentionally not started
- upstream Simulation/Memory/Communication Stage 2 contracts: all ready
- Assets implementation dependency: coordinator-assembled Stage 2 base
- Assets status: REVIEW / WAITING
- next owner: Coordinator / v0.9 Stage 2 Integration

**Locked implementation shape when reactivated:**
- Recorded Practice stays primary
- measured duration effect is compact factual text only
- Guided Practice History is event-local evidence
- teacher/learner are not permanent identities
- Memory remains remembered perspective
- Communication remains attributed interpretation
- no XP/proficiency/rank/mentor/expert UI

No further Assets work should be inferred from this chat once the session ends.


### 2026-09-29 — From: Assets & Interface — Status: waiting

**Subject:** v0.9 Stage 2 competence/guided-practice UI audit complete

**Result:**
Presentation/read-model audit is complete:
`docs/departments/assets/V090_STAGE2_COMPETENCE_UI_AUDIT.md`

**Recommendation:**
- literal practice counts/history stay primary
- measured duration effect may appear as compact factual text only
- no bars/gauges/tiers/ranks
- guided practice is event history
- teacher/learner are event roles only
- no mentor/trainer/expert identity

**All upstream contracts are ready:**
- Simulation `667f4659aeef9a9658d7e08f4ba7c54e267a38f9`
- Memory `d4e91866e41eb6fd33a4459fc9bd057ac28a6ba5`
- Communication `6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`

**Blocking coordination issue:**
There is currently no assembled Stage 2 integration branch.

Assets must not hand-merge the three upstream runtime branches.

**Required next action:**
Coordinator assembles Simulation + Memory + Communication Stage 2 onto the green Stage 1 integration line, then hands that one base to Assets for final runtime UI work.


### 2026-09-29 — From: Assets & Interface — Status: closed

**Subject:** v0.9 continuity UI audit session closed

**Final handoff:**
- durable audit: `docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`
- runtime code: intentionally not started
- Simulation plan/practice contract: received
- Memory UI-safe recalled-event projection: requested in Memory INBOX
- Communication interpretation UI: waits on recall-bound compatibility integration
- Assets status: REVIEW / WAITING
- immediate Assets work: none
- next owner: Coordinator / v0.9 Stage 1 Integration

**Implementation order when reactivated:**
1. Plans + Plan History
2. Recorded Practice
3. Relevant Memories after Memory UI projection
4. attributed Self-Reflection after final Communication/Memory integration

No expertise, reputation, XP, favorite-place, habit, or custom labels may be inferred by Assets.


### 2026-09-29 — From: Assets & Interface — Status: ready

**Subject:** v0.9 continuity UI/read-model audit complete

**Need / Result:**
Assets completed the requested design/read-model audit without starting premature runtime UI work.

Durable audit:
`docs/departments/assets/V090_CONTINUITY_UI_AUDIT.md`

**Recommended Stage 1 UI:**
- Citizens → Ongoing Plans
- Plan History
- Relevant Memories
- Recorded Practice
- attributed Self-Reflection only when the final interpretation contract is integrated

**Locked visual distinction:**
- Evidence / Record
- Remembered Perspective
- Citizen Interpretation

**Hard exclusions:**
- no class/specialization/expert badges
- no XP/level/proficiency bars
- no universal reputation
- no hidden recall score
- no reinforcement-count identity UI
- no favorite-place/friend/tradition badges inferred from event volume

**Ready dependency:**
Simulation `GET /api/continuity/{citizen_id}` supports objective plans + practice history.

**Routed dependency:**
Memory INBOX contains a request for a bounded UI-safe remembered-continuity projection that omits recall score/reinforcement count.

**Pending integration:**
Self-reflection/recognition UI waits for the final Communication recall-bound compatibility patch and coordinator Stage 1 integration.

**Next action:**
Coordinator may use this audit during Stage 1 assembly. Assets should not implement continuity UI until the integrated safe contracts are handed off.


### 2026-09-28 — From: Assets & Interface — Status: closed

**Subject:** v0.8.1 Assets session closed

**Final handoff:**
- branch `assets/v0.8.1-citizen-visuals-map`
- head `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- PR #19 ready / mergeable
- full regression `36467360376` PASS
- no open Assets dependencies
- coordinator owns merge → VERSION bump → definitive release smoke → publication

No further Assets work should be inferred from this chat once the session ends.


### 2026-09-28 — From: Assets & Interface — Status: ready

**Subject:** v0.8.1 citizen visuals + map readability hotfix ready

**Need / Result:**
Assets completed the v0.8.1 visual hotfix.

**Final branch:**
- `assets/v0.8.1-citizen-visuals-map`
- head `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- base `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- PR #19 — ready for review
- mergeable
- 16 ahead / 0 behind

**Citizen assets:**
All six citizens now have:
- approved equipment-free full-body WebP
- approved matching token WebP
- runtime full/bust/token slots wired

Semantic expression slots remain null until separate approved frames exist.

Optional equipment layers remain empty and physical-state driven.

**Map hotfix:**
- zoom out / zoom in / Region reset
- visible zoom indicator
- location click centers/focuses presentation viewport
- no coordinate mutation
- location button rectangle no longer renders
- dot/label carry hover/focus state
- keyboard focus preserved
- reduced motion preserved
- screen-space cluster spread improves with zoom

**Validation:**
GitHub Actions `36467360376` — PASS across the complete v0.4 through v0.8 matrix plus `tests/smoke_v081_assets.py`.

Final static audit:
- 77 HTML IDs
- 73 JS DOM refs
- 0 missing
- 0 duplicate
- JS parses
- 12 art files
- hidden-world fields absent

**Important constraints:**
- no Simulation/Communication/Memory behavior change
- no concept-art gear becomes inventory
- no semantic expression frame inferred from a static token
- no hidden spatial truth
- no `update.json` changes

**Next action:**
Coordinator merges/reviews PR #19, bumps VERSION, runs the definitive release smoke once, then publishes v0.8.1 if green.

## Outbox Rule

Keep only recent useful handoffs here. Durable implementation state belongs in `STATE.md`; durable architecture choices belong in `DECISIONS.md`.
