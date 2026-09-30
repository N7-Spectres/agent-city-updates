from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")

    # Visual travel is derived from a real active Simulation travel job.
    assert "function activeJobFor(citizen)" in js
    assert "citizen.active_job_id" in js
    assert 'String(job.action) !== "travel"' in js
    assert "function citizenRenderMeters(citizen, now = performance.now())" in js
    assert "locationById(citizen.location_id)" in js
    assert "locationById(job.target)" in js
    assert "job.start_minute" in js
    assert "job.end_minute" in js

    # The displayed token interpolates only between authoritative location coordinates.
    assert "Number(from.x_m)" in js
    assert "Number(to.x_m)" in js
    assert "Number(from.y_m)" in js
    assert "Number(to.y_m)" in js
    assert "markerWorld(item, now" in js
    assert "citizenRenderMeters(item.data, now)" in js

    # Motion advances smoothly at the Simulation clock ratio and freezes when paused.
    assert "function continuousSimMinute(now = performance.now())" in js
    assert "state.time_ratio" in js
    assert "if (state.paused) return base;" in js
    assert "stateClockBaseRealMs" in js
    assert "priorEstimate" in js

    # Tokens now participate visually in perspective rather than staying fixed-size HUD stickers.
    assert "function markerPerspectiveScale(item, world, eye)" in js
    assert "vec3Length(vec3Sub(eye, world))" in js
    assert 'style.setProperty("--marker-scale", perspectiveScale.toFixed(3))' in js
    assert "scale(var(--marker-scale, 1))" in css
    assert "transform-origin: center" in css

    # Co-located fan-out now lives in the 3D world plane, so camera projection
    # naturally supplies depth/tilt/zoom behavior.
    assert "function localMarkerWorldOffset(item," in js
    assert "radiusWorld" in js
    assert "world[0] + offset[0]" in js
    assert "world[2] + offset[2]" in js

    # Presentation must never write authoritative citizen coordinates.
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js
    assert ".x_m =" not in js
    assert ".y_m =" not in js

    print("Agent City v0.9.9 3D route-motion smoke passed.")


if __name__ == "__main__":
    main()
