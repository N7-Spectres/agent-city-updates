# Aris — Pre-Blender Local World Body

_Last updated: 2026-09-30_

## Purpose

Aris is the second Agent City citizen promoted from a circular Local-map token to a body-shaped world presentation.

This remains a **2.5D pre-Blender presentation**, not a physical mesh, rig, collision body, or locomotion model.

Core authority remains:

> **Simulation defines reality. Assets renders reality.**

## Canon Reference

Approved concept reference:

`static/assets/citizens/aris/reference/concept/approved_dark_sheet_v1.webp`

The sheet is the durable visual reference for Aris's:
- lean navigator / surveyor silhouette
- cream + teal body language
- orange navigation accents
- cyan visor / display language
- scarf / explorer styling as visual identity reference
- relative presentation height cue of approximately 1.85 m

The 1.85 m cue is visual canon used to preserve relative character identity in Assets. It does not create a Simulation physics dimension unless Simulation later defines one.

## Current Runtime Representation

Local 3D uses:

`static/assets/citizens/aris/world/front.webp`

The body sprite:
- is equipment-free runtime body art
- is anchored to Aris's authoritative Local world position
- uses the same real route-travel interpolation pipeline as Cato
- scales with camera depth
- keeps a Local zoom-out readability floor
- remains selectable through the existing citizen / Visit flow

## Relative Presentation Scale

Cato remains the visual reference at 2.1 m / scale 1.0.

Aris uses:
- presentation scale: `0.881`
- minimum Local readable scale: `0.52`

This lets Aris read as noticeably leaner and shorter than Cato while remaining identifiable at the widest Local zoom.

These are renderer values only. They do not define collision, reach, mass, speed, carrying ability, or any other capability.

## Local-Only Boundary

Full citizen bodies are a Local world presentation.

Region / Planet continue to omit citizen body markers. No Aris body is promoted to global spatial truth.

## Equipment Separation

Aris's concept sheet contains exploration / survey motifs and example gear.

Those remain design references unless real equipped state exists.

No:
- survey tablet
- explorer pack
- scanner
- beacon
- tool
- cargo
- capability

becomes authoritative merely because the concept art depicts it.

## Selection / Motion

Allowed presentation:
- cyan ground-contact affordance
- body-shaped hover / selection glow
- subtle travel-only bob when a real travel job exists
- synchronized ground shadow
- reduced-motion static fallback

The renderer never creates travel or writes coordinates.

## Future Model Slot

Reserved presentation path:

`static/assets/citizens/aris/world/model.glb`

A future GLB should preserve Aris's lean navigator silhouette while continuing to consume the same Simulation position / travel contract.
