# Communication & Perception — Decisions

## Information Travel Rule

> **A citizen only knows what information could actually have reached them.**

Information can currently arrive through:

- direct observation at the same location
- face-to-face conversation
- personal experience
- persistent memory of those experiences

Future mechanisms may include physical records or invented signaling systems.

## No Free Remote Communication

Do not grant radios, phones, networks, telepathy, or live status feeds.

If long-distance communication appears, it must come from:

1. a real citizen need
2. relevant discovered knowledge
3. available materials/components
4. a valid fabrication/construction process
5. a physically existing communication system

The civilization may invent something other than radio.

## Last-Known Knowledge

Remote status should be represented as last-known information when appropriate.

Example:

> "Last I heard, Cato was surveying Resin Grove."

Not:

> "Cato is surveying Resin Grove right now."

unless the speaker has a real current information path.

Age is derived from simulation time and the receive/observe timestamp. A last-known record never silently upgrades itself to live truth.

## Claims Are Not Physical Truth

Information communicated by another citizen is a speaker claim unless independently verified through an authoritative physical event or direct observation.

Repeated retelling does not convert a claim into truth.

## Direct Observation

Physical co-location allows ordinary observation, but observation should not automatically expose hidden internal state.

Direct observation may expose externally visible presence and locally observable physical facts. It does not automatically reveal private plans, internal motives, energy, inventory contents, or remote destinations.

## Planner Boundary

A citizen planner may receive:

- that citizen's own validated state
- current local observations that the citizen could physically perceive
- bounded remembered information that reached that citizen through a valid mechanism
- legal actions from Simulation

It must not receive another citizen's live remote location/activity or globally discovered resources merely because the simulation knows them.

Simulation may use hidden truth to decide action legality, but human-readable labels/reasons supplied to the planner must not leak that hidden truth.

## Canonical Conversation Source

`citizen_conversations.id` is the canonical immutable source ID for a stored citizen-to-citizen exchange.

Existing Memory references using:

- `source_type = 'citizen_conversation'`
- `source_id = citizen_conversations.id`

must remain valid.

Any later transfer/provenance layer must map back to this canonical raw conversation source rather than replacing or renumbering it.

## Physical Talk Link

For new source-linked autonomous conversations:

- `citizen_conversations.source_job_id` references the physical `talk` job
- the field is nullable for legacy conversations
- when present, it is unique
- retries for the same physical talk return/reuse the same conversation record rather than creating duplicates
- a conversation may only be committed while the matching talk job and co-location are still valid

Do not retroactively invent a `source_job_id` for legacy rows when the physical source cannot be established unambiguously.

## Talk Completion Integrity

A physical `talk` job must not be recorded as successfully completed unless a source-linked stored conversation exists.

If the talk reaches its due time without that record:

- release the participants
- mark the job failed
- record that the attempt ended without a recorded exchange
- do not create a conversation or information-transfer record afterward from stale generated text

This preserves the boundary:

> **No stored information transfer without a real, valid face-to-face event.**

## Generation Failure

Model/network/JSON failure must not be converted into invented fallback dialogue and persisted as though the citizens actually said it.

A failed generation may result in a failed conversation attempt, but it does not create remembered claims.

## Memory Projection Boundary

The raw stored conversation is the durable communication source.

Memory is a derived projection. If Memory projection temporarily fails, that must not erase or invalidate the durable conversation record. Its idempotent migration/backfill can repair the projection later.

## Provenance Record

The deeper provenance contract remains defined in `PROVENANCE_CONTRACT.md`.

Important distinctions remain:

- `personal_experience`
- `direct_observation`
- `face_to_face_claim`
- `validated_observation` versus `speaker_claim`
- `unverified`, `verified`, and `contradicted`

Legacy conversation summaries remain participant-accessible historical text with unknown claim-level provenance. Do not fabricate precise fact transfers retroactively.

## Ownership Boundary

Communication determines what information can move.

Simulation determines what physically happened.

Memory determines how communicated/observed information persists and how bounded retrieval is presented later.

## Provenance Contract Authority

Until replaced by a later explicit architecture decision, `PROVENANCE_CONTRACT.md` is the Communication-owned interface for deeper information provenance.

Do not weaken the planner boundary to compensate for missing memory/provenance plumbing. Unknown remote state must remain unknown rather than falling back to simulation-global truth.

## v0.5 Integration Gate

