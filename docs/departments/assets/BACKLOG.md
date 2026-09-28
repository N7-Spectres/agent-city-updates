# Assets & Interface — Backlog

## Ready for Next Session — v0.6 Contracts Arrived

### Simulation — Ready
- consume safe `/api/state` from `simulation/v0.6-research-discovery`
- use safe `discoveries`, `citizen_knowledge`, `experiment_results`, `learned_processes`, and `locations[].known_facts`
- stop assuming deposit reserve `amount` exists in public state
- verify/consume authoritative citizen cargo capacity if present in the final branch
- never expose hidden `world_properties`

### Communication — Ready
- consume structured `status/availability` from `GET /api/visit/{citizen_id}`
- distinguish remote / visitor traveling / citizen traveling / talking / busy / missing
- preserve remote privacy masking
- keep Memory APIs as the normal knowledge UI source; use Communication provenance only where source/transfer context is explicitly needed

### Memory — Completed
- bounded per-citizen knowledge endpoint consumed
- location notebook remains partitioned by citizen
- source/time/verification/channel metadata displayed without merging truth

## Review / Validation — v0.6 Branch

- runtime-test draft PR #3 / `assets/v0.6-knowledge-ui`
- verify Home remains map-centered with compact citizens and Visit
- verify Home no longer grows secondary datasets underneath the map
- verify Citizens page selection and "Visit on Home" handoff
- verify Locations page selection and "Focus on Home map" handoff
- verify visitor map badge opens the correct location
- verify Records tabs still preserve Making / Stores / History / Region / Updates
- verify narrow/mobile navigation
- verify no undiscovered resource/property leaks through Locations
- verify character sheets do not invent appearance/configuration

## Completed in v0.6 Independent Slice

- top-level Home / Citizens / Locations / Records navigation
- compact Home citizen rows
- compact visitor location badge
- simplified Home layout
- Citizens character-sheet shell
- placeholder-safe citizen visual identity slot
- Locations field-notebook shell
- placeholder-safe location scene slot
- discovered-resource filtering
- Records page separation
- specific backend visit reason displayed instead of generic inaccessible label

## Later

- richer citizen identity art from authoritative visual assets
- richer location scene art from authoritative known environment state
- map work-site activity
- tiny robot / portrait tokens
- planet/globe representation
- accumulated environmental history visualization

## Current Blocker

_None._ Simulation, Communication, and Memory contracts are all ready.

The remaining v0.6 work is implementation on PR #3 in the next Assets session, not an external dependency.
