# Iri — Pre-Blender Local World Body

_Last updated: 2026-09-30_

## Purpose

Iri is the third Agent City citizen promoted from a circular Local-map token to a body-shaped world presentation, after Cato and Aris.

This remains a **2.5D pre-Blender presentation**, not a physical mesh, rig, collision body, or locomotion model.

Core authority remains:

> **Simulation defines reality. Assets renders reality.**

## Visual Canon

Iri's approved visual identity is:

- researcher / analyst / citizen
- slender, precise silhouette
- pearl / cream-white shell
- charcoal mechanical joints
- lilac / purple secondary accents
- cyan visor / display language
- sensor-halo / analytical head silhouette
- relative presentation-height cue of approximately **1.78 m**

The 1.78 m cue is visual canon for relative character identity. It does not create a Simulation physics dimension unless Simulation later defines one.

The sensor-halo motif is a visual identity cue only. It does not imply sensing range, scanning capability, communications capability, or any other authoritative function.

## Current Runtime Representation

Local 3D uses the existing Iri body source:

`static/assets/citizens/iri/full.webp`

The source artwork contains a connected dark presentation backdrop. The Local renderer removes only the backdrop connected to the image border at presentation time, producing a transparent body silhouette without rewriting or inventing body pixels.

This cleanup is presentation-only. If the cleanup cannot run, the original asset remains the fallback source rather than creating new state.

The body presentation:
- is anchored to Iri's authoritative Local world position
- uses the same real route-travel interpolation pipeline as Cato and Aris
- scales with camera depth
- keeps a minimum Local zoom-out readability floor
- inherits the shared full-body stacking protection
- remains selectable through the existing citizen / Visit flow

## Relative Presentation Scale

Cato remains the visual reference at 2.1 m / scale 1.0.

Iri uses:
- presentation scale: `0.848`
- minimum Local readable scale: `0.50`

This keeps Iri visually shorter than Aris and Cato, while preserving her narrow analytical silhouette at the widest Local zoom.

These are renderer values only. They do not define physical height, reach, mass, speed, collision, carrying ability, or any other capability.

## Local-Only Boundary

Full citizen bodies are a Local world presentation.

Region / Planet continue to omit citizen body markers. No Iri body is promoted to global spatial truth.

## Equipment Separation

Iri's concept language may show:
- data slate
- research pack
- sensor drone
- analysis tools
- sample / research equipment

Those remain design references unless real equipped state exists.

No concept-art prop or visual motif becomes inventory, equipment, skill, or capability merely because it is depicted.

## Selection / Motion

Allowed presentation:
- lilac / cyan ground-contact affordance
- body-shaped hover / selection glow
- subtle travel-only bob when a real travel job exists
- synchronized ground shadow
- reduced-motion static fallback

The renderer never creates travel or writes coordinates.

## Future Model Slot

Reserved presentation path:

`static/assets/citizens/iri/world/model.glb`

A future GLB should preserve Iri's slender researcher silhouette, pearl/lilac/cyan material language, and sensor-halo identity while continuing to consume the same Simulation position / travel contract.
