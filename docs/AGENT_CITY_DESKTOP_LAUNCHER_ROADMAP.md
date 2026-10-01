# Agent City Desktop Launcher Roadmap

_Last updated: 2026-10-01_

## Goal

Agent City should feel like a normal local desktop application:

- one desktop icon starts or reopens it
- no persistent Command Prompt window is required
- the browser opens automatically once the local server is ready
- later updates can install and restart cleanly
- later polish may add tray/status behavior without changing Simulation authority

## Phase 1 — One-click hidden launch

Status: **IMPLEMENTATION IN PROGRESS for v0.9.20**

Target behavior:

- Windows desktop shortcut named **Agent City**
- shortcut launches through `pythonw.exe`, avoiding a visible CMD window
- launcher checks `http://127.0.0.1:8000/api/state`
- if Agent City is already running, do not start a duplicate server; just open the browser
- if it is not running, start `main.py` without a console window
- wait for the local API to become ready before opening the browser
- write launcher/server failures to local logs under `data/`
- provide a one-time shortcut setup helper
- reserve a stable custom icon path:
  `static/assets/app/agent-city.ico`

Phase 1 deliberately does **not** add:
- automatic update installation
- automatic restart after update
- tray icon/process manager
- Windows-startup launch
- background update polling

## Phase 2 — Managed update + relaunch

Planned after Phase 1 is proven locally.

Desired behavior:

- launcher becomes the stable parent/supervisor for the Agent City runtime
- reuse the existing update manifest/feed and current `update_runner.py`
- when a user-approved or configured update is installed:
  1. stage and verify the update
  2. stop the Agent City runtime cleanly
  3. preserve world data/backups
  4. replace program files
  5. relaunch the runtime automatically
  6. reopen or refresh the Agent City browser surface
- avoid duplicate processes or ports
- failed update/restart must leave useful logs and preserve rollback/backups
- never turn update plumbing into Simulation authority

Open design choice:
- whether updates remain explicitly user-triggered from the Updates UI or can be configured for automatic install after a green published release.

## Phase 3 — Desktop polish

Planned only after Phase 2 is stable.

Possible scope:

- system tray icon
- status states such as Starting / Running / Updating / Restarting / Error
- tray actions: Open Agent City, Restart, Quit
- optional launch-at-Windows-startup preference
- polished splash/startup state if startup delay is noticeable
- custom desktop/tray icon set from Assets
- packaged launcher executable if replacing the Python shortcut provides meaningful reliability/distribution benefits

Do not add decorative complexity unless it improves actual local operation.

## Assets contract

Assets owns presentation only.

Requested future icon:
- canonical path: `static/assets/app/agent-city.ico`
- Windows multi-size ICO preferred (16, 24, 32, 48, 64, 128, 256)
- should remain identifiable at tiny tray/shortcut sizes
- icon creates no world fact, role, equipment, or capability

## Architecture boundary

The launcher may:
- start/stop/reopen the local application process
- check application readiness
- orchestrate update/restart mechanics
- expose operational status

The launcher may **not**:
- edit citizen/world state as part of startup
- create Simulation actions
- repair citizens/resources/world state
- bypass normal persistence or update validation

The city remains autonomous whether launched from CMD, launcher, or future packaged app.
