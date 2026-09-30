from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # The prototype is reachable but isolated from the ordinary app.
    assert '@app.get("/planet-lab")' in main_py
    assert 'STATIC_DIR / "world3d" / "planet_lab.html"' in main_py
    assert 'href="/planet-lab"' in index
    assert "3D Planet Lab" in index
    assert ".primary-tab.prototype-link" in styles

    # No external engine/CDN is required for the first navigation prototype.
    combined = "\n".join((html, css, js))
    assert "https://" not in combined
    assert "http://" not in combined
    assert "three.js" not in combined.lower()
    assert "unpkg" not in combined.lower()
    assert "cdn" not in combined.lower()

    # It is genuinely interactive 3D/WebGL rather than a static concept image.
    assert 'canvas id="world-canvas"' in html
    assert 'getContext("webgl"' in js
    assert "createSphere" in js
    assert "mat4Perspective" in js
    assert "mat4LookAt" in js
    assert 'addEventListener("pointerdown"' in js
    assert 'addEventListener("pointermove"' in js
    assert 'addEventListener("wheel"' in js
    assert 'data-mode="planet"' in html
    assert 'data-mode="region"' in html
    assert 'data-mode="local"' in html

    # The prototype consumes ordinary safe read state and never writes physical state.
    assert 'fetch("/api/state"' in js
    assert 'fetch("/api/visitor/presence?visitor=N7"' in js
    for forbidden in (
        'method: "POST"',
        'method: "PUT"',
        'method: "PATCH"',
        'method: "DELETE"',
        "/api/pause",
        "/api/advance",
        "/api/shared-activities",
    ):
        assert forbidden not in js, forbidden

    # Local mode uses authoritative coordinates already exposed by Simulation.
    assert "position_x_m" in js
    assert "position_y_m" in js
    assert "x_m" in js
    assert "y_m" in js
    assert "localWorld" in js

    # Planet placement is explicitly presentation-only until global geodesy exists.
    assert "presentation shell" in html.lower()
    assert "no global latitude/longitude is claimed yet" in html.lower()
    assert "radiansPerMeter" in js
    assert "anchorLat" in js
    assert "anchorLon" in js

    # Hidden world truth never enters the prototype.
    for forbidden in (
        "planet_seed",
        "generated_deposits",
        "richness",
        "long_axis_m",
        "short_axis_m",
        "orientation_rad",
    ):
        assert forbidden not in js

    # Local view reuses real citizen art and safe current positions.
    assert "/static/assets/citizens/" in js
    assert "state.citizens" in js
    assert "state.structures" in js
    assert "state.routes" in js

    # Accessibility / motion boundaries remain present.
    assert "aria-label" in html
    assert "prefers-reduced-motion" in css
    assert "reduceMotion.matches" in js

    print("Agent City Planet Lab prototype smoke passed.")


if __name__ == "__main__":
    main()
