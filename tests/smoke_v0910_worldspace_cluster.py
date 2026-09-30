from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # Shared-point fan-out belongs to Local 3D world space, not post-projection pixels.
    assert "function localMarkerWorldOffset(item," in js
    assert "const radiusWorld" in js
    assert "world[0] + offset[0]" in js
    assert "world[2] + offset[2]" in js
    assert "localMarkerScreenOffset" not in js

    # Final screen position must be the direct camera projection of the world point.
    assert 'item.element.style.left = projected.x + "px";' in js
    assert 'item.element.style.top = projected.y + "px";' in js
    assert "projected.x + offset.x" not in js
    assert "projected.y + offset.y" not in js

    # The ring remains presentation-only and deterministic around co-located citizens.
    assert "sharesLocalPoint(item, other, 0.5, now)" in js
    assert ".sort((a, b) => String(a.id).localeCompare(String(b.id)))" in js
    assert "Math.cos(angle) * radiusWorld" in js
    assert "Math.sin(angle) * radiusWorld" in js

    # Never write presentation offsets back into Simulation state.
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js
    assert ".x_m =" not in js
    assert ".y_m =" not in js

    print("Agent City v0.9.10 world-space cluster smoke passed.")


if __name__ == "__main__":
    main()
