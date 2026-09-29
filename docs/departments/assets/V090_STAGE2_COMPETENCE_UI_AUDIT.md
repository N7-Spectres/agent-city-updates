# Agent City v0.9 Stage 2 — Competence + Guided-Practice UI Audit

_Status: presentation/read-model audit complete; runtime implementation waits for coordinator Stage 2 assembly_
_Owner: Assets & Interface_
_Last updated: 2026-09-29_

## Purpose

Define how v0.9 Stage 2 should present real practice-derived physical effects and guided-practice history without turning Agent City into an RPG skills screen.

Locked project law:

> **Show the trail, not the title.**

Stage 2 introduces one real bounded physical consequence of repeated practice:
- a small Simulation-owned duration reduction for relevant future work

It also introduces real guided-practice sessions:
- source-backed physical events with teacher/learner roles for that event only

The UI must show those facts without creating:
- skill levels
- proficiency meters
- expertise classes
- trainer/mentor identities
- reputation
- hidden competence rankings

---

# Executive Recommendation

## Primary presentation

Keep **Recorded Practice** as the main competence-facing surface.

Literal practice history/counts remain the clearest and safest way to explain why a citizen may perform some work slightly faster.

Example:

> Extraction  
> 6 recorded practice events  
> 5 completed • 1 failed

This is evidence.

## Secondary presentation

If a family has a non-zero Simulation-provided duration reduction, show a small factual note beneath the evidence:

> Current measured work effect: comparable extraction tasks are 4.25% shorter.

This should be:
- text-first
- compact
- visually subordinate to history
- clearly labelled as Simulation-owned physical effect
- never rendered as a progress/proficiency bar

## Guided practice

Show guided-practice sessions as factual event history.

Example:

> Guided extraction practice  
> Bex guided Cato  
> Day 24, 13:10  
> Completed

Teacher / learner are event-local labels only.

Do not display:
- Mentor Bex
- Trainer level
- Teaching skill
- Student rank
- permanent teacher/learner identity

---

# Why Practice Counts Stay Primary

Practice count is:
- source-linked
- understandable
- non-normative
- already supported by Stage 1 continuity UI
- resistant to accidental RPG framing

The duration effect is physically real, but intentionally small and bounded.

A graphical meter would visually exaggerate that effect and invite users to read it as:
- proficiency
- level progress
- comparative rank
- latent class identity

Therefore:

> **Do not visualize competence magnitude with bars, rings, stars, gauges, or tier colors.**

Literal counts + factual effect text are enough.

---

# Three-Layer Stage 2 Presentation

Stage 1 already established:

1. Evidence / Record
2. Remembered Perspective
3. Citizen Interpretation

Stage 2 extends those layers rather than creating a fourth "Skills" system.

## Evidence / Record

Sources:
- Simulation `GET /api/competence/{citizen_id}`
- Simulation `GET /api/continuity/{citizen_id}`

May show:
- family name
- practice_count
- completed_count
- failed_count
- source practice event IDs
- duration_reduction_percent
- guided-practice session history

This is objective physical/history evidence.

## Remembered Perspective

Source:
- Memory `GET /api/memory/continuity/{citizen_id}`

May show:
- source-backed remembered practice
- source-backed remembered guided-practice events
- teacher/learner source role
- counterparty
- event time
- verification
- safe `competence_family` facet

Must not show:
- recall score
- reinforcement count
- hidden importance/salience
- competence weights/multipliers as Memory truth

## Citizen Interpretation

Source:
Communication final Stage 2 interpretation/language contract.

Examples:
- "I feel more comfortable with this now."
- "I remember Bex guiding me through extraction practice."

Interpretation must remain attributed.

It is not:
- measured physical effect
- objective competence
- permanent identity

---

# Simulation Stage 2 Read Model

Safe endpoint:

`GET /api/competence/{citizen_id}`

Per family:
- `family`
- `practice_count`
- `completed_count`
- `failed_count`
- `duration_multiplier`
- `duration_reduction_percent`
- `source_practice_event_ids`

Also:
- `guided_practice_sessions[]`

Semantics:
- derived from canonical practice events
- no XP/levels
- no class/expertise label
- physical effect is duration-only and bounded

## Fields Assets should display

Recommended:
- family
- practice_count
- completed_count
- failed_count
- duration_reduction_percent
- guided session factual fields

Use source practice event IDs only for drill-down/correlation, not as decorative metadata by default.

## Fields Assets should not invent

Never derive:
- "competence score"
- "proficiency percent"
- "rank"
- "better than citizen X"
- "expert status"
- progress toward next threshold

---

# Measured Physical Effect

## Recommended wording

When `duration_reduction_percent > 0`:

> **Measured work effect**  
> Comparable extraction tasks are currently 4.25% shorter from prior practice.

Alternative compact wording:

