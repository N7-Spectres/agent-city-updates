# Agent City v0.9 — Continuity UI / Read-Model Audit

_Status: design audit only; no runtime implementation authorized yet_
_Owner: Assets & Interface_
_Last updated: 2026-09-29_

## Purpose

Define how Agent City should present long-term continuity without turning history into hidden classes, scores, reputations, authored biographies, or invented social truth.

Locked doctrine:

> **Persistent behavior must have a traceable history.**

Assets should make that trace visible while preserving the distinction between:

1. **objective evidence/history**
2. **citizen-scoped remembered perspective**
3. **citizen interpretation / self-assessment**
4. **later repeated patterns such as habits or customs**

The UI must not collapse those layers into one badge.

---

# Core Presentation Law

> **Show the trail, not the title.**

Allowed:
- "4 recorded extraction practice events"
- "Plan still open: inspect the Resin Grove sample"
- "Created after memory event #214"
- "Bex remembers this repair failing"
- "Bex says she feels more practiced at extraction"

Not allowed:
- "Extraction Expert"
- "Level 4 Fabricator"
- "Best builder"
- "Trusted friend"
- "Favorite place"
- "Resin Grove regular"
- "Evening maintenance tradition"

unless a later safe read model explicitly supports the underlying interpretation/custom and the wording remains appropriately scoped.

---

# Visual Grammar — Three Truth Layers

Continuity UI should use a consistent visual grammar.

## Layer A — Evidence / Record

Meaning:
A source-backed thing actually happened or currently exists.

Examples:
- plan lifecycle row
- completed/failed physical job
- canonical practice event
- source-linked memory event
- real conversation/shared-action source
- plan transition

Suggested styling:
- normal solid cards/rows
- timestamp/source metadata visible on demand
- neutral language
- no personality adjectives

Preferred label vocabulary:
- Recorded
- Completed
- Failed
- Created
- Revised
- Paused
- Resumed
- Abandoned
- Source
- Observed
- Reported

## Layer B — Remembered Perspective

Meaning:
This citizen currently retains/retrieves a source-backed experience or claim.

Examples:
- "Bex remembers the failed repair."
- "Cato recalls N7 walking with him."
- source-backed recognition of another citizen

Suggested styling:
- softer inset panel or memory glyph
- citizen name/perspective explicitly visible
- source type/time/verification accessible
- clearly distinct from objective physical history

Preferred vocabulary:
- Remembers
- Recalls
- Was told
- Reported
- Personally experienced
- Verified memory

Never expose:
- recall score
- reinforcement count
- hidden salience
- retrieval rank

## Layer C — Interpretation

Meaning:
A citizen's current conclusion about their own history or another citizen.

Examples:
- "Bex feels more practiced at extraction."
- "Cato thinks Bex has more field experience than he does."

Suggested styling:
- quote/reflection treatment
- explicitly attributed
- visually separated from objective evidence

Preferred vocabulary:
- "Bex feels…"
- "Cato thinks…"
- "Vale describes…"

Never render interpretation as a canonical stat.

---

# Proposed Information Architecture

The existing **Citizens** page is the natural home for v0.9 continuity.

Do not create a new top-level "Skills" or "Reputation" page.

Recommended citizen-sheet sequence:

1. current physical state
2. current work / equipment
3. **Continuity**
   - Plans
   - Relevant memories
   - Practice history
   - Self / social perspective when safe
4. existing knowledge/history surfaces

This keeps continuity attached to the person whose history produced it.

Records remains the deep archive.

Home remains lightweight and should not become a continuity dashboard.

---

# Surface 1 — Ongoing Plans

## Goal

Answer:

> **What is this citizen trying to continue, and why?**

Primary source:
Simulation `GET /api/continuity/{citizen_id}`

Safe current fields:
- plan ID
- owner
- lifecycle status
- current intent
- next step
- unresolved question
- created minute
- updated minute
- linked Memory event IDs
- transition history when supplied

## Recommended UI

Section title:
**Ongoing plans**

For each open/paused plan:

- current intent as the main line
- status chip using factual lifecycle language:
  - Active
  - Paused
  - Completed
  - Abandoned
  - Superseded
- "Next known step"
- "Open question" when present
- created / last changed time
- small **Why this exists** source-link area
- expandable **Plan history**

Example:

> **Inspect the Resin Grove sample again**  
> Active plan  
> Next: compare another sample at the grove  
> Open question: whether the previous result repeats  
> Why this exists: 2 source-linked memories  
> Last revised: Day 18, 14:20

## Hard rules

- never call a plan a task queue or promise
- "Next step" is intent, not guaranteed execution
- status must come from Simulation
- linked Memory IDs do not imply the UI knows their content unless Memory exposes them safely
- plan history is chronology, not personality

