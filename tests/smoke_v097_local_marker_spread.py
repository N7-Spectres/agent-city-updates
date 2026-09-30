from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")

    # Co-located citizens fan out in screen space only.
    assert "function markerMeterPoint(item," in js
    assert "function sharesLocalPoint(a, b, toleranceMeters = 0.5" in js
    assert "function localMarkerScreenOffset(item," in js
    assert 'other.type === "citizen" && sharesLocalPoint(item, other' in js
    assert "const radius = clamp(54 + colocated.length * 7, 64, 92)" in js
    assert "projected.x + offset.x" in js
    assert "projected.y + offset.y" in js

    # The visitor is pushed farther below a crowded shared point.
    assert "return { x: 0, y: citizenRadius +" in js

    # Physical coordinates remain authoritative inputs; the spread is not written back.
    assert "position_x_m" in js
    assert "position_y_m" in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js
    assert ".x_m =" not in js
    assert ".y_m =" not in js

    # Hover/focus can bring a token forward without changing physical state.
    assert ".citizen-marker:hover" in css
    assert ".citizen-marker:focus-visible" in css

    print("Agent City v0.9.7 Local marker spread smoke passed.")


if __name__ == "__main__":
    main()
