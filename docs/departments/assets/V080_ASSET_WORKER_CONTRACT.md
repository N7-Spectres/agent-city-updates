# Agent City v0.8 — Local Asset Worker Contract

_Status: Stage 1 architecture_
_Owner: Assets & Interface_
_Last updated: 2026-09-28_

## Purpose

Define the local asynchronous visual-generation layer for Agent City without making rendering authoritative over physical reality.

Core rule:

> **Simulation defines the object. Assets renders the object.**

The asset pipeline exists to turn already-valid physical state into reusable visual representations.

It must never:
- create equipment
- create resources
- change quantity
- change condition
- invent capability
- block a physical action from completing
- reveal hidden Simulation truth

Stage 1 defines the persistent job/spec format and worker contract. It does **not** require Blender, 3D generation, or an AI mesh generator yet.

---

## Authority Boundary

### Simulation owns

- physical object identity
- project identity
- quantity
- materials/components
- condition
- location / coordinates
- dimensions when physically defined
- capability
- lifecycle / construction outcome
- ownership / attachment semantics when implemented

### Assets owns

- visual specification derived from safe authoritative state
- render tier
- procedural representation
- local generation job state
- output files
- caches / thumbnails
- fallback visuals
- runtime presentation

### Asset Worker owns

Only the asynchronous transformation:

`validated visual spec → generated visual artifact`

The worker has no authority to mutate Simulation state.

---

## Persistent Identity

Every generated asset must trace back to a stable authoritative subject.

Required source identity:

- `source_type`
- `source_id`

Examples:

- `project:42`
- `structure:8`
- `equipment:17`
- `citizen:aris`
- `resource_stack:seed_site:Plant Fiber`

Prefer real Simulation IDs whenever a unique physical object exists.

Bulk fungible resources are the exception: rendering may use a stable presentation key derived from authoritative storage/location/material identity rather than pretending each unit is a unique object.

---

## Visual Specification

Recommended persisted shape:

```json
{
  "spec_version": 1,
  "source_type": "equipment",
  "source_id": "17",
  "source_revision": "physical-state-hash-or-version",
  "render_tier": "individual",
  "visual_kind": "equipment",
  "generator": "procedural_v1",
  "geometry": {
    "family": "cargo_pack",
    "dimensions_m": [0.55, 0.24, 0.70]
  },
  "materials": [
    {
      "role": "shell",
      "material_key": "processed_structural_material"
    }
  ],
  "presentation": {
    "accent_hint": null,
    "attachment_slot": "back"
  }
}
```

Important:

- the spec contains only safe validated input
- optional presentation hints cannot create capability
- `source_revision` lets Assets know when a physical object changed enough to require regeneration
- hidden world properties never enter the spec merely because they exist in Simulation

---

## Proposed Persistent Tables

Stage 1 architecture may use equivalent storage, but the conceptual contract is:

### `asset_specs`

- `id`
- `source_type`
- `source_id`
- `source_revision`
- `spec_version`
- `render_tier`
- `visual_kind`
- `generator_key`
- `spec_json`
- `created_at`
- `superseded_at`

Unique logical identity:

`source_type + source_id + source_revision + spec_version`

### `asset_jobs`

- `id`
- `asset_spec_id`
- `status`
- `priority`
- `attempt_count`
- `worker_id`
- `claimed_at`
- `created_at`
- `updated_at`
- `completed_at`
- `error_code`
- `error_text`
- `output_path`
- `output_format`
- `content_hash`
- `generator_version`

Status lifecycle:

`queued → working → ready`

Failure path:

`queued → working → failed`

A failed job may later be retried as a new attempt.

Do not overload physical project/job statuses with asset-generation statuses.

---

## Worker Claiming

The local Asset Worker should:

1. poll or receive a local wake signal
2. atomically claim one `queued` job
3. mark it `working`
4. read the immutable referenced spec
5. generate output into a staging path
6. validate the output
7. atomically move output into the generated-assets store
8. record content hash / generator version
9. mark the job `ready`

If generation fails:

- mark only the asset job failed
- retain error metadata
- keep the physical object valid
- continue using fallback presentation

---

## No Simulation Blocking

Critical rule:

> **Physical completion never waits for visual completion.**

Example:

1. Iri finishes constructing a shelter.
2. Simulation creates the real structure.
3. UI immediately shows a safe fallback shelter marker/primitive.
4. Assets queues a richer visual job.
5. The Asset Worker generates a GLB later.
6. UI swaps the fallback for the richer representation when the asset is ready.

If the worker is offline for three days, the shelter still exists.

---

## Output Store

Suggested local layout:

```text
generated_assets/
  equipment/
    17/
      r3/
        object.glb
        thumbnail.webp
        manifest.json
  structures/
    8/
      r1/
        object.glb
        thumbnail.webp
        manifest.json
```

The final path format is implementation detail, but outputs should be:

- local-first
- content-hashable
- reusable
- replaceable by newer revisions
- safe to delete/rebuild from specs when appropriate

Generated outputs are presentation cache, not physical truth.

---

## Render Tiers

### Tier 1 — Individual object

Use when identity matters.

Examples:

