# Agent City v0.8 — Citizen Visual Asset System

_Status: planned design package for v0.8.0 Living World_
_Owner: Assets & Interface_
_Last updated: 2026-09-28_

## Purpose

v0.8 should turn the six citizens from generic interface markers into recognizable visual individuals while preserving the core project law:

> **Simulation defines reality. Assets renders reality.**

The citizen visual system must separate:

1. **permanent citizen identity**
2. **temporary facial / visor expression**
3. **validated physical equipment**
4. **validated activity state**

The art may make citizens charming and recognizable. It may not grant equipment, capability, damage, or physical outcomes.

---

## Shared Species / Civilization Language

All six citizens belong to the same mechanical civilization.

Preserve across the set:

- shared cream / off-white outer shell language
- dark graphite / black internal mechanics
- glossy dark visor face
- luminous eye display
- rounded humanoid mechanical proportions
- common joint / panel / foot design vocabulary
- small geometric chest identity mark
- strong individual accent color
- recognizable head silhouette at tiny token size

They should look related without looking cloned.

The current concept-art family is the preferred visual direction. The **first/refined concept-sheet family** is favored over the later more generic render because it preserves more individuality.

---

## Identity vs Equipment — Hard Rule

Every citizen needs a clean **base-body design** that works with no optional equipment.

Do not permanently bake these into the base body:

- backpacks
- cargo harnesses
- scanners
- tablets
- fabrication kits
- medical/support kits
- crates
- hand tools
- future devices
- any other item that Simulation may later create, transfer, lose, store, service, or destroy

Optional equipment is a separate visual layer.

Core rule:

> **Owning or using equipment must come from validated physical state, not from concept art.**

A prop shown in a concept sheet is a design idea, not proof that the citizen owns it.

---

## Canonical Citizen Directions

These are visual identity directions, not gameplay classes.

### Aris

Canonical aptitude:
**Extraction / prospecting**

Keep:

- teal / cyan identity
- explorer-like head shape
- scarf / neck-wrap identity
- light, agile field silhouette
- curious / outward-looking visual personality

Refine toward:

- prospecting
- field resource assessment
- extraction-site judgment
- exploratory fieldwork

Do not make mapping/navigation his entire permanent identity.

Survey scanners, prospecting tools, sample gear, and field packs are optional equipment.

### Bex

Canonical aptitude:
**Fabrication**

Keep:

- orange identity
- compact, hands-on silhouette
- expressive visor personality
- practical maker energy

Bex should visually read as someone who builds, repairs, adapts, and fabricates.

Do not permanently bake in:

- tool arm
- fabrication backpack
- belt tools
- crates/material packs

Those are equipment layers.

Avoid making Bex the primary construction citizen. Construction is Iri's starting aptitude.

### Cato

Canonical aptitude:
**Logistics / hauling**

Keep:

- heavy body
- broad torso
- oversized shoulders
- sturdy legs / feet
- yellow / industrial steel identity
- visibly larger/heavier proportions than the others

Cato's mass is **canonical body identity**, not removable equipment.

Do not slim Cato down.

Separate optional:

- cargo harness
- hooks
- crates
- dollies
- packs
- hauling accessories

Cato should read as resource movement / logistics more than infrastructure construction.

### Iri

Canonical aptitude:
**Construction**

Keep:

- elegant, tall/slender silhouette
- purple / cyan accents
- halo / antenna alignment motif
- precise body language
- refined, technical appearance

Iri should remain one of the visibly slimmer citizens.

Reinterpret the halo/sensor motif toward:

- alignment
- measurement
- structural planning
- site layout
- projected plans
- precision construction

Do not frame Iri primarily as a laboratory researcher.

Optional construction/survey equipment remains separate from the base body.

### Noma

Canonical aptitude:
**Research / experimentation**

Keep:

- green identity
- softer field-science visual language
- curious, observant presence
- leaf-like / organic-inspired silhouette details where useful

Broaden beyond ecology.

Noma should plausibly study:

- minerals
- material properties
- chemistry
- atmosphere
- biology
- environmental systems
- unknown physical phenomena