## Data dependency

Simulation is ready.

For **Why this exists**, Assets needs a bounded Memory projection resolving plan-linked Memory event IDs to safe display records.

Do not read raw Memory tables directly from the browser.

---

# Surface 2 — Plan History

## Goal

Answer:

> **How did this intention change over time?**

Source:
Simulation plan transitions plus safe source references.

Recommended presentation:
vertical timeline inside the plan card.

Rows may show:
- created
- revised
- paused
- resumed
- superseded
- abandoned
- completed
- linked physical job where safe
- linked source memory where safe

Example:

> Day 17 09:10 — Plan created  
> Day 17 15:42 — Paused after recharge became necessary  
> Day 18 08:25 — Resumed  
> Day 18 11:30 — Next step revised after observation #82

Do not summarize the citizen as "persistent", "indecisive", "focused", etc. from transition volume.

---

# Surface 3 — Relevant Memories / "Why now?"

## Goal

Answer:

> **What retained history is relevant to this citizen right now?**

Primary owner:
Memory & Social.

Use:
- bounded owner-scoped active recall
- source labels
- verification state
- event time
- summary
- safe facets only as navigation/context

Never use:
- raw recall score
- reinforcement count
- hidden salience score
- global-citizen union

## Recommended UI

Section title:
**Relevant memories**

Not:
- Strongest memories
- Top memories
- Most important memories

Reason:
those labels imply hidden score ranking.

Each item should show:
- remembered summary
- when it happened
- source category
- verification/perspective state
- optional source link
- pinned-by-plan indicator only as structural context, not importance

Example:

> **Remembered experience**  
> Failed chassis service attempt at Seed Site  
> Day 11 • personal experience • verified  
> Linked to current plan

Claim example:

> **Remembered report**  
> Cato said the basin route felt difficult under load  
> Day 12 • conversation claim • unverified

## Data dependency

Memory currently has Python-level:
- `causal_recall_snapshot(...)`
- `practice_recall_snapshot_for(...)`

The model-facing practice surface intentionally omits recall score and reinforcement count.

Assets needs a **UI-safe HTTP projection** before implementing this panel.

Requested minimum fields:
- citizen/owner ID
- memory_event_id
- source_type
- source_id
- event_kind
- sim minute / display time
- summary
- verification/status
- pinned flag
- safe source role
- safe display facets where useful

Must omit:
- recall_score
- reinforcement_count
- internal importance/salience score unless Memory explicitly defines a non-causal display semantic

---

# Surface 4 — Practice / Experience Evidence

## Goal

Answer:

> **What real work has this citizen actually done?**

Primary source:
Simulation `practice_events` / `GET /api/continuity/{citizen_id}`.

This is objective physical history.

Safe fields include:
- stable practice event ID
- physical job ID
- activity type
- job status/outcome
- completed minute
- plan ID when present
- location
- target
- material
- project
- observation/shared-action refs

## Recommended UI

Section title:
**Work experience**

Alternative:
**Recorded practice**

Do not title it:
- Skills
- Expertise
- Proficiency
- Level
- Specialization

### Summary line

Literal counts are allowed when clearly described as history:

> 4 recorded extraction practice events

Not:

> Extraction: Level 4

### Detail rows

Show recent/representative source events:

> Extraction • completed • Resin Grove • Day 18  
> Maintenance • failed • tool #7 • Day 17  
> Construction • completed • project #12 • Day 15

Outcome icons may be factual:
- completed
- failed
- no yield
- interrupted

Do not convert failures into permanent weakness.

## Optional grouping

Grouping by activity is acceptable for navigation:

- Extraction (4 recorded events)
- Maintenance (2)
- Construction (1)

Groups must remain event counts, not progress bars.

No bar fills.
No stars.
No tiers.
No "beginner → expert" ladder.

## Data dependency

Simulation Stage 1 safe read model is sufficient for objective practice history.

If the UI later shows **what the citizen remembers about their practice**, that must come from Memory's active recall surface, not the full ledger.

---

# Surface 5 — Self-Assessment

## Goal

Answer:

> **What does this citizen currently think about their own experience?**

This is interpretation, not physical truth.

Primary owner:
Communication + Memory.

Potential safe examples:
- "I've done this several times."
- "I feel more practiced at extraction."
- "I keep having trouble with delicate repairs."

## Recommended UI

Section title:
**Self-reflection**

Treatment:
- attributed quote/perspective card
- never displayed beside physical stats as though equivalent
- evidence link or "grounded in recalled experience" affordance where available

Example:

> **Bex reflects:**  
> "I've done this several times, so I feel more comfortable trying it again."  
> Grounded in recalled extraction experience.