- fabricated tool
- cargo pack
- battery pack
- machine
- unique part
- constructed structure
- actively handled object

Rules:

- preserve stable object identity
- asset may follow object ownership/location
- wear/damage visuals only when authoritative state exposes a safe representation contract

### Tier 2 — Representative bundle / pile / stack

Use for fungible bulk resources.

Examples:

- logs
- stone
- plant fiber
- ingots
- resin containers

Core rule:

> **Do not render one mesh per simulation unit.**

One pile may visually represent many real units.

Possible visual bands:

- trace
- small
- medium
- large
- full

The renderer may derive a display band from authoritative quantity, but it must never change the quantity.

### Tier 3 — Storage abstraction

Use after bulk material is deposited.

Examples:

- warehouse
- storage unit
- bins
- tanks
- material racks

Deposited inventory normally does not remain as hundreds of loose world objects.

Storage may communicate:

- category presence
- fullness band
- active staging

Exact inventory remains Simulation-owned.

---

## Aggregation Example

Physical truth:

- settlement owns 80 logs

Visual truth:

- storage structure shows a large wood-stock representation

Not allowed:

- spawn 80 independent log meshes merely because quantity = 80

Withdrawal:

- citizen stages 2 logs
- Assets may show a small representative carried/staged bundle
- Simulation remains authoritative for the exact 2-unit transfer

---

## Fallback Contract

Every renderable subject needs an immediate fallback.

Examples:

- structure → primitive footprint/block + icon
- equipment → generic silhouette + name/kind
- resource pile → generic material bundle
- citizen → approved 2D identity token
- unknown richer asset → existing v0.7 presentation

Fallback must:

- be lightweight
- never imply unavailable capability
- never invent material detail
- remain usable indefinitely if generation fails

The rich asset is enhancement, not correctness.

---

## Generator Stages

### Stage 1

No Blender requirement.

Support:

- specs
- queue
- deterministic placeholders/procedural recipes
- thumbnails if convenient
- provenance
- fallback lifecycle

### Later procedural generator

May use:

- primitive composition
- modular part library
- deterministic geometry recipes
- material library
- Blender headless
- another local mesh pipeline

### Future model-assisted generator

A local model may help translate validated functional design into a constrained visual recipe.

The model may not invent:

- capabilities
- components
- materials
- dimensions
- ownership
- physical success

Model output is proposed visual form constrained by the spec.

---

## Asset Provenance

Each ready artifact should retain:

- authoritative `source_type`
- authoritative `source_id`
- `source_revision`
- `spec_version`
- generator key/version
- content hash
- output format
- completion timestamp

This lets the city answer:

> “What physical object does this visual represent, and which physical revision was it generated from?”

---

## Superseding Assets

When physical state changes enough to invalidate appearance:

1. derive a new source revision
2. persist a new spec
3. queue a new job
4. continue showing the old safe asset or fallback if appropriate
5. swap when the new asset becomes ready
6. mark older spec/artifact superseded

Never silently rewrite provenance.

---

## Citizen Visual Assets

Citizen base identity is a slightly different case because the six founding citizens have approved presentation canon.

See:

`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

Citizen system rules:

- base body remains stable identity
- visor expression is presentation
- physical gear is separate
- future gear overlays require authoritative possession/attachment semantics
- 2D remains a valid fallback even after 3D exists

---

## Equipment Attachment Dependency

Before full citizen equipment layering becomes authoritative, Simulation may need to expose:

- equipment object ID
- current owner
- current location
- equipped/attached boolean or state
- attachment slot when physically meaningful

Potential slots:

- back
- chest
- waist
- left_hand
- right_hand
- left_arm
- right_arm

Assets must not guess attachment solely from item kind.

---

## Worker Availability

The app should expose Asset Worker health separately from Simulation health.

Possible states:

- offline
- idle
- working
- degraded
- queue_backlog

A worker outage is a visual-service issue, not a civilization outage.

---

## Scheduling / Priority

Suggested priority order:

1. selected / currently visible unique object
2. newly completed structure/equipment
3. nearby world object
4. thumbnails / alternate LOD
5. background regeneration

The queue may deprioritize invisible work without affecting physical state.

---

## Security / Robustness

The worker should:

- write only inside approved asset directories
- reject path traversal
- never execute arbitrary prompt-generated shell commands
- validate output format
- cap attempts / backoff retries
- keep generator errors out of Simulation state
- avoid remote network dependency by default

---

## Continuous-World Dependency

Stage 1 must not invent v0.8 continuous coordinates.

Until Simulation hands off the seeded spatial read model:

- preserve current map truth
- define rendering interfaces only
- do not fabricate world positions for richer assets

Once Simulation provides stable coordinates, asset placement can consume them directly.

---

## Stage 1 Deliverables

Assets Stage 1 should leave the project with:

- this worker contract
- citizen visual-system spec
- render-tier rules
- persistent identity/provenance design
- fallback behavior
- queue lifecycle
- no mandatory Blender dependency
- no full 3D generation requirement
- no Simulation blocking

---

## Core Principles

> **Simulation defines the object. Assets renders the object.**

> **Rendering may aggregate. It may not alter quantity.**

> **A missing rich asset is a presentation fallback, never a missing physical object.**
