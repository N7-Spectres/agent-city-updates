from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    placement_start = js.index("function citizenMapPlacement(citizen)")
    spatial_branch = js.index("if (spatialViewport && x != null && y != null)", placement_start)
    route_branch = js.index('if (job?.action === "travel")', placement_start)
    assert route_branch < spatial_branch

    assert "const progress = jobProgress(job);" in js
    assert "pos: interpolatedPosition(citizen.location_id, job.target, fraction)" in js
    assert "routeDistanceKm * (1 - fraction)" in js
    assert 'class="map-travel-progress"' in js
    assert "km remaining" in js
    assert ".map-travel-progress {" in css

    print("Agent City v0.8.7 route-token travel visualization smoke passed.")


if __name__ == "__main__":
    main()
