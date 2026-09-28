# Assets & Interface — Decisions

## Visual Truth Rule

> **The visual layer may display simulation state. It may not create simulation state.**

Examples:

- show travel only if a real travel job exists
- move a citizen marker according to the real job start/end time
- show a building only after construction succeeds
- show cargo only if it exists in inventory
- show deposits only after validated discovery

## Map Philosophy

The map should become a readable physical world, not a decorative dashboard.

Stylization is allowed, but visual spacing should communicate meaningful geography whenever practical.

### v0.4 map rule

Before a true planet view exists, use the simulation's existing route distance as the source for relative map spacing where possible.

Presentation geometry may improve readability, but must not alter route distance or travel duration.

## Visitor Presentation

N7 and other visitors should have visible physical presence.

Visitor markers must not imply teleportation or remote face-to-face conversation.

## UI Philosophy

Important information should remain above the fold when practical.

Avoid requiring repeated page scrolling to switch between core views.

### v0.4 Control Room decision

Keep **Visit permanently visible** in the right rail.

Place Region / Stores / Structures / History / Updates in a separate persistent Control Room beneath it rather than making Visit itself a utility tab.

This preserves conversation continuity while allowing secondary state to be inspected without leaving the interaction surface.

## Citizen Cluster Decision

When several citizens occupy one location, use a compact labeled token cluster in a dedicated presentation zone around the location rather than stacking anonymous dots on the location marker.

Citizen initials are the current token stage; richer robot/avatar tokens may replace them later.

## Future Avatar Rule

Citizen avatars/tokens may become richer over time, but identity art must remain a presentation layer over validated citizen state.

## Ownership Boundary

Assets may request additional state fields from Simulation but should not alter action duration, resource outcomes, or physical legality simply to improve UI behavior.


## Review / Merge Rule

The v0.4 interface work remains presentation-only until runtime-tested.

Do not merge or publish the interface branch solely because static structural checks pass. Runtime behavior must confirm that visitor travel, citizen travel, selection, chat persistence, pause controls, updater controls, and responsive layout still work with real application state.


## v0.5 Conversation Viewport Rule

Long visitor conversations must scroll inside a bounded Visit panel.

The message log may grow historically, but the page layout should not become taller simply because a conversation is long. Visitor input/actions remain visible and usable outside the scrolling message viewport.

## v0.5 History Presentation Rule

History should distinguish:

- stored conversation content actually present in the current state snapshot, and
- authoritative chronology events whose exchange content is not present in that snapshot.

When only chronology is available, show the confirmed event metadata and explicitly say the exchange text is unavailable. Do not reconstruct or invent missing dialogue.

History is the default Control Room view for v0.5 because it is the most directly useful companion to persistent Visit interaction; Region remains available as a tab and physical region state remains centered in the world view.

## v0.5 Making & Building UI Rule

Fabrication, projects, equipment, tool modifiers, cargo-capacity effects, structures, sites, and construction progress may only be shown from authoritative Simulation state.

Assets must not derive physical bonuses or infer completion from names, LLM text, chronology prose, or frontend calculations when Simulation exposes a validated field instead.

Stable physical IDs should be preserved in UI data attributes / future links where useful so project, structure, tool, and history surfaces can refer to the same real object.


## Dependency Gate Rule

When a requested UI surface depends on new Simulation-owned physical state, Assets should complete independent presentation work first, then stop at a clear dependency boundary.

Do not mock, infer, or temporarily synthesize project/tool/structure state merely to finish the interface ahead of the authoritative schema.


## v0.5 Canonical Conversation Identity Rule

For v0.5 History, `citizen_conversations.id` / `source_id` is the stable UI identity for a real stored citizen exchange.

When present, `source_job_id` may be shown as the physical talk-job anchor.

A failed talk attempt with no conversation row remains chronology only. Assets must never manufacture a transcript or conversation card to make the chronology look complete.

## v0.5 Making View Decision

The former **Structures** Control Room tab becomes **Making** for v0.5.

