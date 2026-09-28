# Assets & Interface — Backlog

## Review / Release — v0.8.1

Assets implementation is complete.

Review surface:

- branch `assets/v0.8.1-citizen-visuals-map`
- head `588dd08558a3b9aaed4a0ab8fe1d6e45a7838337`
- base `release-v0.8.1@c55eb76b89b35a660275ac97f095dcc4f511683e`
- PR #19 — ready for review
- full regression `36467360376` — PASS
- 16 commits ahead / 0 behind official hotfix base

Coordinator release checklist:

- merge/review PR #19
- visually verify Home head tokens
- visually verify Citizens full-body renders
- verify Cato retains heavy silhouette
- verify Iri retains slim silhouette
- verify zoom + / − / Region controls
- click Seed Site and other locations to confirm viewport focus
- confirm location hover/focus has no visible rectangle
- confirm keyboard focus highlights dot/label
- confirm dense Seed Site cluster improves as zoom increases
- confirm no optional gear appears from the art
- bump VERSION to v0.8.1
- run one definitive full release matrix
- publish only after green final run

## Completed — v0.8.1 Assets

- six approved full-body WebP assets
- six approved head/token WebP assets
- all six runtime visual profiles wired
- full-body contain rendering
- token cover rendering
- equipment-layer separation preserved
- expression-frame slots deliberately left null
- map zoom-in control
- map zoom-out control
- map Region reset
- zoom indicator
- presentation-only focused location viewport
- zoom-aware cluster separation
- visible node rectangle removed
- invisible generous node hit target preserved
- keyboard focus preserved
- reduced-motion preserved
- dedicated `tests/smoke_v081_assets.py`
- complete v0.4-v0.8.1 branch regression pass

## Later Citizen Visual Work

When separately approved assets exist:

- neutral expression frame
- blink frame
- happy `^ ^` frame
- focused frame
- curious frame
- optional richer bust crops
- transparent/higher-resolution archival masters if desired
- physically validated equipment overlays
- eventual 3D translation preserving the same silhouettes

Do not synthesize these into runtime canon without an approved source.

## Current Blockers

_None._

Next owner:
**Coordinator / v0.8.1 Release**


## Session Closed — v0.8.1

No open Assets implementation task remains in this session.

Resume only for:
- coordinator review feedback on PR #19,
- a visual regression found during final release validation,
- or a new milestone/work packet.

Current next owner:
**Coordinator / v0.8.1 Release**


## Compact status-bar rule

For the next character-sheet / Home-state polish pass:

- preserve the current compact Home citizen-card dimensions; do not make those cards taller or visually busier
- if Energy / Integrity move from plain percentages to bars, use **micro-bars**: thin, short, inline with the icon/value rather than full-width progress components
- keep the numeric percentage visible for precision
- use the same authoritative live values on Home and Citizen sheet
- clearly separate current charge/energy from long-term battery health/capacity
- character-sheet maintenance bars may be slightly wider because the sheet has more space, but should still remain visually quiet
- avoid stacking multiple large colored bars in one card
- prefer one small visual cue per metric over decorative gauges
