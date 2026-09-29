# Agent City v0.9 — Civilization Continuity Doctrine

_Last updated: 2026-09-29_

## Purpose

v0.9 is the milestone where Agent City stops treating each autonomous choice as an isolated decision and begins making the present meaningfully descend from recorded history.

The target is not a class system, scripted character arcs, or decorative lore.

The target is:

> **A citizen's current choices should increasingly be explainable by what they actually experienced, learned, attempted, remembered, discussed, succeeded at, failed at, and chose to continue.**

Existing project laws remain authoritative:

> **The AI may decide intent. The simulation decides reality.**

> **A citizen only knows what information could actually have reached them.**

v0.9 adds a third continuity law:

> **Persistent behavior must have a traceable history.**

---

## Architecture Lock 1 — Memory Is Causal Infrastructure

Memory is not flavor text and not a post-hoc biography generator.

Persistent plans, habits, confidence, preferences, social expectations, place attachment, and self-assessment may be influenced by retained history only when that history is backed by real events or legitimate communication.

Memory must therefore support:

- durable source identity
- citizen-scoped ownership
- bounded retrieval
- relevance weighting
- salience
- reinforcement through repeated related experience
- uncertainty / claim status where appropriate
- meaningful aging or reduced retrieval priority without silently rewriting history
- retrieval that survives prompt/context limits

The model must never receive an unbounded life transcript.

The Memory layer should provide the smallest relevant continuity packet needed for the current decision.

### Required causal chain

Preferred pattern:

`real event / received claim → retained memory → relevant retrieval → citizen interpretation → new intent → Simulation validation → new real event`

Forbidden pattern:

`hidden stat / author label → behavior → retroactive story explaining it`

---

## Architecture Lock 2 — No Identity Labels As Behavioral Causes

Citizens may become more experienced at activities, but the system must not turn experience into permanent classes.

Do not create behavior-causing identity fields such as:

- `role = miner`
- `class = engineer`
- `specialization = researcher`
- `personality_job = builder`

Internal experience metrics may exist if they are grounded in actual practice and used carefully, but they are evidence about history, not a canonical identity.

A citizen may become more likely to choose work they have repeatedly performed successfully because:

- they remember doing it,
- they have accumulated relevant practice,
- they have evidence that they are effective,
- they have unfinished plans connected to it,
- others have legitimately asked for or recognized their help.

The cause must be history, not a title.

---

## Architecture Lock 3 — Recognition Emerges Socially

The system must not declare that a citizen "is the expert" as objective social truth merely because an internal metric is high.

Recognition should emerge through perspective.

Examples:

- Bex may remember repeated successful extraction work.
- Cato may remember Bex helping with difficult field work.
- Noma may have a different assessment based on a failure she witnessed.
- Bex may eventually say, "I've done this a lot," or "I'm good at this," if her own retained experience supports that statement.
- Another citizen may say, "Bex has more experience with this than I do," if their own knowledge supports the comparison.

Those statements remain citizen perspectives unless the underlying factual part is independently supported.

No automatic titles, ranks, guild roles, leadership weight, or social authority are created from recognition.

---

## Architecture Lock 4 — Experience Must Come From Practice

Skill growth must descend from real completed actions and outcomes.

Potential inputs include:

- successful or failed extraction
- fabrication
- construction
- surveys / inspections
- maintenance
- experiments
- travel / logistics work
- teaching or guided practice, once a real teaching mechanism exists
- other future Simulation-owned action types

Experience must not increase from:

- merely talking about an activity
- agreeing to do it
- being near someone who performs it
- hidden coordinator/admin edits presented as normal history
- concept art or UI labels

If competence affects physical outcomes, Simulation owns the effect and its limits.

Memory may explain how the citizen interprets that experience.

---

## Architecture Lock 5 — Plans Persist, But They Are Not Destiny

Citizens may form multi-step plans that survive beyond one action.

A persistent plan must have:

- owner
- creation time
- initiating reason / evidence
- current intent
- current state
- source history
- next known step or unresolved question
- revision / abandonment history
- completion or failure state when applicable