## Hard rules

- no competence percentage
- no confidence bar
- no "expert" badge
- no planner bias score
- no inference by Assets from practice count

## Data dependency

Do not derive from Simulation counts.

Wait for the final integrated Communication/Memory safe interpretation contract.

Communication's development endpoint:
`GET /api/continuity-language/{citizen_id}`

is useful for audit/debug, but normal UI should bind only after the coordinator integrates the recall-bound compatibility patch.

---

# Surface 6 — Social Recognition

## Goal

Answer:

> **What does one citizen legitimately think/remember about another?**

There is no reputation page and no global score.

Recommended placement:
Citizen sheet → **Perspectives** subsection, only when safe records exist.

Each card must name the observer.

Example:

> **Cato's perspective on Bex**  
> Remembers Bex helping during two field-work events.  
> "Bex has done more of this than I have."

Not:

> Bex — Highly respected  
> Reputation 82  
> Extraction Expert

## Hard rules

- every recognition item is perspective-scoped
- source-backed only
- different citizens may disagree
- absence of recognition is normal
- do not aggregate observers into one rating
- do not display reinforcement count as social strength

## Data dependency

Requires Memory owner-scoped social/recognition projection.

Communication may provide safe language, but Memory must prove the observer had a legitimate information path.

Stage 1 UI should omit this subsection entirely if that projection is unavailable.

---

# Surface 7 — Place Meaning

## Goal

Answer:

> **What does this place mean to this particular citizen because of their history?**

Physical location truth stays on Locations.

Citizen-specific meaning belongs either:
- Citizen sheet → Places remembered
- Locations sheet → perspective selector / "Meaning to…" subsection

Do not author a global mood for the location.

## Recommended UI

Example for Resin Grove:

> **Meaning to Iri**  
> Remembers nearly exhausting her battery here during a field trip.

> **Meaning to Cato**  
> Several retained hauling/extraction experiences are linked here.

The two perspectives may coexist.

Do not render:

> Resin Grove — Iri's favorite place

unless an explicit citizen interpretation read model later supplies that statement.

## Data dependency

Memory needs a safe place-facet projection resolving:
- owner citizen
- stable place/location ID
- retained source events
- bounded summary/interpretation if explicitly supported
- verification/source links

The existing facet system has a future `place:<place_id>` hook, but the audit should not assume a current public UI endpoint.

---

# Surface 8 — Visitor Continuity

## Goal

Answer:

> **What source-backed history does this citizen have with this visitor?**

Recommended placement:
Visit panel or Citizen continuity section.

Possible factual surface:
- recorded visits
- source-linked shared activities
- remembered useful exchanges
- safe prior-visit summaries

Example:

> **With N7**  
> 3 recorded visits  
> 1 completed shared walk  
> Most recent remembered encounter: Day 18

This is encounter history, not relationship rank.

Do not render:
- Friend
- Trusted visitor
- Bond level
- Favorite human

unless a citizen-scoped interpretation explicitly supports such language and project doctrine later permits it.

## Data dependency

Existing visit/shared-action history can support factual counts.

Interpretive visitor meaning remains Memory/Communication-owned.

---

# Surface 9 — Habits

## Stage

Future v0.9 Stage 3 only.

Do not implement from raw event frequency in Stage 1.

A habit card should exist only after a safe habit read model says:
- a repeated pattern is established
- evidence threshold/semantics are explicit
- the pattern belongs to this citizen
- source events remain traceable

Potential UI:

> **Recurring pattern**  
> Vale has repeatedly chosen maintenance during evening wind-down.  
> Based on 6 qualifying events across 9 simulated days.

Even then, avoid trait language such as:
"Vale is a maintenance person."

## Required dependency

Memory/Simulation must define a safe habit projection.

Assets must not count chronology rows and invent a habit.

---

# Surface 10 — Customs / Traditions

## Stage

Future v0.9 Stage 3 only.

Customs require:
- repeated behavior
- multiple participants/observers
- retained social memory
- communication/transmission
- continued voluntary repetition

Recommended placement:
Records → History / future Civilization section.

Possible display:

> **Emerging shared custom**  
> [safe read-model description]  
> First observed: …  
> Participants/observers: …  
> Source events: …

Do not create:
- culture score
- tradition level
- civilization trait badges

No Stage 1 placeholder should tease customs as locked features.

If no safe custom exists, show nothing.

---

# Home Screen Rule

Home should remain about **what is happening now**.

Allowed continuity additions:
- one compact marker that a selected citizen has an unfinished plan, if useful
- current active-plan text may replace redundant activity text only when it improves clarity

Not allowed:
- XP bars
- skill summaries
- reputation
- habit badges
- memory score
- long continuity histories

