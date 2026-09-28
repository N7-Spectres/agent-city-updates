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
