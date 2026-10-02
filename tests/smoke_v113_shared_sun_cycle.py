from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

    # One shared, continuous sim-time sun drives all three world scales.
    assert "function solarLighting(now = performance.now())" in js
    assert "state ? continuousSimMinute(now) : 720" in js
    assert "const localDirection = vec3Normalize([" in js
    assert "const globeDirection = vec3Normalize([" in js
    assert "east[0] * localDirection[0]" in js
    assert "up[0] * localDirection[1]" in js
    assert "north[0] * localDirection[2]" in js

    # Dawn/day/dusk/night remain presentation states only.
    assert "function visualDayPhase(simMinute)" in js
    assert "document.body.dataset.dayPhase = lighting.phase;" in js
    assert '"dawn light"' in js
    assert '"daylight"' in js
    assert '"dusk light"' in js
    assert '"night"' in js

    # Planet/Region use a real soft-terminator lit shader.
    assert 'uniform vec3 uLightDir;' in js
    assert 'uniform vec3 uSunColor;' in js
    assert 'uniform vec3 uNightColor;' in js
    assert 'uniform float uTerminatorWidth;' in js
    assert 'float incidence = dot(n, normalize(uLightDir));' in js
    assert 'float dayMask = smoothstep(-uTerminatorWidth, uTerminatorWidth, incidence);' in js
    assert "lighting.globeDirection" in js
    assert 'mode === "region" ? 0.11 : 0.075' in js

    # Local terrain has actual surface normals and uses the same moving sun.
    assert "let localTerrainNormalBuffer = null;" in js
    assert "const normals = [];" in js
    assert "const addLitTriangle = (p0, p1, p2) =>" in js
    assert "localTerrainNormalBuffer = createBuffer(normals);" in js
    assert "bindLitArrayBuffer(" in js
    assert "lightDir: lighting.localDirection" in js

    # Marker/label readability remains independent of world shading.
    assert "updateMarkers(matrix, now);" in js
    assert "markerLayer" in js

    # Captions make the active lighting state explicit across Local/Region/Planet.
    assert '"Planet globe • shared sun • "' in js
    assert '"Regional globe • shared sun • "' in js
    assert '"Seeded terrain mesh • " + localSurfaceStatus + " • "' in js

    # Fresh build keys prevent the new lighting code from being hidden by an old iframe.
    assert "build=1.1.3" in index
    assert "build=1.1.3" in html

    # Lighting remains presentation-only.
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    print("Agent City v1.1.3 shared sun/day-night cycle smoke passed.")


if __name__ == "__main__":
    main()
