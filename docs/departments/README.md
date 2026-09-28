# Agent City Departments

These folders are the persistent development memory for Agent City.

The purpose is to let specialized development tasks work independently without requiring one chat/thread to carry every detail forever.

## How to Start a Department Task

A new task should begin by reading:

1. `docs/AGENT_CITY_PROJECT_STATE.md`
2. `docs/departments/COORDINATION.md`
3. its department's `INBOX.md`
4. its department's `STATE.md`
5. its department's `DECISIONS.md`
6. its department's `BACKLOG.md`

Then continue from the recorded state instead of reconstructing the project from chat history.

## Department Files

Each department maintains:

### INBOX.md
Requests, dependencies, and coordinator messages waiting for that department.

Read this at the start of every work session.

### OUTBOX.md
Recent completed handoffs, deliverables, and messages intended for the coordinator or another department.

Keep this concise; durable state belongs elsewhere.

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

## Shared Coordination Board

`docs/departments/COORDINATION.md` is the shared project task board.

It tracks work as:

- ACTIVE
- WAITING
- READY
- REVIEW
- DONE

Departments should update their own inbox/outbox during work. The main coordinator may route those messages and maintain the shared board.

## Minimal Session Protocol

At the start of a department work session:

1. read Project State
2. read Coordination
3. read your Inbox
4. read your State / Decisions / Backlog
5. continue the highest-priority relevant work

Before ending a substantial work session:

1. update State
2. record durable choices in Decisions
3. update Backlog
4. write cross-department results/requests to Outbox or the receiving department's Inbox
5. update Coordination when status materially changed

The human user should normally only need to open a department chat and say:

> **Check your inbox and continue.**

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