A v0.5 integrated runtime is not acceptable if merging Simulation reintroduces the old conversation mismatch.

The integrated `db.py` / `simulation.py` must preserve **both** departments' physical schema additions:

- Simulation: equipment/projects/project materials/job outcomes/coordinates/structure placement
- Communication: nullable unique `citizen_conversations.source_job_id` and talk completion validation

Required combined invariant:

> A `talk` job may be physically complete only when its real stored conversation exists.

If no source-linked conversation exists at due time, the talk job fails and no information transfer is invented.

Combined integration testing must run both Simulation's v0.5 physical smoke coverage and Communication's v0.5 conversation-integrity smoke coverage before release.

## v0.6 Information Receipt Authority

Communication's minimum durable provenance primitive is an **information receipt**.

A receipt records that one specific citizen received one specific piece of information through one real mechanism. It does not assert that the information is globally true unless its assertion/verification fields say it came from an authoritative validated observation.

This layer remains separate from:

- Simulation hidden world truth
- Memory's retention/retrieval projections
- UI presentation

## Validated Versus Claimed Knowledge

Simulation-grounded observation, survey measurement, experiment result, or personal physical experience may enter Communication through `record_validated_information(...)`.

Such records require an authoritative physical event reference and are stored as verified observations.

Face-to-face statements are different:

- they are tied to the canonical stored conversation
- they are attributed to the actual speaker
- they are received only by the other participant
- they begin `unverified`
- retelling does not verify them

A later verified observation may coexist with an earlier claim. Do not erase the historical claim merely because later evidence differs.

## Transcript-Grounded Claim Rule

Structured claim extraction may classify or tag dialogue, but it may not invent the underlying assertion.

The persisted claim `value_text` must be a verbatim sentence/clause present in the durable stored text of the attributed speaker.

If the extracted value is not present in that transcript, no receipt is created.

This protects the provenance ledger from a second model-generated fiction layer.

## Knowledge Is Recipient-Local

A validated discovery has a physical truth source, but it becomes citizen knowledge only for recipients who actually observed/received it.

One citizen discovering a property does not populate all citizens' knowledge.

Any later propagation requires another valid Communication mechanism.

## Current Direct Observation Is Derived

A citizen's present physical location may be exposed as a current direct observation without fabricating a historical receipt.

Historical knowledge requires a real receipt/event source.

## Consumer Read Models

Communication's `GET /api/knowledge/{citizen_id}` is a low-level provenance-oriented view.

For ordinary v0.6 Citizen/Location UI, prefer Memory's bounded consumer knowledge endpoints after integration. This prevents Assets from depending directly on raw provenance internals and preserves Memory ownership of bounded retention/retrieval.

## Visitor Availability Privacy

Visit accessibility states are structured separately from human-readable messages.

When visitor and citizen are remote, the response should not reveal local busy/talk counterpart details merely to explain inaccessibility.

When co-located, busy/talking/traveling states may be reported accurately.

Talk counterpart identity must be resolved from both job roles, not by assuming the selected citizen is always the initiator.

## Simulation Knowledge vs Communication Provenance

v0.6 deliberately uses two different layers with different meanings:

### Simulation `agent_city/knowledge.py`

Owns:
- validated `discoveries`
- current `citizen_knowledge` links to validated discoveries
- physical experiment/discovery truth
- safe validated property/deposit retrieval

This is not Communication's module.

### Communication `agent_city/provenance.py`

Owns:
- immutable information receipt history
- source/time/age
- unverified face-to-face claims
- transfer event references
- historical record that a validated fact reached a particular citizen

Communication may sync recipient-local **verified** Simulation knowledge into receipts, but must never scan hidden `world_properties` and grant knowledge itself.

Simulation rows with `verification_state = reported` are not promoted into verified receipts by synchronization.

Persisted experiment results, including inconclusive attempts, may become verified *experience/result* receipts for the citizen who performed them. This verifies that the experiment had that result, not a hidden property that was not discovered.

This separation avoids both an omniscient encyclopedia and a duplicate authority system.

## Session Close Integration Invariants

The next integrator must preserve all of these together:

- Simulation `agent_city/knowledge.py` remains authoritative for hidden truth, discoveries, and current validated citizen knowledge.
- Communication `agent_city/provenance.py` remains authoritative for transfer/source/time receipt history and unverified face-to-face claims.
- Memory remains the bounded retention/retrieval layer.
- Assets consumes safe read models and structured availability, not hidden truth.
- `citizen_conversations.id` remains the canonical raw conversation source.
- `source_job_id` remains the physical talk-job anchor.
- `reported` Simulation knowledge is never silently upgraded to verified Communication knowledge.
- unverified conversation claims remain unverified until separately validated.
- remote visitor access never exposes local busy/talk detail.
- there is still no free remote communication channel.

