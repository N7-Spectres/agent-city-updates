# Assets & Interface — Outbox

_Record completed handoffs, requests to other departments, and major deliverables here._

## Recent Messages

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