> Practice effect: −4.25% task duration

The first is preferred on the Citizen sheet because it is harder to mistake for a skill stat.

## When the value is zero

Do not render:
> Practice effect: 0%

Prefer omission.

Zero-value cards create a skill-system silhouette where none is needed.

## Visual treatment

- plain text
- small engineering/status glyph allowed
- no colored fill amount
- no progress bar
- no radial gauge
- no level tint
- no celebratory rank styling

## Comparison rule

Do not compare citizens by duration reduction in normal UI.

Even though the endpoint is objective, a cross-citizen leaderboard would effectively become a competence ranking surface.

Records/debug tooling could later expose raw factual comparisons if explicitly authorized, but not as citizen identity.

---

# Guided-Practice History

Source:
Simulation `guided_practice_sessions[]`

A session is a real event.

Recommended presentation:
within the existing **Evidence / Record** continuity layer.

Section title:
**Guided practice history**

Each row:

> **Extraction practice**  
> Bex guided Cato  
> Completed • Day 24, 13:10  
> Session #12

Or from the learner sheet:

> **Extraction practice**  
> Practiced with Bex  
> Completed • Day 24, 13:10

Prefer relational wording over badges.

## Teacher / learner labels

Safe as event-local metadata:
- Guide: Bex
- Learner: Cato

Avoid:
- Mentor
- Trainer
- Apprentice
- Student class
- Instructor level

## Session completion semantics

A completed guided session:
- is real history
- does not itself create learner competence/practice
- may temporarily support the learner's next matching real task
- the learner's later physical task creates the actual new practice evidence

UI must not say:
> Cato gained extraction skill from Bex.

Safe:
> Bex guided Cato through extraction practice.

---

# One-Use Guidance Effect

Simulation may apply a one-use guidance effect to the learner's next matching task.

Current safe read endpoint exposes guided session history but does not provide a dedicated UI semantic such as:
"guidance currently pending for next matching task."

Assets should **not derive that active state in the frontend** from raw session rows.

Reason:
- `status='complete'`
- `consumed_by_job_id IS NULL`

is implementation data, but a dedicated safe presentation field would be clearer if the project later wants this visible.

Recommendation for Stage 2 UI:
- show session history
- do not show a "guidance buff" / pending bonus badge

If coordinator later wants pending guidance visible, request a Simulation-owned explicit presentation field.

Absolutely do not render:
- buff icon
- +4% training bonus
- temporary skill-up badge

---

# Family Names

Current bounded families:
- surveying
- extraction
- experimentation
- fabrication
- construction
- maintenance

These are **activity families**, not roles/classes.

UI wording should reflect that.

Safe:
> Extraction — 6 recorded practice events

Unsafe:
> Extraction Specialist

Do not use family names as subtitles beneath citizen names.

---

# Failure History

Failed attempts count as real experience.

Recommended factual summary:

> Extraction  
> 6 recorded events  
> 5 completed • 1 failed

A failed attempt should not produce:
- weakness badge
- red proficiency penalty
- "bad at extraction"
- permanent negative trait

Failures may appear in recent event rows with their actual outcome.

---

# Guided Practice in Remembered Perspective

Memory's existing safe endpoint remains:

`GET /api/memory/continuity/{citizen_id}`

Stage 2 Memory refreshes both:
- canonical practice Memory
- guided-practice Memory

Safe remembered fields may include:
- source type / source ID
- source role
- counterparty
- event summary
- time
- verification
- safe competence-family facet
- plan-pinned state

Examples:

> **Remembered experience**  
> Bex guided me through extraction practice.  
> Day 24 • learner role • verified

> **Remembered experience**  
> I guided Cato through maintenance practice.  
> Day 23 • guide role • verified

Do not convert repeated guide-role memories into:
> Mentor

The event trail is enough.

---

# Citizen Interpretation

Communication owns interpretation.

Safe examples:
- "I feel more comfortable doing this."
- "I've done enough of this that the same work is a little quicker for me now."
- "I remember Bex guiding me through it."

The UI must visually attribute these statements.

Recommended placement:
existing **Citizen Interpretation** continuity layer.

Do not automatically construct interpretation from:
- practice_count
- duration_reduction_percent
- completed guided sessions

Assets should display Communication-provided language only.

---

# Asking for Help

The UI does not need a "Find trainer" or "Ask expert" control.

Citizens may naturally ask:
- "Have you done much extraction?"
- "Could you show me how you approach this?"

This is Communication/planner behavior.

Assets should not inspect global competence snapshots to recommend another citizen.

That would create an omniscient expertise lookup.

If a future UI allows a visitor to inspect factual citizen history, it should remain read-only evidence, not matchmaking/authority.

---

# Citizen Sheet Stage 2 Layout

Existing Stage 1 continuity block should remain the host.

Recommended order:

## Evidence / Record

