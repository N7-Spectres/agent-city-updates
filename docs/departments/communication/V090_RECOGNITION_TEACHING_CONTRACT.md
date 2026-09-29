# Communication & Perception — v0.9 Recognition, Self-Assessment & Teaching Contract

_Last updated: 2026-09-29_

## Purpose

v0.9 allows citizens to talk naturally about experience and continuity without
turning practice history into classes, titles, reputation, or magical social
knowledge.

This contract sits between:

- Memory's owner-scoped causal recall,
- Simulation's canonical plans/practice events,
- and actual face-to-face language.

Core laws remain:

A citizen only knows what information could actually have reached them.

Persistent behavior must have a traceable history.

## 1. Self-Assessment Source Rule

A citizen may describe their own experience using their own canonical physical
practice evidence.

Authoritative physical source:

practice_events

Examples that may be supported:

- "I've done this before."
- "I've done this several times."
- "I've had trouble with this more than once."
- "I feel more practiced at this now."

Communication may summarize counts to the citizen, but the count is evidence
about personal history, not a skill score.

### "Several times" rule

Communication permits the phrase "I've done this several times" only when the
same citizen has at least three real practice events for that activity.

This is a language threshold only.

It is not:

- XP
- level
- specialization
- rank
- objective competence
- permanent identity

## 2. Self-Assessment Is Interpretation

Simulation can prove that physical practice happened.

Memory can surface the relevant source-backed experiences.

The citizen may interpret those experiences.

Examples:

- "I think I'm getting better at repairs."
- "I still don't trust myself with delicate assembly."
- "I feel more comfortable on this route now."

These are citizen beliefs.

They are not automatically physical capability facts.

If competence later changes real outcomes, Simulation owns those effects.

## 3. Recognition Of Another Citizen Is Perspective

Communication must never inspect another citizen's global practice history and
present it as though the speaker personally knew it.

Recognition about another citizen may use only information available through
the speaker's owner-scoped Memory.

Allowed evidence paths include:

- something the speaker personally experienced with the other citizen,
- something the other citizen actually told them,
- a legitimate received claim,
- future direct observation Memory,
- other source-backed Memory that belongs to the speaker.

### Example

Cato may say:

"I've seen Bex handle this before."

only if Cato's own retained history supports that statement.

Cato may not say:

"Bex has 14 extraction events, so she's our extraction expert."

merely because Simulation stores Bex's practice history.

## 4. No Global Reputation Or Titles

Recognition never creates canonical social identity.

Forbidden authoritative labels include:

- expert
- master
- specialist
- trainer
- mentor
- leader
- senior
- rank
- class
- reputation score

A citizen may use ordinary subjective language such as:

- "I'd ask Bex first."
- "She seems more practiced at that than I am."

only when their own evidence supports the perspective.

No invisible civilization-wide reputation is created.

## 5. Comparative Claims Need Comparative Evidence

Statements such as:

"Bex has done this more than I have."

need evidence available to the speaker for both sides of the comparison.

The speaker's own practice count alone is insufficient.

Another citizen's hidden/global practice count is never a valid Communication
source.

If the speaker only knows that Bex has done the activity before, use weaker
language:

"I know Bex has worked on this before."

## 6. Repetition Does Not Upgrade Truth

Memory reinforcement means easier recall.

It does not mean a claim becomes more true.

Three repeated unverified reports remain unverified reports.

Recognition language must preserve the underlying verification/source state.

## 7. Teaching Conversation Boundary

A citizen with real personal practice may explain:

- what they did,
- what they observed,
- what worked or failed,
- what they would try next,
- how they personally approach the task.

But conversation alone creates:

- no learner practice event,
- no competence gain,
- no skill transfer,
- no physical success,
- no teaching credential.

Until Simulation defines a real guided-practice/teaching mechanism:

Explanation is communication, not practice.

A listener may remember the explanation as a claim/social event.

They do not become more competent merely because they heard it.

## 8. Future Guided Practice

If a real teaching mechanism is added later, it must have Simulation-owned
physical/action evidence.

Potential future source requirements:

- teacher citizen ID
- learner citizen ID
- canonical guided-practice action/job ID
- activity type
- physical task performed
- outcome
- completion minute
- any competence/practice effect explicitly owned by Simulation

Communication may then connect teaching conversation to the real action, but may
not manufacture the effect itself.

## 9. Persistent Plans In Conversation

Simulation owns canonical citizen_plans.

Communication may safely discuss:

- plan ID
- status
- current intent
- next step
- unresolved question

Conversation may:

- ask about a plan,
- question it,
- suggest revision,
- discuss alternatives,
- express confidence/doubt.

Conversation does not itself:

- create
- revise
- pause
- resume
- abandon
- supersede
- complete

the canonical plan.

A plan is intent, not competence and not guaranteed future completion.

## 10. Visitor Continuity

A citizen may recognize a visitor only from real retained interaction:

- visits,
- durable exchanges,
- completed shared activities,
- legitimate visitor-linked Memory.

UI/account ownership creates no importance, authority, or special status.

Example:

"We've walked together before."

requires a real retained shared-activity source.

## 11. Runtime Integration

Communication's v0.9 language adapter lives in:

agent_city/continuity_language.py

It consumes optional upstream APIs after coordinator integration.

Memory:
- causal_recall_snapshot(...)

Simulation:
- practice_snapshot_for(...)
- plan_snapshot_for(...)

The adapter is merge-order safe. If upstream modules are absent, it returns no
invented evidence.

## 12. Model-Facing Sections

Communication may provide bounded sections such as:

- SELF-ASSESSMENT EVIDENCE
- PERSPECTIVE-SAFE RECOGNITION
- PERSISTENT PLAN DISCUSSION
- TEACHING / EXPLANATION BOUNDARY
- VISITOR CONTINUITY

These sections are evidence packets and language constraints.

They are not identity labels.

## 13. Non-Goals

This stage does not add:

- competence score
- skill tree
- XP
- class
- role promotion
- expert badge
- leader selection
- universal reputation
- teaching skill transfer
- social authority weight
- global knowledge of other citizens' practice

## Acceptance Examples

### Safe self-description

If Bex has four source-backed extraction practice events:

"I've done extraction several times."

Safe.

"I'm the settlement's extraction expert."

Not supported.

### Safe recognition

If Cato remembers working beside Bex during extraction:

"I've seen Bex do this before."

Potentially safe.

If Cato has no such Memory:

"Bex is more experienced than I am."

Not supported merely from hidden Simulation counts.

### Safe teaching

"I can tell you what worked for me last time."

Safe if personal practice supports it.

"I taught Cato fabrication, so he's better at it now."

Not supported without a future Simulation guided-practice event.

### Safe plan discussion

"I'm still trying to finish that Resin Grove follow-up."

Safe if the canonical plan exists.

"We talked about finishing it, so the plan is complete."

Never valid.
