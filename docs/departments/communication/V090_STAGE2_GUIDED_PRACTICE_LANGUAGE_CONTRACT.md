# Communication & Perception — v0.9 Stage 2 Guided Practice & Competence-Safe Language Contract

_Last updated: 2026-09-29_

## Purpose

Stage 2 lets citizens talk naturally about real repeated practice, measured physical effects, asking for help, and real guided-practice sessions without turning any of those into titles, ranks, reputation, or magical skill transfer.

Core laws remain:

- information must have a legitimate source path
- Simulation owns physical competence effects and guided-practice events
- Memory owns bounded autobiographical recall
- Communication owns perspective-safe language

## 1. Three different evidence layers

### Objective physical effect

Simulation may expose a citizen's own bounded task-time effect derived from canonical practice evidence.

Communication may surface that as a current self fact, for example:

- "I currently finish comparable extraction tasks a little faster from past practice."

Communication must not convert that into:

- expert
- specialist
- level
- proficiency rank
- permanent role

A measured effect is current physical performance state, not social identity.

### Remembered personal practice

Present autobiographical language comes from Memory active practice recall:

- practice_recall_snapshot_for(...)
- practice_recall_context_for(...)

The full durable practice ledger remains objective archive/history only.

A citizen may have a measurable physical effect even when the old source practice is not currently recalled.

In that case, Communication may describe the current effect but must not invent the forgotten autobiographical story.

### Recognition of another citizen

Recognition of another citizen remains speaker-owned perspective Memory only.

Communication must not inject the other citizen's objective competence snapshot into the speaker's dialogue context.

## 2. Asking for help

A citizen may ask another citizen about their experience even when they do not know the answer.

Safe:

- "Have you done much extraction?"
- "Could you show me how you approach this?"
- "What worked for you last time?"

Unsafe without evidence:

- "You're the best extractor, so teach me."
- "You have seven extraction runs, so you're more qualified."

A question is not itself a competence claim.

If speaker-owned Memory contains relevant prior experience with the counterpart, the citizen may use that source-backed history honestly when asking.

## 3. Ordinary explanation versus guided practice

Ordinary face-to-face conversation may transfer:

- claims
- advice
- instructions
- remembered experience
- hypotheses
- suggestions

It creates no physical competence.

A real guided-practice session is a Simulation-owned physical event with:

- guided_practice_sessions.id
- teacher citizen ID
- learner citizen ID
- activity family
- physical job ID
- start/completion time
- optional source conversation ID
- optional consumed learner job ID

Conversation may propose or discuss guided practice.

Conversation alone does not start it.

## 4. Current guided-practice availability

Communication may tell a citizen that they can currently propose/start guided practice only when that citizen's own legal Simulation action list exposes a guided_practice action.

This is a self-owned capability surface.

Communication must not query another citizen's hidden/global competence ledger to tell the speaker who can teach them.

If the speaker does not know another citizen's experience, they may ask.

## 5. Teacher and learner are event roles

Teacher and learner identify roles in one real guided-practice event.

They are not permanent identities.

Do not create authoritative labels such as:

- mentor
- trainer
- expert
- master
- specialist
- leader
- senior
- instructor rank

A citizen may naturally say:

- "Bex guided me through extraction practice last time."

when active Memory recalls that source-backed event.

They may not conclude:

- "Bex is my permanent mentor."

unless a future social system establishes such a relationship through its own source-backed history.

## 6. Guided practice itself grants no competence

A completed guided-practice session is a real experience, but it is not learner practice evidence by itself.

Simulation may allow that completed session to modestly affect the learner's next matching real task.

Only the learner's later physical task creates new canonical practice evidence.

Communication must preserve this difference.

Safe:

- "Bex guided me through extraction practice."
- "I later used that guidance during an extraction run." when recalled source evidence supports it.

Unsafe:

- "The session made me skilled at extraction."
- "Bex taught me extraction, so I'm now an expert."

## 7. Measured effect versus interpretation

Simulation owns measured physical effect.

The citizen owns interpretation.

Example:

Objective:
- matching extraction tasks currently receive a small source-backed duration reduction

Interpretation:
- "I feel more comfortable doing this now."

The interpretation does not replace the objective source, and the objective source does not create an identity label.

## 8. Disagreement is allowed

Two citizens may assess the same person's experience differently because they may have different Memory.

One citizen may remember seeing Bex guide extraction practice.

Another may know nothing about it.

There is no global reputation packet that resolves the disagreement automatically.

## 9. Memory source rules

Communication may consume:

- practice_recall_snapshot_for(...)
- practice_recall_context_for(...)
- guided_practice_recall_snapshot_for(...)
- guided_practice_recall_context_for(...)
- causal_recall_snapshot(...) for counterpart recognition

Model-facing context must not expose:

- recall_score
- reinforcement_count
- hidden salience math
- global practice ledgers for another citizen

## 10. Simulation source rules

Communication may consume for the speaker's own current state:

- competence_snapshot(...)
- current legal possible_actions(...)

Model-facing measured-competence language should expose only bounded physical effect, not hidden weighted-evidence math or raw global comparison values.

Communication must not use competence_snapshot(other_citizen) as social recognition evidence.

## 11. Planner boundary

If guided_practice appears in legal actions, planner may choose it as a real physical action.

The planner must understand:

- legality means the session can be attempted
- session completion itself creates no learner practice/competence
- no expert/mentor/title follows from legality
- ordinary talk is not skill transfer

Simulation remains authoritative for start, duration, completion, one-use guidance support, and later learner practice.

## 12. Visitor boundary

Visitor conversation may discuss:

- the citizen's own remembered experience
- the citizen's own measured physical effect
- source-backed past guided-practice experiences

Visitor conversation does not create:

- a citizen-citizen guided-practice session
- visitor competence
- skill transfer
- social authority

Current citizen-to-citizen guided-practice legal options are not injected into visitor dialogue.

## 13. Non-goals

This stage does not add:

- XP
- levels
- skill trees
- universal expertise
- trainer/mentor titles
- reputation
- remote competence lookup
- conversation-based competence
- frontend-derived competence

## Canonical source chain

For guided-practice continuity:

Simulation guided_practice_sessions.id
→ Memory role-specific event
→ bounded active recall
→ Communication perspective-safe language

For the learner's later competence growth:

real learner job
→ practice_events.id
→ Memory retained practice
→ bounded recall
→ self-assessment language

## Acceptance examples

### Safe

"I remember Bex guiding me through extraction practice."

"I've done this enough that the same work is a little quicker for me now."

"Have you worked with this before? Could you show me your approach?"

### Unsafe

"Bex is our extraction expert."

"I explained fabrication to Cato, so Cato is better at it now."

"I know I completed eight extraction jobs" when active Memory does not currently recall that archive history.

"Cato should ask Bex because the database says Bex has a higher competence score."

## Runtime integration

Communication Stage 2 extends:

- agent_city/continuity_language.py
- agent_city/comms.py
- agent_city/planner.py
- main.py

The implementation is merge-order safe. If Stage 2 Memory/Simulation modules are absent, no Stage 2 evidence is invented.
