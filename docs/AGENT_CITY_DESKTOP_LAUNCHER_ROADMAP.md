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

Status: **PUBLISHED in v0.9.20**

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

Status: **PUBLISHED in v0.9.21**

Delivered:
- automatic update-availability refresh while Agent City is open
- installation remains user-approved to avoid surprise restarts
- existing backup/stage/update flow retained
- updater waits for the old runtime to exit before replacing files
- failed shutdown aborts replacement rather than touching live program files
- post-update relaunch routes through `agent_city_launcher.pyw`
- direct `main.py` relaunch remains a fallback if the launcher is unavailable
- browser reconnect/reload behavior remains automatic
- update-runner operations log to `data/update_runner.log`

Future unattended auto-install remains an optional later policy choice; it is not enabled by default.

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

Status: **PUBLISHED in v0.9.22**

Delivered:
- persistent single-instance desktop supervisor
- Windows notification-area tray host
- tray status states: Starting / Running / Restarting / Updating / Error / Stopping / Stopped
- tray actions: Open Agent City, Restart Agent City, Quit Agent City
- optional **Start with Windows** toggle using the current-user Windows startup registry
- double-click tray icon opens Agent City
- local launcher shutdown endpoint for controlled Restart/Quit
- update handoff waits for both runtime and old desktop supervisor before replacing files
- new launcher/tray returns after an update
- no new Python dependencies required
- custom ICO path remains `static/assets/app/agent-city.ico`; Windows application icon is used as a safe fallback until Assets supplies the custom art

Deferred intentionally:
- packaged launcher EXE, because the current Python/Windows launcher is working and packaging would add update complexity without a current reliability benefit
- splash screen, because startup is short and a modal startup surface would add clutter rather than useful feedback

Phase 3 functionality is complete. The custom icon remains a presentation-polish follow-up only.

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


## Post-Phase 3 — Ollama companion auto-start

Status: **PUBLISHED in v0.9.25**

Agent City now treats the local Ollama service as part of the one-click desktop experience.

Delivered:
- launcher probes `http://127.0.0.1:11434/api/tags`
- an already-running Ollama instance is reused rather than duplicated
- if Ollama is offline, launcher searches PATH and normal Windows install locations
- `ollama serve` starts hidden with no CMD window
- Ollama output is logged to `data/ollama.log`
- launcher waits for Ollama readiness when possible before opening the city
- tray **Restart Agent City** also re-checks/starts Ollama
- if Ollama is missing or cannot start, Agent City still launches and the existing UI reports Ollama offline

The launcher does not stop an already-running Ollama instance when Agent City quits, because Ollama may be shared with other local applications.
