# World & Simulation — State

_Last updated: 2026-09-28_
_Current release: v0.3.0_

## Mission

Own physical truth.

The LLM may choose intent, but every physical action must be legal, validated, timed, and persisted by the simulation.

## Core Rule

> **The AI may decide intent. The simulation decides reality.**

## Current Time Model

Target chronology:

**1 real hour = 4 simulated hours**

Approximate:

- 6 real hours = 1 simulated day
- 1 real day = 4 simulated days
- 1 real week = 28 simulated days
- about 3 real months = 1 simulated year

Time stops while the app is closed.

Pause freezes simulation time.

## Current Actions

Implemented autonomous actions include:

- travel
- survey
- extract
- deposit cargo
- charge
- wait / observe
- face-to-face citizen talk

Jobs have:

- start minute
- end minute
- duration
- active/completed status
- current activity
- intent reason

## Current Physical State

Citizens track:

- location
- energy
- integrity
- active job
- carried materials

World tracks:

- locations
- routes
- deposits
- survey state
- structures
- settlement stores

Current known starter regions:

- Seed Site
- Northern Ridge
- Rocky Basin
- Southern Flats
- Resin Grove

## Current Starting Infrastructure

- Habitat / Workshop
- Solar Array
- Battery Bank
- Charging Station
- Storage Unit
- Basic Workbench
- Crude Smelter

## Current Starting Resources

- Processed structural material
- Conductive wire
- Mechanical components
- Lubricant
- Fasteners
- Battery cells
- Basic electronics

## Current Discovery Model

Surveying can confirm deposits.

Discoveries record who personally discovered them.

The UI may show settlement-confirmed deposits, while citizen prompts should respect individual information boundaries.

## Current Visitor Physics

v0.3.0 gives visitors physical presence and travel duration.

Visitor travel uses the world clock and known routes.

Face-to-face interaction obeys physical location.
