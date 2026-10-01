# Agent City Application Icon

_Last updated: 2026-10-01_

## Canonical runtime asset

`static/assets/app/agent-city.ico`

This one multi-resolution Windows ICO is shared by:

- the Agent City desktop shortcut
- the Windows notification-area / system tray host

Editable design reference:

`static/assets/app/agent-city-source.svg`

## Visual identity

The icon represents **Agent City the application**, not any one citizen.

Design language:
- dark rounded tile for reliable contrast on light and dark Windows UI
- cyan network / city arch
- three-building city silhouette
- warm Agent City gold central tower
- small node cues at larger icon sizes
- transparent outer corners

Palette follows the existing Agent City UI:
- deep tile: `#0C1218`
- cyan: `#64DDEC`
- gold: `#D5A65B`
- ivory: `#EBF2F5`

Tiny frames are deliberately simplified. The 16 px and 24 px images retain the arch + three-tower silhouette while omitting node details that would collapse into noise.

## Included ICO frames

- 16 × 16
- 24 × 24
- 32 × 32
- 48 × 48
- 64 × 64
- 128 × 128
- 256 × 256

Each frame is 32-bit RGBA PNG data inside the ICO container.

## Truth boundary

This is application branding only.

The skyline, arch, nodes, and color hierarchy do **not** establish:
- citizen leadership or rank
- profession or class
- inventory or equipment
- physical capability
- undiscovered locations or resources
- political / organizational authority

No Simulation, Memory, or Communication truth is encoded by the mark.

## Runtime contract

The existing launcher already consumes the canonical path:
- `install_desktop_shortcut.ps1`
- `agent_city_tray.ps1`

No launcher behavior changes are required.