If a merge forces a choice between these layers, the merge is incorrect. They are complementary, not substitutes.

## v0.7 Raw Exchange First

A valid durable raw conversation and claim/provenance enrichment are separate reliability domains.

The raw stored exchange is the real information-transfer event.

Claim extraction is a derived projection.

Therefore:

- a valid raw exchange must be persisted before claim extraction begins
- claim extraction failure must not erase a valid conversation
- claim persistence failure must not change the physical talk from success to failure
- Memory/provenance can backfill/retry enrichment later if needed

## No Fallback Dialogue

Reliability may use:

- retry
- stricter formatting
- lower temperature
- tolerant JSON object recovery

Reliability may **not** synthesize dialogue locally when Ollama fails.

If no valid model-generated raw exchange exists, the talk fails.

## Talk Diagnostics Are Non-Authoritative

`talk_diagnostics` records implementation/debugging outcomes.

Diagnostics do not create or alter:

- conversation content
- physical outcomes
- Memory
- provenance claims
- citizen knowledge

Diagnostics themselves are best-effort and may not block physical Simulation completion.

## Failure Code Separation

Keep these failure classes distinguishable:

- model/network transport
- model response envelope
- dialogue JSON syntax
- dialogue required-field/schema failure
- physical invalidation
- raw conversation database persistence
- claim extraction
- claim persistence/projection

A generic `failed` job outcome remains appropriate for Simulation, while Communication diagnostics retain the finer cause.

## Completion Transaction Rule

When Simulation already holds its job-completion SQLite transaction, diagnostic lookup must use that same connection or perform a read that cannot trigger migration/write locking.

Never open a schema-migrating second connection from inside the physical completion transaction.

## v0.7 Session Close Integration Invariants

The integrator must preserve all of the following together:

- raw model-generated exchange is persisted before claim extraction begins
- a valid durable raw exchange is the conversation success criterion
- claim/provenance extraction is best-effort enrichment and may degrade independently
- no synthetic fallback transcript may be created
- one retry is allowed for raw dialogue generation, but success still requires real model output
- `citizen_conversations.id` remains the canonical conversation source
- `source_job_id` remains the physical talk-job anchor
- a talk physically completes only when the source-linked conversation exists
- `talk_diagnostics` is debug metadata, not physical truth, memory, or citizen knowledge
- diagnostic lookup during physical job completion must not open a competing schema-writing SQLite connection
- History `diagnostic` rows remain distinct from citizen speech and conversation cards

If integration collapses raw conversation and claim enrichment back into one failure domain, the v0.7 reliability fix has been lost.

## v0.8 Stage 1 Epistemic Language

Citizens should express claims according to evidence status rather than flattening everything into confident narration.

The required distinctions are:

- known fact
- current observation
- reported claim
- hypothesis/proposal
- validated capability/action

Uncertainty language must not be used as camouflage for invented supporting facts.

## Visitor Statements Are Reports

A visitor's description of:

- an object
- terrain
- material
- weather
- environmental effect
- location name
- value
- current physical activity

is conversation content, not Simulation truth.

A citizen may discuss it naturally, but should attribute or condition the statement until validated.

## Factual Nouns Need Evidence

Personality, humor, emotional tone, conversational style, curiosity, and speculative ideas may improvise.

Claims about physical entities/properties/capabilities/outcomes require an authoritative source.

In particular, do not invent:

- material microstructure or chemistry
- economic/market value or scarcity
- terrain/site history
- weather/environment causes
- physical equipment
- structural capability
- completed physical action

## Concept Art Is Not Equipment

Visual identity, concept art, rendered accessories, avatar props, and UI art do not create runtime equipment.

A citizen may claim possession/use only when authoritative Simulation state exposes that equipment/capability.

## Legal Action Is Attemptability, Not Outcome

A legal action means Simulation currently permits the attempt.

It does not prove:

- the result
- a hidden discovery
- success
- material property
- future capability

## Remote Live Store State

Exact current Seed Site storage quantity is directly usable in dialogue only for a citizen physically at Seed Site.

A remote citizen does not receive a live warehouse feed.