Plant imagery, sample canisters, scanners, and field packs may remain part of Noma's visual vocabulary, but they are not permanent profession locks or mandatory equipment.

### Vale

Canonical aptitude:
**Generalist / cooperation**

Keep:

- warm red accent
- approachable proportions
- highly expressive visor language
- supportive / socially readable presence

Shift away from explicit medic identity.

Avoid permanent:

- medical cross
- dedicated doctor symbolism
- medical backpack

Vale should visually communicate:

- coordination
- assistance
- adaptability
- cooperation
- community support
- the citizen who can help almost anywhere

Support tablets, utility bags, headsets, or future tools are optional equipment.

---

## Relative Silhouette / Scale Notes

These ratios are **visual design ratios only**, not physical Simulation heights unless later made authoritative.

Use a shared baseline body scale of 1.00.

- **Aris:** ~1.00, lean/agile
- **Bex:** ~0.97–1.00, compact/practical
- **Cato:** ~1.10–1.15, broad/heavy
- **Iri:** ~1.03–1.07, tallest/slimmest elegant silhouette
- **Noma:** ~1.00, medium/light with softer silhouette
- **Vale:** ~1.00, balanced/approachable

All six should still share enough anatomy/joint language to feel like the same mechanical species.

---

## Required 2D Asset Tiers

### 1. Head / Home token

Used for:

- Home citizen rail
- map markers
- compact directories
- small interaction surfaces

Target display:
**64–96 px**

Each citizen should have a small expression sprite set.

Minimum:

- neutral / eyes open
- blink / visor blank

Recommended:

- neutral
- blink
- happy `^ ^`
- soft-happy curved eyes
- focused / narrow
- curious / asymmetric
- optional rare surprised state later

### 2. Bust / conversation portrait

Used for:

- richer chat surfaces
- directory cards
- future visitor interaction polish

Target source:
**128–256 px or larger master downsampled for UI**

Bust art should visually match the head token and full-body body design.

### 3. Full-body citizen asset

Used for:

- Citizens character sheet
- future richer location/world presentation
- later 3D modeling reference

Preferred production master:

- clean neutral or relaxed 3/4 stance
- transparent background
- no optional equipment
- same canvas/anchor conventions across all six
- enough resolution for a ~700–1000 px tall web display
- larger archival master may be retained separately

---

## Visor Expression System

The visor is a major personality channel.

Expression animation is a **presentation system**, not a hidden emotional simulation.

Safe idle mannerisms may include:

- periodic blink
- occasional happy eye shape
- subtle curious eye variation
- subtle focused eye variation

Blink behavior:

- mostly neutral/open frame
- switch to blank visor for roughly 120–180 ms
- randomized interval per citizen
- avoid synchronized blinking across the population
- rare double blink is acceptable

Suggested personality bias:

### Aris
- neutral
- curious
- occasional happy squint

### Bex
- frequent happy `^ ^`
- playful asymmetric expression
- focused while fabricating

### Cato
- mostly steady neutral
- focused while hauling
- rarer but very readable happy expression

### Iri
- calm neutral
- narrow/focused precision eyes
- subtle pleased curve

### Noma
- gentle curious
- soft happy
- attentive/focused during experiments

### Vale
- most socially expressive
- warm `^ ^`
- attentive curves
- supportive / reassuring expression family

Activity-linked expression changes may use validated state, but must not claim unsupported internal emotion.

---

## Lightweight Motion System

Keep browser motion inexpensive.

Prefer:

- CSS `transform`
- CSS `opacity`
- sprite/frame swaps
- compositor-friendly movement

Examples:

- idle: subtle bob
- travel: real route movement + small travel bob
- talking: subtle pulse / expression cycle
- charging: inexpensive opacity-based glow
- working: focused expression or light status motion

Avoid widespread continuous:

- large blur animation
- expensive filters
- heavy animated shadows
- particle systems on every citizen

Respect:

`prefers-reduced-motion`

---

## Modular Equipment Layering

The character sheet should be able to visually change as the civilization physically changes.

Recommended conceptual layer order:

1. rear / backpack equipment
2. base body
3. chest / waist equipment
4. held / arm-mounted equipment
5. foreground accessories

All layers should share:

- same canvas size
- same body origin
- same scale
- documented attachment points

Example:

`Bex base body + real fabricated cargo pack`

If the equipment is removed, transferred, stored, broken, or replaced, the visual layer should update from authoritative state.

Do **not** treat simple inventory ownership as necessarily "equipped" if Simulation later distinguishes possession from active attachment/use.

### Future Simulation contract needed

Before v0.8 visual equipment layering is fully authoritative, Assets may need a stable physical interface for:

- equipped / attached equipment IDs
- equipment owner
- current location
- optional visual attachment slot such as:
  - back
  - chest
  - waist
  - left hand
  - right hand
  - arm mount

Until such a contract exists, show validated equipment in lists but avoid guessing which body slot it occupies.

---

## Suggested Asset Manifest

Example:

```json
{
  "aris": {
    "accent": "#5dd7df",
    "body": {
      "base": "citizens/aris/base_full.webp"
    },
    "head": {
      "neutral": "citizens/aris/head_neutral.webp",
      "blink": "citizens/aris/head_blink.webp",
      "happy": "citizens/aris/head_happy.webp",
      "focused": "citizens/aris/head_focused.webp",
      "curious": "citizens/aris/head_curious.webp"
    },
    "bust": {
      "neutral": "citizens/aris/bust_neutral.webp"
    }
  }
}
```

The manifest should be presentation data only.

It must not create physical inventory or capabilities.

---

## Performance Strategy

Home should load only lightweight token assets.

Recommended:

- head token: 64–96 px
- bust: lazy or context-loaded
- full body: lazy-load selected citizen
- equipment overlays: lazy-load only when required for the selected citizen

Do not load six giant full-body masters just to draw six Home tokens.

The isolated motion-bench experiment showed the core interaction idea works well conceptually:

- six moving citizen tokens
- route travel
- idle / work / talk states
- citizen selection
- larger crowd stress mode

The production implementation must use real Agent City state rather than the scripted motion plan used by the isolated bench.

---

## Character Sheet Target

The Citizens page should visually become:

**Left**
- citizen directory with living head token

**Main**
- full-body base citizen render
- validated equipment overlays when available
- physical status / maintenance
- cargo / capacity
- work / projects
- bounded knowledge / memory

The full body is identity.

The equipment is current physical configuration.

Those two concepts must remain separate.

---

## Home Citizen Rail Target

Replace letter-only circles with the citizen's real head token.

The token may:

- blink
- show occasional idle expression
- reflect talking/working/travel state through safe presentation cues

At tiny size, individual accent colors and head silhouettes must remain instantly recognizable.

---

## Future 3D Translation

The 2D concept art should become the **visual reference canon** for later 3D work.

When 3D arrives:

- preserve body proportions/silhouettes
- preserve accent identities
- preserve Cato's large heavy chassis
- preserve Iri's especially slim/elegant chassis
- preserve shared mechanical species language
- keep gear as separate meshes / attachments
- use the visor expression set as an emissive texture atlas or equivalent
- do not permanently model optional props into base meshes

A future procedural/local asset worker may generate or assemble GLB assets from validated Simulation objects, but:

> **The generated mesh represents physical state. It does not define physical state.**

---

## v0.8 Citizen Visual Deliverables

Desired package for all six citizens:

- clean base full-body asset
- consistent 3/4 reference
- optional front reference
- head neutral token
- head blink token
- happy expression token
- focused expression token
- curious/soft expression token as appropriate
- bust portrait
- accent palette
- proportion note
- optional-equipment concept sheet kept separate from base body
- manifest entry
- documented future attachment points

Primary citizen set:

- Aris
- Bex
- Cato
- Iri
- Noma
- Vale

---

## Non-Goals / Guardrails

v0.8 citizen art must not:

- create equipment in Simulation
- imply an item is equipped just because concept art includes it
- assign new skills from visual design
- expose hidden world facts
- invent damage based only on artistic weathering
- force a citizen into a profession beyond their canonical aptitude
- make expressions authoritative emotional-state claims
- require 3D/Mixamo before the 2D system is useful

---

## Core Visual Principle

> **Identity stays. Equipment changes. Expressions live. Simulation remains truth.**