Plans may be:

- continued
- revised
- paused
- superseded
- abandoned
- completed

A plan is not a command queue.

The citizen must be able to change course when:

- required material is unavailable
- new evidence undermines the premise
- energy / maintenance needs intervene
- another higher-priority concern emerges
- the citizen simply re-evaluates the plan based on legitimate context

Planner chooses intent.
Simulation still validates every physical step.

---

## Architecture Lock 6 — Habits Must Be Repeated History, Not Templates

A routine or preference may emerge only from repeated behavior or repeated successful choices.

Examples that may eventually become real:

- a citizen often performs maintenance during evening wind-down
- a citizen repeatedly visits Resin Grove during active hours
- two citizens frequently talk after returning from field work
- a citizen prefers one fabrication method after repeated success with it

Do not seed arbitrary lifestyle routines merely to make the city feel alive.

The system should distinguish:

- one-off action
- repeated pattern
- strong recurring tendency
- socially recognized custom

The threshold for each must be explicit and evidence-backed.

---

## Architecture Lock 7 — Places Accumulate Citizen-Specific Meaning

Physical place truth remains Simulation-owned.

Meaning is citizen-scoped.

The same place may legitimately carry different remembered significance for different citizens.

Example:

**Resin Grove**
- Iri may remember nearly exhausting her battery there.
- Cato may remember repeated plant-fiber trips.
- Bex may remember a useful extraction lesson.
- N7 may remember walking there with a citizen.
- A citizen who never went there and never heard about those events does not inherit those meanings.

Place attachment or aversion must descend from retained events, not from generic authored location mood.

---

## Architecture Lock 8 — Visitor Continuity Must Be Earned By Real Encounters

A visitor may become part of a citizen's social history only through real, source-linked interaction.

Eligible examples:

- face-to-face visit
- completed shared physical activity
- useful information genuinely exchanged
- repeated conversations
- a promise later fulfilled or broken, once promise tracking is explicitly supported

A citizen may later remember:

"N7 walked with me to Resin Grove."

only if a real visit/shared-action chain supports it.

The system must not manufacture visitor importance from frequency of UI use, account ownership, coordinator status, or hidden admin access.

Visitors remain visitors, not rulers.

---

## Architecture Lock 9 — Self-Assessment Must Be Evidence-Backed

Citizens may form beliefs about themselves.

Examples:

- "I've gotten better at this."
- "I keep having trouble with delicate repairs."
- "I know this route well."
- "I tend to work better with Cato on hauling jobs."

These statements should emerge from retrieved personal history and real outcomes.

A self-assessment is still a belief or interpretation, not automatically an objective fact.

The planner may use it as a soft bias.
Simulation remains authoritative for physical capability.

---

## Architecture Lock 10 — Social Memory Is Perspective, Not Global Reputation

There is no universal reputation score.

If social recognition is added, it must remain citizen-to-citizen and source-backed.

Each citizen may retain different impressions based on:

- what they personally observed
- what was told to them
- what they jointly experienced
- whether prior cooperation succeeded or failed
- how recent / repeated / salient those interactions were

Do not collapse those perspectives into a single canonical "Bex reputation = 82" that drives everyone identically.

Aggregate metrics may exist for diagnostics, but not as citizen knowledge or an invisible social law.

---

## Architecture Lock 11 — Forgetting Must Reduce Access, Not Rewrite The Past

The city needs bounded context, so not every memory can remain equally retrievable forever.

Forgetting/decay may affect:

- retrieval priority
- detail richness
- confidence in minor details
- availability of low-salience events

It must not:

- change what physically happened
- silently reverse known facts
- erase source provenance from durable records
- fabricate a different past
- remove high-salience continuity merely because a prompt window is small

Durable archive and active recall are separate concepts.

---

## Architecture Lock 12 — Culture Requires Repetition Plus Transmission

Social customs or traditions may emerge only when real repeated behavior becomes socially recognized and transmitted.

Required ingredients should include some combination of:

