# Agent City Departments

These folders are the persistent development memory for Agent City.

The purpose is to let specialized development tasks work independently without requiring one chat/thread to carry every detail forever.

## How to Start a Department Task

A new task should begin by reading:

1. `docs/AGENT_CITY_PROJECT_STATE.md`
2. its department's `STATE.md`
3. its department's `DECISIONS.md`
4. its department's `BACKLOG.md`

Then continue from the recorded state instead of reconstructing the project from chat history.

## Department Files

Each department maintains:

### STATE.md
What exists **right now**.

Include:
- current implementation
- current version
- files/systems owned
- known bugs
- current work
- recent test observations

### DECISIONS.md
Rules that should not be casually reversed.

Use this for:
- architecture laws
- design constraints
- ownership boundaries
- decisions made after testing

### BACKLOG.md
Future work and open questions.

Backlog entries are **not implemented features**.

## Departments

- `assets/` — Assets & Interface
- `memory/` — Memory & Social
- `communication/` — Communication & Perception
- `simulation/` — World & Simulation

## Cross-Department Rule

Departments may request data or behavior from one another, but should avoid silently modifying systems owned elsewhere.

Example:

- Assets may request travel progress data.
- Simulation defines the travel duration and exposes validated progress.
- Assets visualizes it.

Another example:

- Memory may request event participant IDs.
- Simulation records the event.
- Memory decides how that event is remembered.

## Shared Laws

> **The AI may decide intent. The simulation decides reality.**

> **Information must travel through a real mechanism.**

> **Visitors are visitors, not rulers.**

> **Full history may be stored locally, but model context must remain bounded.**

## Release Philosophy

Prefer substantial milestones over micro-updates.

When the city surprises us, treat the surprise as test data and strengthen the underlying systems.