1. Ongoing Plans
2. Recorded Practice
   - family counts
   - recent practice rows
   - optional measured work effect line
3. Guided Practice History
   - factual session rows

## Remembered Perspective

4. Relevant Memories
   - ordinary practice recall
   - guided-practice recall
   - source role/counterparty

## Citizen Interpretation

5. Self-reflection / recognition language
   - attributed
   - no objective stat styling

Do not create a new top-level Skills tab.

---

# Recommended Practice Family Row

Example:

> **Extraction**  
> 6 recorded events  
> 5 completed • 1 failed  
> Measured work effect: comparable extraction tasks are 4.25% shorter.

This is sufficient.

No bar is necessary.

## Why no bar

A bar needs an implied maximum.

There is no meaningful citizen-facing "100% extraction" state.

The physical effect cap is an implementation safety bound, not a mastery scale.

Using the 8% cap as a 100% visual endpoint would incorrectly transform an engineering cap into a proficiency system.

Therefore:

> **Never map duration reduction / 8% cap onto a visual mastery bar.**

---

# Guided Session Row Fields

From Simulation session history, use only straightforward event metadata such as:
- session ID
- activity family
- teacher ID/name
- learner ID/name
- status
- started minute
- completed minute
- source conversation ID when useful
- consumed learner job ID only in deep Records/debug context if needed
- summary

Do not show historic teacher/learner practice counts captured inside the session as proof of rank.

Those counts explain Simulation legality/audit, not citizen-facing identity.

---

# Home Screen

No Stage 2 competence display on Home.

Do not add:
- skill icons
- competence badges
- practice count chips
- training indicators

Home stays focused on current activity.

If a citizen is physically in a guided-practice job, the existing current-activity display may naturally say so because Simulation owns that activity string.

That is enough.

---

# Records

Records may later contain a deeper factual archive:
- competence-family evidence rows
- guided-practice session history
- source practice event IDs

Still no:
- leaderboard
- rank ordering
- "top citizen"
- skill matrix heatmap

A matrix of citizens × competence families would strongly imply ranking even if technically factual.

Avoid unless the coordinator explicitly wants a diagnostic/admin-only surface.

---

# Empty States

Use:
- No recorded practice in this activity family.
- No guided-practice sessions recorded.
- No relevant guided-practice memory is active right now.

Do not use:
- Untrained
- Novice
- Skill level 0
- No mentor
- Training not unlocked

---

# Runtime Dependencies

## Simulation — ready

Branch:
`simulation/v0.9-competence-stage2`

Head:
`667f4659aeef9a9658d7e08f4ba7c54e267a38f9`

Safe endpoint:
`GET /api/competence/{citizen_id}`

## Memory — ready

Branch:
`memory/v0.9-experience-stage2`

Head:
`d4e91866e41eb6fd33a4459fc9bd057ac28a6ba5`

Safe endpoint remains:
`GET /api/memory/continuity/{citizen_id}`

No new Memory endpoint is required.

## Communication — ready

Branch:
`communication/v0.9-guided-practice-stage2`

Head:
`6af2f6cb8b9fe3d44b30c9dad2fc6e54926b09cf`

Interpretation/language contract is ready.

## Coordinator — still required before runtime work

Assets must implement only from the coordinator's assembled Stage 2 integration base.

Do not build runtime UI by merging department branches inside Assets.

---

# Runtime Implementation Recommendation

When coordinator hands off the assembled Stage 2 base:

1. extend existing Citizen Continuity cache/load path with `/api/competence/{citizen_id}`
2. keep existing Stage 1 `/api/continuity/{citizen_id}`
3. keep existing `/api/memory/continuity/{citizen_id}`
4. add competence-family factual rows under Recorded Practice
5. add measured work-effect text only when reduction > 0
6. add Guided Practice History rows
7. allow Memory's guided-practice events to appear naturally in Relevant Memories
8. display Communication interpretation only through safe attributed language
9. add Stage 2 Assets smoke guarding all no-RPG constraints

No new top-level navigation is needed.

---

# Acceptance Criteria

Stage 2 Assets UI is acceptable only if:

1. practice counts remain historical evidence
2. duration reduction is labelled as measured physical work effect
3. duration reduction is never a bar/proficiency meter
4. no frontend-derived competence exists
5. teacher/learner remain event roles
6. guided session itself is not shown as competence gain
7. no mentor/trainer/expert badge exists
8. no cross-citizen competence leaderboard exists
9. Memory recall still hides recall/reinforcement scores
10. Communication interpretation is visibly attributed
11. objective effect and interpretation remain visually distinct
12. Home gains no competence clutter
13. current Stage 1 continuity surfaces remain intact
14. no `update.json` change occurs

---

# Core Stage 2 UI Principle

> **Practice can change how work performs. The interface should show the evidence and the measured effect without turning either into a title.**