It groups three related authoritative physical surfaces in one place:

- Projects
- Equipment
- Structures

This is a presentation grouping only. It does not merge their simulation semantics.

## Local Coordinate Presentation Rule

v0.5 `x_km/y_km` values are shown only as local site coordinates.

Do not render them as proof of a continuous globe/free-roam world until Simulation actually owns that geography.


## v0.5 Integration Ownership Rule

Once the Assets branch is complete and marked REVIEW, cross-branch assembly belongs to the coordinator.

Assets should not merge Simulation-owned code into its department branch merely to produce a single milestone branch. The coordinator must integrate completed department branches while preserving each department's invariants and then smoke-test the assembled runtime.


## v0.6 Information Architecture Rule

Home is the place to visit the city, not the place to display every dataset.

Keep Home focused on:
- compact citizens
- world/map
- selected-citizen Visit

Move deeper information into dedicated top-level views:
- Citizens
- Locations
- Records

## v0.6 Knowledge-Bound UI Rule

The UI may show known state, not hidden Simulation truth.

For Locations and Citizens:
- undiscovered resources/properties are absent
- communicated claims remain distinguishable from verified discovery/observation
- one citizen's knowledge must not silently become every citizen's knowledge
- placeholder visuals must not imply real equipment, structures, appearance, or environment details that are not authoritative

## v0.6 Missing-Knowledge Presentation Rule

Missing knowledge is normal.

Do not render unknown facts as tantalizing locked fields, silhouettes of undiscovered resources, question-mark technologies, or other UI that reveals the shape of hidden truth.

Prefer omission or a neutral empty state.

## v0.6 Records Separation Rule

Making, Stores, History, Region, and Updates/Admin remain accessible, but they live outside Home in a dedicated Records view so secondary state does not compete with the world/visit experience.


## v0.6 Consumer Layering Rule

Use each department's read model for its own layer:

- **Simulation safe public state** for current validated physical/world facts
- **Memory bounded APIs** for normal citizen/location knowledge surfaces
- **Communication availability/provenance** for how information arrived and why a visit is or is not accessible

Do not replace Memory's bounded consumer knowledge view with Communication's lower-level provenance/debug surface.

Do not reconstruct hidden Simulation truth from missing fields.

## v0.6 Visit Privacy Rule

When the visitor is remote from a citizen, the UI must not reveal that citizen's local busy/talking counterpart merely because Communication knows it.

Render the backend-provided `status/reason/availability` as bounded by Communication's privacy logic rather than independently inspecting remote citizen jobs.


## v0.7 Home Rail Rule

On desktop, Citizens, World, and Visit should share one approximate vertical height budget.

Long lists and conversations scroll inside their rails rather than stretching the page.

## v0.7 Recent Activity Rule

Home Recent Activity is a compact at-a-glance surface, not a second full history.

Show about five meaningful items.

Conversation summaries may come only from real stored `citizen_conversations`.

Failed talk attempts remain events and must never be converted into synthetic conversation summaries.

Routine low-value churn such as ordinary observe/wait activity should not crowd Home.

## v0.7 Avatar Presentation Rule

Avatar identity is presentation-only.

Until unique authoritative art exists:

- use a neutral mechanical fallback
- use initials and interface accent identity
- do not imply physical paint, clothing, equipment, damage, or customization

State animation may reflect only validated current activity/job state.

Future 2D art should drop into the manifest without changing layout structure.

## v0.7 Motion Rule

Avatar motion is subtle status presentation, not a physics layer.

Allowed examples:
- idle bob/pulse
- travel bob while Simulation provides real route movement
- charging glow
- talking/working status animation

Respect `prefers-reduced-motion`.

## v0.7 Maintenance Alert Rule

Do not create maintenance alarms from guessed thresholds.

Use Simulation-owned degraded/maintenance/failure semantics or explicitly handed-off threshold guidance.

Home should show only meaningful exceptions. Detailed condition belongs on Citizens/Records.


## v0.7 Maintenance Field Consumption Rule