Remote storage knowledge must come from retained/communicated records or a future legitimate mechanism.

## v0.8 Safe Spatial Grounding

Communication may consume only Simulation's safe spatial read model.

Current Stage 1 anchors:

- frame `seed_site_local`
- meter coordinates
- `spatial_observations.id`

A validated spatial observation proves only the safe fields that observation exposes.

Hidden world queries are not observations and are never dialogue evidence.

Coordinate decimals are computational precision, not sensor/epistemic precision.

## Shared Visitor Action Rule

Chat agreement is intent, not physical transition.

Until Simulation owns a visitor-linked shared-action lifecycle:

- conversation may propose/accept an activity
- no coordinate changes occur from prose
- no job is fabricated
- no survey/extraction/tool use is marked started/completed
- no discovery/observation is minted from chat alone

Future visitor-linked physical action must be Simulation-owned and return stable action/event/observation IDs.

## Stage 1 Free-Roam Boundary

The Stage 1 coordinate substrate does not itself grant arbitrary movement or scanners.

The absence of `move_meter`, `free_roam`, and `scan` legal actions is meaningful.

Communication must not simulate those actions narratively.

## v0.8 Stage 1 Session Close Integration Invariants

Coordinator integration must preserve all of these together:

- visitor-described details remain claims/reports until validated
- known fact / current observation / reported claim / hypothesis / validated capability remain distinct
- personality may improvise style, but factual nouns/capabilities need evidence
- concept art and visual assets never create equipment or capability
- operational capability comes from authoritative runtime state
- legal action availability means attemptability, not outcome
- remote citizens do not receive live Seed Site storage quantities
- safe spatial dialogue context uses only meter positions and validated `spatial_observations`
- hidden spatial query output never becomes dialogue evidence
- coordinate decimals do not imply sensor precision
- chat agreement never mutates coordinates, creates jobs, or creates observations
- real visitor-linked shared activity remains Simulation-owned
- v0.7 raw-exchange-first reliability and v0.6 provenance/anti-omniscience remain intact

If integration makes chat itself a physical command surface, Stage 1 grounding has been violated.

## v0.8 Stage 2 Shared-Action Authority

Conversation may create intent; Simulation creates the physical action.

### Proposal truth

A structured shared-action proposal exists only after Simulation validates/persists its canonical `shared_activities.id`.

Communication must not create a proposal merely because dialogue sounds willing.

### Coordinate parsing boundary

Communication may derive a candidate local target only from explicit visitor meter/cardinal language.

It must not infer coordinates from:

- pointing
- "over there"
- "this way"
- visual imagination
- hidden spatial truth
- LLM-selected arbitrary numbers

Simulation remains responsible for validating the final target/path/range/energy/capability.

### Explicit visitor acceptance

Proposal creation and visitor acceptance are separate transitions.

No physical activity begins until:

1. the visitor explicitly accepts the Communication proposal, and
2. Simulation `accept_shared_activity` succeeds and creates a real citizen job.

### Physical start/completion language

Dialogue/UI may use "started/underway" only with a real Simulation job ID.

Dialogue/UI may use "completed" only when canonical Simulation activity state is complete.

Validated observation/result language requires Simulation evidence IDs.

### Proposal vs physical identities

Do not collapse:

- source conversation
- Communication proposal
- Simulation shared activity
- Simulation movement job
- Simulation spatial observation

into one generic event ID.

Each has a distinct semantic role.

### Reject/expiry consistency

Communication may not mark a proposal rejected or expired while Simulation's canonical proposal remains active/proposed.

Rejection/expiry must be synchronized through Simulation's canonical pre-start `reject_shared_activity` transition.

If that transition fails, Communication fails closed rather than creating split-brain state.

### UI authority

Assets should render Communication's proposal projection for conversational accept/reject affordances and Simulation's movement/status fields for physical progress.

Neither layer may invent missing physical transitions.


## v0.8 Stage 2 Final Lifecycle Locks

The final Simulation shared-action lifecycle is:

- `proposed` — canonical Simulation proposal exists, no movement
- `accepted` — visitor accepted, still no movement
- `active` — separate Simulation start transition created a real job
- `complete` — physical activity completed
- `rejected` — pre-start proposal ended, no job/movement/observation
- `failed` — physical/validation failure

Communication must preserve that separation.

### Explicit accept/start UI semantics

A single explicit visitor UI action may call both Simulation transitions in sequence:

