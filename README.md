# Agent City

Agent City is a local-first autonomous mechanical civilization simulation.

## Repository layout

- `main` is the coordination and publishing ledger.
  - `update.json` is the authoritative updater manifest.
  - `docs/` contains project state, department contracts, decisions, handoffs, and roadmaps.
- `release-v*` branches contain runnable Agent City release snapshots.
- The currently published runtime version is mirrored in root `VERSION` for human/tooling clarity.

## Release rule

A release is published only after the full regression workflow passes on the exact immutable release commit. `update.json` must point to that exact green SHA.

## Core laws

> The AI may decide intent. The simulation decides reality.

> Information must travel through a real mechanism.

Visitors can observe and participate, but they are not rulers, gods, or omniscient operators.