Use Simulation's v0.7 condition semantics directly.

- show `condition_state`, `service_due`, `operational`, battery/chassis service fields as authoritative
- show `effective_cargo_bonus` and `effective_extraction_speed_multiplier` as current equipment capability
- do not substitute pristine design modifiers for current effective capability
- do not rederive maintenance thresholds in JavaScript
- critical/non-operational equipment and structures remain visible
- a condition percentage alone does not authorize invented visible damage

## v0.7 Maintenance History Rule

`maintenance_events[]` is the physical maintenance history source.

Home Recent Activity should favor meaningful completed maintenance events or threshold-level exceptions, not microscopic wear.

Communication `diagnostic` rows are debug/system records, not citizen speech and not conversation summaries.

Memory guidance remains separate: a physical maintenance event does not automatically mean a citizen remembers it.


## v0.7 Effective Capability Rule

For worn equipment, display Simulation's authoritative effective modifiers:

- `effective_cargo_bonus`
- `effective_extraction_speed_multiplier`

Pristine design modifiers are not current capability and must not be substituted.

## v0.7 Diagnostic Presentation Rule

Communication `diagnostic` history is system/debug information.

- exclude diagnostics from normal Home Recent Activity
- never render diagnostics as citizen speech or conversation summaries
- diagnostics may remain visible as muted system/debug rows in full History


## v0.7 Integration Handoff Rule

Assets v0.7 is complete once its branch is in REVIEW with branch-level UI contracts verified.

Final cross-department assembly belongs to the coordinator. Assets must not merge Simulation, Communication, or Memory runtime code into its presentation branch merely to produce a single combined release branch.


## Citizen Concept Sheets / Canonical Visual Identity

The six generated Agent City character sheets are approved as strong visual identity references for the citizens' bodies, silhouettes, face-display style, accent families, and overall mechanical design language.

Important authority boundary:
- embedded role labels, slogans, depicted tools, packs, drones, tablets, medical kits, or other accessories in concept art are **visual concept material**, not automatic Simulation truth
- current canonical citizen aptitudes remain defined by the project/runtime unless explicitly changed by coordinator decision
- gear shown in a concept sheet does not mean that citizen physically owns that equipment
- when the runtime later supports authoritative equipped gear, the rendered avatar may add/remove/alter visible equipment to match actual state
- preserve the core body/face/color identity even as real equipment changes

The visual layer must not convert concept-art props into physical inventory or capabilities.


## v0.8 Citizen Asset Architecture Rule

Citizen visuals are layered:

1. permanent base identity
2. visor expression
3. validated physical equipment
4. validated activity presentation

Core rule:

> **Identity stays. Equipment changes. Expressions live. Simulation remains truth.**

Base-body art must not bake in optional gear.

Full details:
`docs/departments/assets/V080_CITIZEN_VISUAL_SYSTEM.md`

## v0.8 Expression Rule

Blink/happy/focused/curious visor frames are lightweight presentation/personality.

They are not authoritative hidden emotional-state claims.

Activity-linked expression choices may use validated state, but idle mannerisms remain non-physical presentation.

## v0.8 Equipment Overlay Rule

Do not visually attach a backpack/tool/device merely because:
- concept art showed it
- the citizen's aptitude suggests it
- it exists somewhere in inventory

Equipment overlays require authoritative physical possession/attachment semantics.

If Simulation later distinguishes "owned" from "equipped/attached", Assets must obey that distinction.


## v0.8 Home Job Progress Rule

Home may display active-job progress only from authoritative Simulation timing:

- `start_minute`
- `end_minute`
- current `sim_minute`

Idle rows stay compact. UI progress must not estimate duration independently.

## v0.8 Chat Keyboard Rule

Visitor chat uses one submit path.

- Enter requests normal form submission
- Shift+Enter inserts newline
- IME composition does not submit
- Talk button remains functional
- an explicit in-flight guard prevents duplicate sends

## v0.8 Runtime Visual Profile Rule

Citizen presentation canon may define:

- accent identity
- silhouette family
- base-body asset slots
- visor-expression asset slots

It may not define:

- inventory
- equipped gear
- capability
- physical dimensions unless Simulation later makes them authoritative

Canonical visual profiles are presentation metadata.

## v0.8 Asset Worker Rule

Persistent asset generation is asynchronous presentation infrastructure.

Physical objects/projects must remain valid even when:

- the worker is offline
- a job is queued
- generation fails
- Blender is not installed
- no rich asset exists yet

Use a safe fallback until a generated asset is ready.

Full contract:
`docs/departments/assets/V080_ASSET_WORKER_CONTRACT.md`

## v0.8 Render Aggregation Rule

Use the minimum visual multiplicity needed to understand physical state.

- unique object → individual representation
- fungible quantity → representative bundle/pile/stack
- deposited bulk inventory → storage abstraction

Never spawn one visible mesh per simulation unit simply because quantity is large.

## v0.8 Spatial Rendering Gate

Do not convert presentation-only map geometry into physical continuous coordinates.

Continuous-world UI begins only after Simulation provides:

- coordinate frame / units
- safe citizen/landmark positions
- stable physical subject identity
- safe observation precision / extent

Approximate knowledge must remain approximate visually.


## v0.8 Safe Spatial Consumption Rule

When Stage 2 is authorized, Assets may consume only the safe Simulation read model:

- `state.spatial_frame`
- location `x_m/y_m`
- citizen `position_x_m/position_y_m`
- structure/project `x_m/y_m`
- visitor presence `x_m/y_m`
- `state.spatial_observations[]`

Reference frame:
- `seed_site_local`
- meters
- +x east
- +y north
- local tangent plane
- no global lat/lon mapping yet

Do not expose or infer:
- planet seed
- hidden generated-deposit tables
- hidden geometry/richness
- undiscovered procedural resources
- raw hidden query payloads

Observation radius is epistemic precision. Exact-looking decimals must not be presented as more precise than `radius_m`.

## v0.8 Stage 1 Travel Rendering Rule

Until Simulation provides continuous movement:

- route travel remains discrete physical state
- while traveling, citizen/visitor remains at the authoritative origin coordinate
- on validated arrival, switch to destination coordinate
- do not interpolate a physically meaningful path from endpoint x/y values

Presentation animation may continue to use existing non-authoritative map interpolation only where it is clearly presentation, but it must not be relabeled as continuous-world physical position.


## v0.8 Stage 2 Continuous Movement Rendering Rule

Stage 2 allows continuous local movement rendering only from Simulation's final authoritative movement payload.

Assets may smooth/render only the exact authoritative segment described by:
- start x/y
- target x/y
- start/end minute
- current authoritative x/y
- progress

Do not derive alternate routes, waypoints, hidden terrain paths, or inferred geometry.

## v0.8 Stage 2 Shared-Action UI Rule

Shared-action presentation has three separate identity layers:

1. Communication proposal/provenance ID
2. Simulation shared physical activity ID
3. Simulation physical movement job ID

UI labels must preserve the physical boundary:

- `proposed` / `accepted` = intent, no movement
- `active` / Communication `started` = real physical job exists
- `complete` / Communication `completed` = Simulation completion
- `rejected` / failed / cancelled = no active physical movement

A proposal card must never look like an active movement marker before `simulation_action_id` exists.

## v0.8 Stage 2 Observation Rendering Rule

Render an exploration observation only when Simulation supplies a real `spatial_observations.id`.

Use `radius_m` or equivalent uncertainty visually when practical.

Baseline observation must not visually imply:
- known material
- known geology
- exact deposit center
- hidden generated-body shape

Stable deposit identity may be used only after safe discovery exposes it.

## v0.8 Stage 2 Visitor Shared-Activity Rule

Visitor presence during a shared walk comes from the authoritative visitor-presence/shared-activity state.

Assets must not independently move the visitor because chat accepted a proposal.

Conversation agreement is intent; Simulation start is physical movement.