- repeated event pattern
- multiple participants or observers
- retained social memory
- communication about the pattern
- continued voluntary repetition

One repeated behavior by one citizen is a habit, not a culture.

A coordinator may not simply author:

"Every evening the citizens gather."

The city must actually do it often enough for citizens to notice and continue it.

---

# v0.9 Stage Order

## Stage 1 — Causal Memory + Persistent Plans

Primary goal:
establish the continuity spine before adding visible specialization.

Memory first defines:
- salience model
- bounded retrieval contract
- reinforcement/related-event linking
- active recall vs durable archive
- citizen-specific self/place/social continuity packets
- provenance requirements

Simulation / planner then define:
- persistent plan state
- plan revision/abandonment
- next-step continuity
- action/outcome references

Acceptance:
- a citizen can resume a meaningful unfinished plan after unrelated actions and time have passed
- the retrieved reason for resuming is traceable to retained history
- a citizen with no relevant history does not receive invented continuity

## Stage 2 — Practice, Competence, Teaching, Recognition

Primary goal:
allow repeated real work to create differentiated capability without classes.

Define:
- practice/experience accumulation from completed actions
- bounded competence effects owned by Simulation
- self-assessment from personal evidence
- social recognition from legitimate observation/communication
- teaching only through explicit physical/social mechanisms

Acceptance:
- two citizens can become differently experienced through different histories
- neither receives a permanent class/title
- other citizens may notice the difference only when they have grounds to know it

## Stage 3 — Habits, Place Meaning, Social Customs

Primary goal:
allow repeated history to create recognizable long-term patterns.

Define:
- routine detection
- place-specific personal meaning
- recurring cooperation patterns
- socially transmitted customs
- UI surfaces for continuity without exposing hidden scoring

Acceptance:
- present-day patterns can be traced to prior repeated events
- deleting the history would remove the justification for the pattern
- no culture/custom appears solely because a template said it should

---

# Cross-Department Authority

## Memory & Social
Owns:
- retained continuity
- salience
- retrieval
- source links
- citizen-scoped social/place/self memory
- active recall vs archive boundary

Does not own:
- physical outcome
- competence physics
- action legality
- global social truth

## World & Simulation
Owns:
- completed physical action/outcome
- plan-state legality where physical state is involved
- competence effects on real work
- energy/material/tool/world constraints
- canonical event anchors

Does not own:
- what a citizen remembers
- social interpretation
- identity labels

## Communication & Perception
Owns:
- what was actually said
- who could hear/receive it
- claim vs verified-fact distinction
- perspective-safe social recognition language
- future teaching/social-transfer conversational surface

Does not own:
- skill gain merely from dialogue
- physical completion
- canonical identity/reputation

## Assets & Interface
Owns:
- presentation of plans, history, routines, experience, and relationships once safe read models exist
- visual continuity cues

Must not:
- expose hidden scores as identity
- invent titles/classes
- turn diagnostic aggregate metrics into citizen-visible truth
- imply a routine/custom exists before the underlying evidence supports it

---

# Anti-Patterns

Do not ship v0.9 features that amount to:

- RPG classes hidden behind "emergent specialization"
- arbitrary XP detached from completed actions
- a universal reputation number
- global omniscient memory
- authored habits that did not emerge
- automatic friendship/attachment because two entities share screen time
- plans that behave as hard scripts
- memories invented to justify current behavior
- cultural traditions generated from flavor text
- visitor favoritism based on account ownership
- summaries that become evidence without a source chain

---

# v0.9 Success Test

A strong v0.9 city should support questions like:

- Why does this citizen keep returning to Resin Grove?
- Why does Bex prefer this kind of work?
- Why does Cato trust or not trust Bex's field judgment?
- Why did this plan get abandoned?
- Why does Iri avoid running her battery so low now?
- Why does this place matter to Noma?
- Why do these two citizens often work together?
- Why does a citizen remember N7?

The answer should be reconstructable from actual recorded history.

If the explanation ultimately reduces to a hard-coded label, hidden class, fabricated memory, or generic personality sentence, Civilization Continuity has failed.
