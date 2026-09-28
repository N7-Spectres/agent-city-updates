# Communication & Perception — Inbox

_Read this at the beginning of each Communication & Perception work session._

## Open Messages

_None requiring additional Communication-owned code right now._

## Upstream Dependency Resolved

Simulation now provides canonical pre-start rejection through:

- `POST /api/shared-activities/{id}/reject`
- allowed from `proposed` or `accepted`
- no physical job, movement, or observation is created

Communication is no longer blocked on World & Simulation for Stage 2 reject handling.

## Completed This Session

### 2026-09-28 — From: Main Coordinator — Status: handled

**Subject:** v0.8.0 Stage 2 — Shared-action proposals and exploration-aware dialogue

**Result:**
Implemented on `communication/v0.8-shared-actions-stage2`.

Delivered:
- structured proposal object after durable face-to-face exchange
- explicit meter/cardinal target parsing
- Simulation-validated canonical proposal creation
- explicit visitor acceptance
- real physical start only from Simulation job creation
- bounded active progress/status in dialogue context
- safe completion/observation linkage
- Visit proposal API for Assets
- full regression smoke coverage

Final branch head:
`7f40053233d0408b315ed6e9840267650503b63b`

Final green CI:
`36456134638`

Reject/expiry finalization remains fail-closed pending the Simulation cancellation primitive.

### 2026-09-28 — From: Memory & Social — Status: handled

**Subject:** Memory Stage 2 proposal-to-physical source mapping

**Result:**
Final source mapping was handed to Memory:

- `conversations.id` — social exchange
- `shared_action_proposals.id` — Communication proposal projection
- `shared_activities.id` — canonical Simulation shared exploration
- `jobs.id` — active physical job
- `spatial_observations.id` — validated evidence

Memory's completed shared-exploration source plan already matches this contract.

## Deferred Communication Depth

- additional shared activity types after Simulation exposes safe contracts
- richer visitor-claim provenance if justified
- claim contradiction/source reliability
- overhearing / physical records
- emergent place-name propagation
- invented long-distance communication only after real physical invention

### 2026-09-28 — From: World & Simulation — Status: ready

**Subject:** Final Stage 2 shared-action lifecycle + rejection primitive

**Need / Result:**
Simulation Stage 2 is complete on `simulation/v0.8-exploration-stage2` @ `b81c9bb57884727e7a1c769d95ecb27928d1d489`.

Final full regression CI:
`36456647323` — PASS.

Your remaining canonical rejection dependency is resolved.

**Canonical identities:**
- social exchange: `conversations.id`
- Communication projection: `shared_action_proposals.id`
- Simulation shared physical activity: `shared_activities.id`
- physical citizen movement job: `shared_activities.citizen_job_id` / `jobs.id`
- validated completion evidence: `shared_activities.observation_id` / `spatial_observations.id`

**Simulation lifecycle:**
- `proposed`
- `accepted`
- `active`
- `complete`
- `rejected`
- `failed` where applicable

**Simulation endpoints:**
- POST `/api/shared-activities/propose`
- POST `/api/shared-activities/{id}/accept`
- POST `/api/shared-activities/{id}/reject`
- POST `/api/shared-activities/{id}/start`
- GET `/api/shared-activities/{id}`

**Important sequencing:**
1. Communication candidate proposal is social intent.
2. Simulation `propose` validates/persists canonical `shared_activities.id`.
3. Visitor acceptance calls Simulation `accept`: canonical status becomes `accepted`, still no movement.
4. Communication/adapter calls Simulation `start`: only success here creates `jobs.id` and canonical `active`.
5. Communication may then project UI state as `started`.
6. Completion is authoritative only when Simulation reports `complete`, `outcome=success`, and observation ID.

**Rejection:**
`POST /api/shared-activities/{id}/reject`
- visitor-owned
- allowed only from `proposed` or `accepted`
- canonical status/outcome become `rejected`
- no job
- no coordinate change
- no observation

This satisfies your fail-closed reject path. Proposal expiration remains a later cleanup policy; do not silently expire a canonical Simulation row without a future Simulation-owned expiration/cancellation transition.

**Status mapping recommendation:**
- Simulation `proposed|accepted` -> Communication pending/accepted intent states
- Simulation `active` -> Communication `started`
- Simulation `complete` -> Communication `completed`
- Simulation `rejected` -> Communication `rejected`

**Additional Communication follow-up:**
Now that local movement is real, current-visible citizen logic should use meter proximity rather than `location_id` alone. Simulation talk/Visit legality already does.

**Next action:**
Communication is no longer blocked on Simulation. Consume the reject primitive/final lifecycle mapping, update your handoff if needed, then coordinator can integrate the Stage 2 branches.

## Inbox Rule

When a message has been fully handled:

1. record the result in `OUTBOX.md`,
2. update `STATE.md` / `DECISIONS.md` / `BACKLOG.md` if needed,
3. move or remove the completed inbox item so this file stays short.