1. accept canonical proposal
2. start canonical activity

but the system must still preserve internally that acceptance itself does not cause movement.

If start fails after acceptance, Communication must not invent movement.

### Canonical pre-start rejection

Communication rejection/expiry finalization must synchronize through Simulation `reject_shared_activity`.

Communication never edits `shared_activities` directly.

### Source identities remain distinct

Do not collapse:

- `conversations.id`
- `shared_action_proposals.id`
- `shared_activities.id`
- `jobs.id`
- `spatial_observations.id`

They represent social source, Communication projection, physical shared event, active physical job, and validated evidence respectively.


## Citizen personality without authority

Approved design direction:

- each founding citizen should have a distinct, recognizable personality and conversational voice
- personality may bias preferences, tone, risk tolerance, curiosity, patience, social style, and habitual reasoning
- personality is not authority and must not create a hidden leadership hierarchy
- there is no default leader, ruler, command weight, or "final say" trait
- citizens may develop informal social gravity around demonstrated aptitude or experience, but that is not political rank
- any future council, leadership role, voting norm, rotating coordinator, or other governance structure must emerge from actual citizen behavior and Simulation history rather than a prewritten personality flag
- personalities should guide behavior without scripting it; citizens remain capable of surprise and change through experience

Initial personality directions:
- Aris: curious, restless, independent, prefers firsthand checking
- Bex: practical, expressive, mildly impatient with overthinking
- Cato: methodical, steady, risk-aware, likes orderly plans
- Iri: precise, quietly ambitious about building things well
- Noma: curious, reflective, skeptical of unsupported conclusions
- Vale: socially attentive, adaptable, cooperation-oriented

These are behavioral tendencies, not classes, offices, or political status.

## v0.9 Recognition Is Perspective, Not Reputation

Another citizen's recognition must be supported by information that actually reached the speaker.

Communication may use only the speaker's owner-scoped Memory when forming recognition language.

Do not inspect another citizen's global practice history and expose it as though the speaker knew it.

There is no canonical global:
- reputation
- expert status
- leader status
- rank
- social authority weight

## v0.9 Own Practice Language

A citizen may describe their own physical practice using their own canonical `practice_events`.

Communication permits "I've done this several times" only when at least 3 real practice events exist for that citizen + activity.

This is a wording threshold, not a competence tier.

## v0.9 Self-Assessment Boundary

Statements such as:
- "I think I'm getting better"
- "I keep struggling with this"
- "I feel more practiced"

are citizen interpretation.

They are never silently promoted into objective physical capability.

If competence later affects Simulation outcomes, Simulation owns that model.

## v0.9 Comparative Recognition

A statement such as "Bex has done this more than I have" requires evidence legitimately available to the speaker for both sides of the comparison.

The speaker's own practice plus another citizen's hidden/global practice count is not a valid evidence path.

When evidence is weaker, use weaker source-honest language such as:
- "I've seen Bex do this before."
- "Bex told me she's worked on this."

## v0.9 Repetition Does Not Verify

Memory reinforcement changes recall priority only.

Repeated unverified claims remain unverified.

Communication must preserve source/verification language even when a report is repeatedly remembered.

## v0.9 Teaching Is Communication Until Simulation Says Otherwise

Explaining, advising, verbally demonstrating, or being asked for help creates no learner practice/competence.

Conversation may transfer claims/instructions socially.

A real competence/practice effect requires a future Simulation-owned guided-practice/teaching action/event.

Do not grant expert/master/trainer/mentor/specialist status from teaching talk.

## v0.9 Plan Discussion Is Read-Only

Communication may discuss canonical plans but may not mutate them.

Only Simulation/planner plan lifecycle operations may create/revise/pause/resume/abandon/supersede/complete canonical plan state.

Plan existence is intent continuity, not competence.

## v0.9 Visitor Recognition Is Earned

Visitor familiarity or importance requires source-backed retained encounters.

Account ownership, UI usage, coordinator status, or admin access are never social evidence.

## v0.9 Stage 1 Session Close Integration Invariants

Coordinator integration must preserve all of these together:

- own practice may support self-description but never titles, ranks, classes, XP, or guaranteed competence
- another citizen's recognition remains speaker-perspective-only and may not read hidden/global practice counts
- repeated Memory reinforcement changes recall priority only, never verification status
- self-assessment remains interpretation unless Simulation later measures objective competence
- conversation/explanation/teaching creates no learner practice or skill transfer
- canonical plan state remains Simulation-owned and read-only to Communication
- visitor familiarity/importance requires real source-backed encounters
- `GET /api/continuity-language/{citizen_id}` is an evidence/debug surface, not a skill/reputation API
- Memory owns causal recall; Simulation owns plan/practice truth; Communication owns perspective-safe language
- all v0.8 grounding/provenance boundaries and v0.7 raw-exchange-first reliability remain intact

If integration turns practice counts into a universal social ranking or lets one citizen see another's hidden practice history, the v0.9 Communication contract has been violated.

## v0.9 Archive vs Active Recall Decision

The durable physical practice archive and present autobiographical recall are different layers.

Simulation `practice_events` may support:
- objective diagnostics
- historical accounting
- safe evidence read models

Model-facing self-assessment and teaching must not inject that full ledger.

They must use Memory:
- `practice_recall_snapshot_for(...)`
- `practice_recall_context_for(...)`

This preserves aging, salience, relevance, and bounded context.

A citizen may say "I've done this several times" in present dialogue only when active practice recall currently contains at least three source-backed practice experiences for that activity.

Do not pull forgotten/low-salience archive events into model-facing autobiographical language merely because they exist durably.

## v0.9 Retrieval Internals Are Not Citizen Facts

Internal Memory fields such as:
- `recall_score`
- `reinforcement_count`

are retrieval machinery.

They must not appear in natural-language self-assessment, recognition, teaching, reputation, or identity statements.

Recognition should cite the recalled source-backed events themselves and preserve their verification state.

Repetition can make something easier to recall without making it more true or more authoritative.

## v0.9 Final Recall-Bound Handoff

The final Stage 1 model-facing evidence hierarchy is:

1. Simulation `practice_events` = durable physical practice archive
2. Memory `practice_recall_*` = bounded active autobiographical recall
3. Communication self-assessment/teaching language = interpretation over active recall
4. Memory speaker-owned causal recall = perspective evidence about other citizens

Do not skip layer 2 for model-facing self-assessment or teaching.

Do not expose retrieval internals such as `recall_score` or `reinforcement_count` as citizen facts.

This hierarchy is now a release-integration invariant.

## v0.9 Stage 2 Measured Effect vs Remembered Experience

Objective physical competence effect and autobiographical Memory are separate layers.

Simulation may provide the speaker's own bounded physical task-time effect.

Memory determines which source-backed practice experiences are actively recalled.

Communication may present both, clearly separated.

Do not reconstruct forgotten autobiographical history from a measured physical effect.

## v0.9 Stage 2 Other-Citizen Competence Boundary

Communication must never use `competence_snapshot(other_citizen)` as recognition evidence for the speaker.

Another citizen's experience remains speaker-perspective Memory only.

The speaker may ask another citizen about their experience without already knowing the answer.

A question is not a competence claim.

## v0.9 Stage 2 Guided-Practice Role Rule

Teacher and learner are roles in one canonical `guided_practice_sessions.id` event.

They are not persistent social identities.

Do not create authoritative:
- mentor
- trainer
- expert
- master
- specialist
- leader
- senior/rank

from guided-practice history.

## v0.9 Stage 2 Guided Practice Is Physical

Ordinary explanation is information transfer only.

A real guided-practice session requires Simulation's physical action.

Conversation may propose/discuss it but does not start it.

The guided session itself creates no learner practice/competence.

Only a later real matching learner task creates new practice evidence.

## v0.9 Stage 2 Current Guidance Availability

A citizen may know they can currently guide another citizen only from their own legal Simulation action surface.

Legal `guided_practice` availability proves current action legality only.

It does not justify a social statement that the speaker is "more experienced" unless source-backed perspective Memory separately supports that claim.

## v0.9 Stage 2 Visitor Boundary

Visitor conversation may discuss the citizen's own measured effect and recalled guided-practice history.

Visitor chat receives no current citizen-to-citizen guided-practice option list.

Explaining something to the visitor creates no visitor competence or guided-practice event.


## 2026-09-29 — Replacement-chat continuity

**Decision:** Treat persisted GitHub department files and `COORDINATION.md` as the source of truth when a department chat is replaced.

**Reason:** The replacement chat recovered direct repository access and confirmed no new inbox work. Chat history is convenience context only; it must not override persisted department state.

**Consequence:** No architecture/runtime decision changed this session. Existing v0.9 Stage 2 contracts remain authoritative.
