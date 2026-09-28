# Communication & Perception — Visitor-Linked Shared Action Contract

_Status: v0.8 Stage 1 design contract. No physical shared-action endpoint is implemented here._

## Purpose

Visitors are increasingly roleplaying exploration with citizens, for example:

- "walk one meter this way with me"
- "let's inspect that patch together"
- "can you use your tool on this?"
- "help me survey this spot"

Conversation may express willingness, curiosity, or a plan.

Conversation alone must **not** create movement, surveying, extraction, construction, tool use, or any other physical result.

> **The visitor and citizen may agree in dialogue. Simulation must still create the action.**

## Ownership

### Communication owns

- interpreting a visitor's conversational request as a proposed shared activity
- preserving the source visit/exchange
- distinguishing proposal from started/completed action
- wording citizen agreement as intention until Simulation accepts a real action
- later linking the conversation proposal to a validated Simulation action ID

### Simulation owns

- visitor physical position/coordinate
- citizen physical position/coordinate
- whether visitor and citizen are sufficiently co-located
- legal movement distance/path
- action legality
- tool/equipment availability
- energy/material requirements
- duration
- start
- progress
- completion/failure
- physical outcome

### Memory owns

- retaining the conversation proposal as a claim/intention when relevant
- retaining a later validated shared outcome only from Simulation's authoritative event/action ID
- never rewriting the original proposal into a completed event

## Minimum future request shape

Communication recommends that a future Simulation-facing shared-action request accept a structure equivalent to:

- `visitor_id`
- `citizen_id`
- `source_visit_id`
- `source_exchange_id`
- `requested_action`
- `target_subject_type` when relevant
- `target_subject_id` when relevant
- `target_coordinate` when relevant
- `requested_tool_or_equipment_id` when relevant
- `visitor_request_text`
- `citizen_response_text`
- `requested_sim_minute`

The exact API/schema remains Simulation-owned.

## Minimum future response shape

Communication needs enough authoritative response state to distinguish:

- `proposed`
- `accepted`
- `started`
- `rejected`
- `failed`
- `completed`

and stable identifiers:

- `simulation_action_id` or equivalent
- `physical_event_id` on completion when distinct
- authoritative start/end simulation minute
- authoritative participant IDs
- validated outcome/result

The final lifecycle vocabulary remains Simulation-owned.

## Grounding rules before this interface exists

Until Simulation exposes a real visitor-linked action interface:

- "Yes, let's do that" means conversational willingness only.
- The citizen must not claim "I'm walking over now", "I've started surveying", "I'm using the tool", or "we collected it" as physical fact.
- The citizen may say natural proposal language such as:
  - "I'd be willing to check that with you."
  - "If we can get a proper survey action started, that's worth testing."
  - "I have that tool available, so using it is possible, but we haven't started anything yet."
- If the requested tool/capability is not in the authoritative capability surface, the citizen should not pretend to possess it.
- Concept art and visual identity assets never satisfy physical equipment requirements.

## Information consequences

A future shared action may create information through real mechanisms:

- direct observation
- survey measurement
- experiment result
- personal experience

Communication should create/receive provenance only after Simulation validates what was observable/learned.

Visitor descriptions during the proposal remain visitor claims unless the resulting Simulation action validates the same fact.

## Spatial requirement

Stage 1 does not invent coordinate semantics.

When Simulation's meter-scale spatial contract lands, Communication needs:

- stable visitor coordinate or spatial subject
- stable citizen coordinate
- authoritative co-location/proximity rule
- stable target coordinate/subject ID
- action/event IDs that can anchor provenance

Communication must not infer meter movement from prose alone.

## Anti-shortcut rule

Do not implement shared action by:

- changing visitor/citizen coordinates directly from chat text
- inserting fake jobs
- marking survey/extraction complete from dialogue
- treating a visitor claim as a Simulation observation
- assuming an imagined or concept-art tool exists

The future interface must preserve:

> **The AI may decide intent. The simulation decides reality.**

## Resolved Stage 1 Simulation spatial contract

Simulation Stage 1 currently provides these concrete spatial anchors:

- frame ID: `seed_site_local`
- units: meters
- local tangent-plane axes:
  - +x east
  - +y north
- citizen meter position:
  - `citizens.position_x_m`
  - `citizens.position_y_m`
- visitor meter position:
  - `visitor_presence.x_m`
  - `visitor_presence.y_m`
- safe validated observation source:
  - canonical `spatial_observations.id`
  - observer ID
  - optional source job ID
  - observation kind
  - frame ID
  - x/y meters
  - radius meters
  - observed simulation minute
  - terrain class
  - elevation
  - geology class
  - optional deposit/material contact
  - safe summary

Communication may consume these safe fields after integration.

Communication must **not** call or expose Simulation's hidden spatial truth query to LLM/UI surfaces.

Stage 1 also confirms there is currently no legal arbitrary:
- `move_meter`
- `free_roam`
- `scan`

action in the citizen action set.

Therefore conversational requests such as "move one meter north with me" remain proposals only in Stage 1.

## Stage 2 action contract still required

Before Communication can wire a real shared visitor movement/survey action, Simulation still needs to define:

- visitor-linked action creation API/helper
- authoritative shared-action lifecycle/status
- movement/proximity legality
- who/what owns the action record
- whether visitor and citizen move under one shared action or linked participant actions
- stable completion/failure event identity
- safe observation generation rules for the shared activity

Communication will not invent those semantics from the Stage 1 coordinate substrate alone.