## v0.8 Stage 2 Local Focus View Rule

Physical coordinates and display scale are separate concepts.

The world view may automatically switch from regional meter scale to a local meter focus when a selected citizen or active shared activity would otherwise move only a few pixels.

The focus viewport may change:
- center
- scale
- which nearby known landmarks/evidence remain visible

It may not change:
- authoritative x/y
- movement target
- movement progress
- observation coordinates
- observation uncertainty

Local focus is a camera/readability decision, not a physical transition.

## v0.8 Stage 2 Authoritative Position Rule

During Stage 2 local/shared movement, the citizen and visitor markers use server-derived current x/y.

Browser smoothing is allowed only between successive authoritative updates on the same Simulation-defined segment.

No browser-side prediction may continue movement beyond the latest authoritative state.

## v0.8 Stage 2 Baseline Evidence Rule

A baseline observation may communicate:
- observed location
- radius/uncertainty
- safe terrain
- existence of a distinct physical contact when Simulation exposes a stable subject ID

It must not communicate material or classified geology merely because hidden Simulation truth contains those values.

## v0.8 Stage 2 Rejection Presentation Rule

Canonical Simulation rejection means no physical action began.

If Communication's broad synchronization layer later represents that terminal condition under a generic failure bucket, Assets should prefer the safe canonical `simulation_status = rejected` signal for the user-facing "Declined" label.

This is presentation compatibility only and does not rewrite Communication or Simulation state.

## v0.8 Asset Queue Separation Rule

The local Asset Worker cache is not part of civilization physical truth.

Its database:
`data/asset_worker.db`

must remain separate from the Agent City Simulation save.

The queue may persist:
- visual specs
- visual-job state
- generator provenance
- output cache metadata

It may not persist or mutate:
- physical inventory
- capability
- Simulation job state
- physical construction completion
- resource quantity
- hidden world truth

A failed/missing asset job results in fallback presentation, never a failed/missing physical object.


## v0.8.1 Runtime Citizen Art Rule

Approved full-body and token art is permanent presentation identity, not physical inventory.

For v0.8.1:
- `full`, `bust`, and `token` may reference approved art
- optional equipment layers remain empty unless physical equipped-state semantics later authorize them
- concept-sheet props never become runtime equipment merely because they are drawn

## v0.8.1 Expression Slot Rule

A static citizen token is not automatically a semantic expression frame.

`head.neutral`, `head.blink`, `head.happy`, `head.focused`, and `head.curious` remain null until separate approved frames exist.

This keeps future blink/personality animation explicit rather than inferring expressions from arbitrary crops.

## v0.8.1 Map Zoom Rule

Map zoom and focus are camera/presentation state only.

They may change:
- viewport center
- visual scale
- screen-space token spacing

They may not change:
- authoritative x/y
- physical movement
- observations
- known/hidden spatial truth

Region reset returns presentation zoom/center to default.

## v0.8.1 Map Hit-Target Rule

Location nodes keep a generous invisible click/focus target for usability.

Hover, selected, and keyboard focus should decorate only the node dot and/or label, not paint the full rectangular button surface.

Keyboard `:focus-visible` must remain visually clear.

## v0.8.1 Hotfix CI Rule

Department validation may use focused/temporary checks, but the coordinator owns the definitive release run.

For v0.8.1:
- department branch may validate aggressively
- temporary validation workflows must be removed before handoff
- official release workflow is preserved from `release-v0.8.1`
- coordinator performs the final full regression at VERSION bump before publication


## v0.8.1 Final Handoff Rule

Once the v0.8.1 Assets branch is:
- aligned 0-behind the official hotfix base,
- fully regression-tested,
- marked ready for review,
- and all Assets-owned dependencies are resolved,

Assets stops implementation and hands release ownership to the coordinator.

The coordinator owns:
- PR integration
- VERSION bump
- the definitive release smoke
- release metadata / updater publication

Assets must not publish `update.json` or continue changing the hotfix after handoff unless review feedback identifies an interface-owned regression.
