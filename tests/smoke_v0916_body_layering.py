from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # Full-body citizens use the shared body class created by the Local renderer.
    assert '"citizen-world-body"' in js
    assert 'String(item.id) + "-world-body"' in js

    # Bodies must render above ordinary token/location markers (default z-index 12)
    # so a walking body cannot disappear under a crowded Seed Site token cluster.
    assert ".citizen-marker.citizen-world-body {" in css
    assert "z-index: 23;" in css

    # Visitor stays readable at z-index 24, but an explicitly selected/hovered body
    # rises one layer higher for inspection.
    assert ".visitor-marker {" in css
    assert "z-index: 24;" in css
    assert ".citizen-marker.citizen-world-body.selected," in css
    assert "z-index: 25;" in css

    # No physical state mutation is introduced by this presentation-only fix.
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    print("Agent City v0.9.16 body-layering smoke passed.")


if __name__ == "__main__":
    main()