Deep continuity belongs on Citizens / Records.

---

# Citizens Directory Rule

Do not add permanent role/subclass labels beneath names.

Existing canonical aptitude text remains historical starting-context presentation where already used, but v0.9 continuity must not replace it with dynamically generated titles such as:
- Prospector
- Senior Fabricator
- Logistics Expert
- Master Builder

If later competence differences affect Simulation, the UI should still prefer evidence/history over identity labels.

---

# Locations Rule

Location page should keep:
- physical known facts
- structures/resources/routes
- knowledge/evidence

Citizen-specific place meaning must be visibly separate from physical location truth.

Recommended heading:
**Remembered here**

with a citizen selector or individually attributed cards.

Never merge all citizens' place memories into one "location personality."

---

# Records Rule

Records may expose deeper factual archives:

- plan transition archive
- objective practice ledger
- source-linked continuity events

Records should not expose:
- hidden recall score
- reinforcement count as an identity metric
- hidden salience
- global recognition aggregation

A developer/debug surface may expose internal diagnostics separately if explicitly authorized, but it must never masquerade as citizen-facing truth.

---

# Empty-State Rules

Absence is meaningful and normal.

Use:
- "No unfinished plans."
- "No source-backed memories are currently relevant here."
- "No recorded practice for this activity."
- omit Social Recognition / Place Meaning / Habits / Customs subsections when no safe read model exists

Do not use:
- "Skill not unlocked"
- "No reputation yet"
- "Habit level 0"
- greyed-out Expert badge
- locked Tradition slot

Those reveal system-shaped hidden labels rather than lived history.

---

# Stage 1 Implementation Recommendation

Once the Memory + Simulation + Communication Stage 1 contracts are integrated, Assets should implement only the surfaces backed by finalized safe endpoints.

Recommended first slice:

## Citizens → Continuity

1. **Plans**
   - current/open plans
   - next step
   - unresolved question
   - plan transition timeline

2. **Relevant memories**
   - only if Memory exposes a UI-safe bounded endpoint
   - source/time/verification
   - no recall score/reinforcement

3. **Recorded practice**
   - factual history from Simulation
   - activity grouping/counts
   - source events
   - no skill bars

4. **Self-reflection**
   - only if final integrated Communication/Memory interpretation projection is ready
   - attributed and clearly separated from evidence

Do not implement habits, customs, reputation, expertise, or favorite-place badges in Stage 1.

---

# Explicit Data Dependencies

## Ready — Simulation

Branch:
`simulation/v0.9-continuity-stage1`

Safe endpoint:
`GET /api/continuity/{citizen_id}`

Ready for:
- plans
- plan lifecycle
- practice history

## Ready internally — Memory

Branch:
`memory/v0.9-causal-memory-stage1`

Safe internal contracts:
- `causal_recall_snapshot(...)`
- `practice_recall_snapshot_for(...)`

Important:
the practice model-facing surface omits recall score and reinforcement count.

### Assets request

Before normal UI implementation, expose a bounded **UI-safe owner-scoped continuity-memory endpoint**.

It should provide display-safe recalled event records without internal ranking metrics.

Suggested semantics, not a mandated route name:
- owner citizen ID
- recalled event ID
- source type / source ID
- source role
- event kind
- sim time / display time
- summary
- verification/status
- pinned-by-plan boolean
- safe facets only where presentation requires them

Must omit:
- recall score
- reinforcement count
- global aggregation

## Pending final compatibility — Communication

Development endpoint:
`GET /api/continuity-language/{citizen_id}`

The coordinator currently waits on Communication's recall-bound compatibility patch.

Assets should not bind production UI to the pre-patch interpretation payload.

After final integration, Assets may consume:
- self-assessment text
- source-backed recognition language
- visitor continuity language

only where perspective/source semantics remain explicit.

## Future — Stage 3 Memory/Simulation

Needed later:
- place-meaning projection
- habit projection
- custom/tradition projection

Assets will not infer these from raw event volume.

---

# Acceptance Criteria For Any v0.9 Continuity UI

A continuity surface is acceptable only if:

1. every behavioral/history statement has a safe source path
2. objective evidence and citizen interpretation are visually distinguishable
3. plan intent is not presented as guaranteed action
4. practice events are not converted into XP/levels/classes
5. recognition remains observer-specific
6. place meaning remains citizen-specific
7. no hidden recall/reinforcement score is exposed
8. no universal reputation is created
9. habits/customs appear only from explicit safe read models
10. deleting/altering source history would remove the justification for the displayed continuity
11. unknown/absent continuity is omitted rather than represented by locked empty systems
12. Home remains lightweight

---

# Core UI Principle

> **History can explain the citizen. The interface must not name a destiny for them.**
