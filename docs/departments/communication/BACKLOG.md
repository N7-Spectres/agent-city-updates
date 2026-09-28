# Communication & Perception — Backlog

## v0.8 Stage 2 — Immediate Integration Blocker

Communication proposal/start/status work is complete on:

`communication/v0.8-shared-actions-stage2`

Remaining dependency:

### Simulation canonical proposal cancellation

Need:

`cancel_shared_activity(conn, activity_id, visitor, *, now, reason)`

Required semantics:

- only terminalize unstarted canonical `shared_activities.status='proposed'`
- validate the proposed visitor
- never cancel an already active/completed physical job through this proposal-cancel path
- preserve participant/source/target fields
- persist terminal `cancelled` or equivalent status
- create no movement or observation
- return success/message

Communication already fails closed if this function is unavailable.

Once supplied:

- explicit visitor reject can synchronize both layers
- visitor leave/travel can expire pending proposals without leaving stale Simulation proposals
- Assets can safely enable reject/decline UI

## Stage 2 Coordinator Merge Requirements

Preserve both department implementations in `main.py`:

### Simulation physical endpoints/state
- canonical `shared_activities`
- continuous movement payloads
- physical propose/accept/status API/helpers
- jobs and observation completion

### Communication conversational endpoints/context
- `shared_action_proposals`
- `/api/shared-actions/...`
- proposal creation from durable visitor exchange
- explicit accept/reject UI layer
- bounded shared activity dialogue context

Do not replace Communication proposal semantics with direct UI calls to Simulation's proposal endpoint, or the durable conversational source/explicit RP bridge is lost.

## Stage 2 Source Chain

Keep distinct:

1. `conversations.id` — social source exchange
2. `shared_action_proposals.id` — Communication proposal projection
3. `shared_activities.id` — Simulation canonical shared activity
4. `jobs.id` — active physical job
5. `spatial_observations.id` — validated exploration evidence

## Future Shared-Action Depth

After Stage 2 integration:

- additional Simulation-owned shared activity types may be exposed through explicit safe contracts
- tool-assisted inspection may use actual available equipment IDs
- proposal parser may expand beyond cardinal meter requests only when Simulation defines safe target semantics
- cancellation after physical start should be a separate Simulation movement/job cancel design, not proposal rejection
- proposal provenance may later be surfaced in History/Memory if useful

## Existing Deferred Communication Depth

- structured visitor-claim provenance beyond current raw visitor exchange
- claim contradiction/reliability reconciliation
- third-party overhearing
- physical records / notice boards
- emergent place-name propagation
- invented long-distance communication after actual research/material/fabrication prerequisites

## Ongoing Safety Audits

- no hidden world query in prompts
- no concept-art capability
- no remote live-state leakage
- no LLM-invented coordinates
- no proposal-as-completion
- preserve v0.7 raw-exchange-first conversation reliability
