# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

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
