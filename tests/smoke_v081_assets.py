from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CITIZENS = ("aris", "bex", "cato", "iri", "noma", "vale")


def assert_webp(path: Path, expected_size: tuple[int, int] | None = None) -> None:
    data = path.read_bytes()
    assert len(data) > 1000, f"{path} is unexpectedly small"
    assert data[:4] == b"RIFF", f"{path} is not RIFF"
    assert data[8:12] == b"WEBP", f"{path} is not WebP"


def main() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    # DOM contract remains clean.
    html_ids = re.findall(r'id="([^"]+)"', html)
    js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert len(html_ids) == len(set(html_ids)), "duplicate HTML IDs"
    assert js_ids <= set(html_ids), sorted(js_ids - set(html_ids))

    # Map zoom/readability controls are visible and presentation-only.
    for node_id in ("map-zoom-in", "map-zoom-out", "map-zoom-reset", "map-zoom-label"):
        assert f'id="{node_id}"' in html
        camel = {
            "map-zoom-in": "mapZoomIn",
            "map-zoom-out": "mapZoomOut",
            "map-zoom-reset": "mapZoomReset",
            "map-zoom-label": "mapZoomLabel",
        }[node_id]
        assert f'{camel}: document.getElementById("{node_id}")' in js

    assert "let mapZoomLevel = 1" in js
    assert "let mapCenterOverride = null" in js
    assert "MAP_ZOOM_MIN" in js and "MAP_ZOOM_MAX" in js
    assert "function setMapZoom" in js
    assert "window.focusMapLocation" in js
    assert "mapCenterOverride = x != null && y != null" in js
    assert "scalePxPerMeter: Math.max(0.0001, scale * mapZoomLevel)" in js
    assert "mapZoomLevel = 1" in js
    assert "mapCenterOverride = null" in js

    # Zoom/focus must not call any physical write endpoint or mutate state coordinates.
    zoom_slice = js[js.index("function updateMapZoomLabel"):js.index('window.focusLocation = function')]
    assert "fetch(" not in zoom_slice
    assert "position_x_m =" not in zoom_slice
    assert "position_y_m =" not in zoom_slice
    assert "/api/" not in zoom_slice

    # Keep the generous hit target, but never paint its rectangle.
    assert ".map-node {" in css
    assert "width: 132px" in css
    assert "min-height: 56px" in css
    focus_block = css[css.index(".map-node:hover,"):css.index(".node-dot,")]
    assert "border-color: transparent" in focus_block
    assert "background: transparent" in focus_block
    assert ".map-node:focus-visible .node-dot" in focus_block
    assert ".map-node:focus-visible .node-label" in focus_block
    assert "box-shadow:" in focus_block
    assert "prefers-reduced-motion" in css

    # All six approved base bodies + head tokens are real runtime assets.
    for citizen in CITIZENS:
        full_rel = f"static/assets/citizens/{citizen}/full.webp"
        token_rel = f"static/assets/citizens/{citizen}/token.webp"
        assert_webp(ROOT / full_rel)
        assert_webp(ROOT / token_rel)

        full_url = f"/static/assets/citizens/{citizen}/full.webp"
        token_url = f"/static/assets/citizens/{citizen}/token.webp"
        assert f'full: "{full_url}"' in js
        assert f'bust: "{token_url}"' in js
        assert f'token: "{token_url}"' in js

    # Optional equipment and unapproved expression frames remain absent.
    assert js.count("equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] }") == 6
    assert js.count("neutral: null") == 6
    assert js.count("blink: null") == 6
    assert js.count("happy: null") == 6
    assert js.count("focused: null") == 6
    assert js.count("curious: null") == 6

    # Full-body art must fit without cropping; tokens may crop to the face.
    assert ".avatar-full.has-image .avatar-image" in css
    assert "object-fit: contain" in css
    assert ".avatar-token.has-image .avatar-image" in css
    assert "object-fit: cover" in css

    # The sheet copy now describes approved identity, not a placeholder.
    assert "Approved base-body identity" in html
    assert "interface fallback until unique art is supplied" not in html

    # Hotfix remains visual-only and cannot expose hidden seeded truth.
    for forbidden in (
        "planet_seed",
        "generated_deposits",
        "center_x_m",
        "long_axis_m",
        "short_axis_m",
        "richness",
    ):
        assert forbidden not in js

    print("Agent City v0.8.1 citizen-art/map hotfix smoke passed.")


if __name__ == "__main__":
    main()
