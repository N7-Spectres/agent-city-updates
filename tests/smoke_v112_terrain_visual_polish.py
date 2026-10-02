from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    lab_html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")

    assert "let localTerrainHighlightBuffer = null;" in js
    assert "let localTerrainShadowBuffer = null;" in js
    assert "const highElevationThreshold = minElevation + elevationRange * 0.63;" in js
    assert "const steepSlopeThreshold = 0.045;" in js
    assert "averageElevation >= highElevationThreshold" in js
    assert "slopeRatio >= steepSlopeThreshold" in js

    assert "const minorStride = 2;" in js
    assert "const majorStride = 6;" in js
    assert "let localTerrainMajorWireBuffer = null;" in js

    assert "function rebuildLocalLocationPads()" in js
    assert "for (const location of knownLocations())" in js
    assert "const padRadiusMeters = clamp(localFrame.metersPerWorld * 0.105, 52, 110);" in js
    assert "const center = localWorld(xMeters, yMeters, 0.010);" in js
    assert "const edge = localWorld(x, y, 0.012);" in js
    assert "localLocationPadBuffer" in js
    assert "localLocationPadRingBuffer" in js

    assert "--home-panel-height: clamp(740px, calc(100vh - 168px), 890px);" in css
    assert "build=1.1.2" in index
    assert "build=1.1.2" in lab_html

    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    print("Agent City v1.1.2 terrain visual polish smoke passed.")


if __name__ == "__main__":
    main()
