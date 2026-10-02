# Agent City v1.0 — Material Independence Contract

## Milestone

v1.0 means the civilization has a real Simulation-supported path to replace essential manufactured starter supplies from locally obtained raw materials.

It does **not** mean infinite resources, guaranteed survival, a technology tree, or omniscient research.

## Canonical Evidence Chain

```
real raw material
  -> validated material-property discovery
  -> citizen-owned learned production process
  -> legal process_material action
  -> jobs.id
  -> production_events.id
  -> physical resource output
```

Every downstream capability must remain reconstructable from this chain.

## Authority

Simulation owns:
- hidden material truth
- property-to-process support rules
- process inputs / outputs / yields
- required structure
- energy and time
- action legality
- production events
- physical resource changes

The planner chooses whether to pursue available work. It cannot invent or alter production physics.

## Discovery Boundary

Production definitions remain hidden until the citizen owns every prerequisite verified discovery.

Raw material presence does not imply:
- smeltability
- conductivity
- workability
- battery suitability
- lubricant suitability
- a conversion recipe

Conversation may transmit claims but cannot silently grant verified production capability.

## Citizen Ownership

Production knowledge is citizen-owned through `learned_processes`.

Another citizen does not gain a production process merely because:
- somebody else learned it
- the UI displays the output material
- a conversation mentioned it
- the civilization has used the process before

Future process teaching may be added only through a real evidence/provenance mechanism.

## Physical Production

`process_material` is a real timed job.

At start:
- legal process knowledge is revalidated
- required structure must be operational
- required inputs must exist
- energy safety must pass
- inputs are physically consumed
- energy is physically consumed

At completion:
- outputs enter Seed Site storage
- `production_events` records the job, process, inputs, outputs, outcome, and summary
- citizen and structure wear apply
- ordinary fabrication-family practice evidence may be recorded

## Current First-Generation Replenishment

The current world supports evidence-backed paths for:
- Processed structural material
- Conductive wire
- Mechanical components
- Lubricant
- Fasteners
- Battery cells
- Basic electronics

These paths depend on discoveries involving Ferrite Stone, Silicate, Copper-like Ore, Carbonaceous Rock, Native Resin, and the produced intermediate Crude Metal Stock.

This list is Simulation implementation, not citizen foreknowledge.

## Regression Invariant

`tests/smoke_v100_material_independence.py` must continue to prove:

1. hidden production/world truth is absent from ordinary snapshot state
2. no production action exists merely because raw stock is present
3. verified experiments unlock only evidence-supported processes
4. intermediate material can require its own testing
5. all seven manufactured starter categories can be reproduced after their starting amounts are set to zero
6. real production events are persisted
7. sustainability context recognizes learned replenishment instead of remaining hard-coded
8. locally reproduced maintenance stock can service a real due structure

If any of those fail, Agent City no longer satisfies the v1.0 Material Independence milestone.
