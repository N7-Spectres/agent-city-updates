# Cato — Pre-Blender World Body Pilot

_Last updated: 2026-09-30_

## Purpose

Cato is the first Agent City citizen to graduate from a circular Local-map token to a body-shaped world presentation before a true 3D mesh exists.

This is intentionally a **2.5D pre-Blender body pilot**, not a claim that a real mesh/rig already exists.

Core authority remains:

> **Simulation defines reality. Assets renders reality.**

## Current Runtime Representation

Local 3D uses:

`static/assets/citizens/cato/world/front.webp`

The body sprite is:
- transparent-background
- equipment-free
- visually derived from the approved chunky yellow Cato concept
- anchored at Cato's authoritative Local world position
- scaled by camera depth
- carried by the existing authoritative route-travel renderer
- selected through the existing citizen selection/Visit flow

Aris is separately promoted in v0.9.14 and Iri in v0.9.18. Bex, Noma, and Vale remain token-based until their own approved rollout.

## Physical / Presentation Boundary

Authoritative:
- citizen identity
- Simulation `position_x_m / position_y_m`
- real travel job origin/destination
- travel start/end timing
- energy / integrity / current activity
- equipped or carried real state when separately exposed

Presentation-only:
- body sprite dimensions in screen space
- the tiny world-space fan-out used when citizens share one physical point
- ground shadow
- selection glow
- subtle travel bob while a real travel job exists

The body sprite never writes coordinates, creates travel, or grants Cato equipment/capability.

## Equipment Separation

The runtime body creates an empty `.world-equipment-layer`.

That layer is intentionally empty in v0.9.12.

The concept sheet's:
- cargo harness
- lift hook
- cargo crate

are **design references only** until Simulation says Cato actually has/equips/carries corresponding real objects.

No concept-art prop becomes inventory by being drawn.

## Blender Handoff

Future model slot reserved by presentation metadata:

`static/assets/citizens/cato/world/model.glb`

A future GLB should preserve:
- chunky/broad/heavy logistics silhouette
- cream/off-white + yellow + dark mechanical material language
- glossy dark visor with cyan eye display
- equipment-free base body
- separate optional gear attachment points

A true model may replace the sprite presentation while continuing to consume the same:
- Local world coordinates
- travel-job interpolation
- selection
- camera focus
- time/day presentation
- equipment-state contract

The renderer must not infer physical facing, gear, cargo, or capability from the mesh.

## v0.9.13 Grounding Polish

The first post-pilot polish pass keeps the same authoritative world position and sprite-body contract while improving presentation:

- body screen box widened slightly for Cato's approved heavy silhouette
- ground anchor moved closer to the sprite's foot line
- neutral ground-contact ellipse added beneath the body
- selected / hover states emphasize the ground contact as well as the body
- route-travel bob reduced to read as a heavy body rather than a floating token
- route-travel shadow compresses in sync with the presentation bob
- reduced-motion disables both travel animations

These are presentation measurements only. They do not define Cato's physical height, width, mass, collision body, or locomotion model.

## Next Pre-Blender Opportunities

Before Blender is required, Assets can still add:
- additional approved directional body sprites
- idle/travel presentation poses
- separate validated equipment overlays
- body-scale/camera tuning
- body-shaped selection/focus affordances
- richer ground contact/shadow
- similar body pilots for the remaining citizens

Do not synthesize extra body states into runtime canon without an approved source.
