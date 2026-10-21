# Agent City — Current 3D Citizen Model Notes

_Last updated: 2026-10-20_

## Why this exists

The first true/current Cato 3D model is the style benchmark for the remaining citizens.

The older PNG/WebP runtime bodies were useful pre-3D presentation assets, but they must **not** become the geometry template for new citizen meshes. Their proportions, panel breaks, pose, and sprite-specific compromises are historical presentation artifacts.

## Canonical source priority

When building or revising a citizen model, use this order:

1. **Current accepted 3D model / mesh** — highest visual authority.
2. **These current 3D model notes** — silhouette/personality requirements.
3. **Latest approved concept sheets** — identity cues, accent family, visor language, distinctive motifs.
4. **Old runtime PNG/WebP bodies** — legacy UI/reference only; never use them as the primary geometry/proportion source.

If an old PNG conflicts with the current Cato-style 3D language, the 3D language wins.

## Shared species language

All six citizens should clearly belong to the same mechanical species/family:
- glossy dark face visor
- readable emissive eye display
- cream/off-white primary shell language
- dark graphite/charcoal internal mechanics
- modular hard-surface armor over articulated joints
- similar joint logic, hand/foot construction, and face-shell architecture
- citizen-specific accent color and silhouette cues

Do **not** make five totally different robot species.

Cato is the current style baseline, but **not** the body-shape template. Each citizen should look unmistakably different from Cato at silhouette distance.

## Base-body rule

Every base citizen model is equipment-free.

Do not permanently model:
- backpacks
- crates
- tablets
- scanners
- drones
- tool arms
- medical kits
- cargo hooks/harnesses
- profession-specific tools

Those belong to future optional attachment/equipment meshes when Simulation authorizes them.

Permanent identity features are allowed when they define the citizen rather than their inventory, e.g. Iri's halo motif or Noma's leaf-like antenna shapes.

## Presentation-height cues

These are **visual identity cues only**, not Simulation physics dimensions:

| Citizen | Presentation cue |
| --- | ---: |
| Cato | ~2.10 m reference |
| Vale | ~2.00 m |
| Aris | ~1.85 m |
| Iri | ~1.78 m |
| Bex | ~1.60 m |
| Noma | ~1.60 m |

Use them to maintain obvious relative character identity. Do not turn them into collision, carrying, speed, or capability rules.

## Personality must survive at silhouette distance

The goal is that a viewer can identify the citizen before reading a label:

- **Cato** — broad, heavy, powerful logistics chassis.
- **Aris** — lean, agile, outward-looking field/explorer silhouette.
- **Bex** — compact, practical maker/fabricator silhouette.
- **Iri** — slender, precise, elegant technical silhouette with halo motif.
- **Noma** — compact, softer field-science silhouette with leaf-like antenna identity.
- **Vale** — tall, balanced, approachable support/generalist silhouette with the most socially expressive face language.

## Visor expression

Visor expression is personality presentation, not hidden emotional state.

Model the face/visor so emissive eye shapes can later support:
- neutral
- blink
- happy/curved
- focused/narrow
- curious/asymmetric

Do not bake one permanent expression into the geometry.

## Modeling handoff

Before any of the remaining five models are approved:
- compare them directly beside the current Cato model, not beside the old sprite;
- verify same-world mechanical language;
- verify distinct silhouette/personality;
- verify no optional equipment was baked into the base;
- verify scale reads correctly beside Cato;
- verify the model still reads clearly from the RTS Local camera.

> **Current 3D model wins over old sprite geometry. Identity stays. Equipment changes. Simulation remains truth.**
