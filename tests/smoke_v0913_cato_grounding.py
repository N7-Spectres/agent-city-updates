from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # Cato remains the same presentation-only sprite-body pilot.
    assert 'kind: "sprite_body"' in js
    assert 'baseBody: "/static/assets/citizens/cato/world/front.webp"' in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    # Ground anchor is tightened toward the feet and the body gets modestly
    # more screen presence without introducing any physical dimensions.
    assert "width: 58px;" in css
    assert "height: 116px;" in css
    assert "translate(-50%, -97%)" in css
    assert "transform-origin: 50% 97%;" in css

    # Ground contact has its own presentation ring + shadow.
    assert ".cato-world-body::before" in css
    assert ".cato-world-body::after" in css
    assert ".cato-world-body.selected::before" in css
    assert ".cato-world-body:hover::before" in css

    # Real route travel may animate presentation, but the heavier body stays
    # visually planted and the shadow reacts with the same cadence.
    assert ".cato-world-body.route-traveling::after" in css
    assert "@keyframes cato-world-travel-shadow" in css
    assert "translateY(-1.4px)" in css

    # Reduced-motion users receive a static body and static ground shadow.
    assert ".cato-world-body.route-traveling .world-body-image," in css
    assert ".cato-world-body.route-traveling::after" in css
    assert "animation: none !important;" in css

    print("Agent City v0.9.13 Cato grounding smoke passed.")


if __name__ == "__main__":
    main()
