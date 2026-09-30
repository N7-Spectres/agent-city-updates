from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    lab_html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")
    lab_css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    lab_js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # Home is 3D-first, not merely linked to a separate lab page.
    assert "<h2>Live local world</h2>" in index
    assert 'id="home-world-stage"' in index
    assert 'id="home-world-3d"' in index
    assert 'src="/planet-lab?embed=1&mode=local"' in index
    assert 'id="world-view-fallback-toggle"' in index
    assert "2D fallback" in index

    # Legacy 2D map remains present only as a deliberate fallback.
    assert 'id="route-layer"' in index
    assert 'id="map-layer"' in index
    assert ".world-stage-3d:not(.show-legacy-map) > .map-layer" in styles
    assert ".world-stage-3d.show-legacy-map .home-world-3d" in styles

    # Embedded Planet Lab removes full-page chrome but keeps Local/Region/Planet controls.
    assert 'data-mode="planet"' in lab_html
    assert 'data-mode="region"' in lab_html
    assert 'data-mode="local"' in lab_html
    assert 'query.get("embed") === "1"' in lab_js
    assert 'query.get("mode")' in lab_js
    assert 'let mode = initialMode;' in lab_js
    assert "body.embedded .lab-topbar" in lab_css
    assert "body.embedded .left-panel" in lab_css
    assert "body.embedded .right-panel" in lab_css

    # Clicking a citizen in embedded 3D hands selection back to Home.
    assert '"agent-city-world-select"' in lab_js
    assert 'entityType: "citizen"' in lab_js
    assert "window.parent.postMessage" in lab_js
    assert 'message.type === "agent-city-world-select"' in index
    assert 'typeof window.selectCitizen === "function"' in index

    # The local renderer mirrors the same simulation-time day phases as Home.
    for phase in ("dawn", "day", "dusk", "night"):
        assert phase in lab_js
    assert "function visualDayPhase(simMinute)" in lab_js
    assert "function localPalette()" in lab_js
    assert "document.body.dataset.dayPhase = visualDayPhase(state.sim_minute)" in lab_js

    # Integration remains read-only from the 3D world surface.
    for forbidden in (
        'method: "POST"',
        'method: "PUT"',
        'method: "PATCH"',
        'method: "DELETE"',
    ):
        assert forbidden not in lab_js, forbidden

    print("Agent City v0.9.6 Home 3D world integration smoke passed.")


if __name__ == "__main__":
    main()
