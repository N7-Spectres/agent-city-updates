from __future__ import annotations

import sqlite3
from pathlib import Path

from agent_city.spatial import public_terrain_heightfield

ROOT = Path(__file__).resolve().parents[1]


def make_conn(seed: str = "mesh-seed-a") -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.execute(
        "CREATE TABLE locations (id TEXT PRIMARY KEY, x_m REAL, y_m REAL)"
    )
    conn.execute(
        "INSERT INTO meta(key, value) VALUES ('planet_seed', ?)",
        (seed,),
    )
    conn.execute(
        "INSERT INTO locations(id, x_m, y_m) VALUES ('seed_site', 125.0, -75.0)"
    )
    return conn


def main() -> None:
    with make_conn() as conn:
        first = public_terrain_heightfield(
            conn,
            radius_m=3250.0,
            resolution=41,
        )
        second = public_terrain_heightfield(
            conn,
            radius_m=3250.0,
            resolution=41,
        )

    assert first == second
    assert first["frame_id"] == "seed_site_local"
    assert first["center_x_m"] == 125.0
    assert first["center_y_m"] == -75.0
    assert first["radius_m"] == 3250.0
    assert first["resolution"] == 41
    assert len(first["heights_m"]) == 41 * 41
    assert first["discovery_boundary"] == "surface_only_no_geology_or_deposits"
    assert first["elevation_quantization_m"] == 2.0
    assert all(abs((height / 2.0) - round(height / 2.0)) < 1e-9 for height in first["heights_m"])

    # Different world seeds must produce a different stable visual terrain.
    with make_conn("mesh-seed-b") as conn:
        different = public_terrain_heightfield(
            conn,
            radius_m=3250.0,
            resolution=41,
        )
    assert different["heights_m"] != first["heights_m"]

    # Public mesh output must never contain hidden prospecting truth.
    forbidden_keys = {
        "planet_seed",
        "geology_class",
        "material",
        "richness",
        "generated_deposits",
        "deposit_bodies",
        "long_axis_m",
        "short_axis_m",
        "angle_rad",
    }
    assert not (forbidden_keys & set(first))

    # Clamp and odd-grid behavior keep request cost bounded.
    with make_conn() as conn:
        clamped = public_terrain_heightfield(
            conn,
            radius_m=99999.0,
            resolution=48,
        )
    assert clamped["radius_m"] == 4200.0
    assert clamped["resolution"] == 49
    assert len(clamped["heights_m"]) == 49 * 49

    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")

    assert 'from agent_city.spatial import public_terrain_heightfield' in main_py
    assert '@app.get("/api/world/local-terrain")' in main_py
    assert "public_terrain_heightfield(" in main_py

    # The client receives only the safe surface payload, never the private seed.
    assert 'fetch(' in js
    assert '"/api/world/local-terrain?radius_m="' in js
    for forbidden in (
        "planet_seed",
        "generated_deposits",
        "richness",
        "long_axis_m",
        "short_axis_m",
        "angle_rad",
        "geology_class",
    ):
        assert forbidden not in js, forbidden

    # Actual WebGL terrain triangles + wire mesh replace the flat plane when
    # available, while the old plane remains as a safe fallback.
    assert "let localTerrainBuffer = null;" in js
    assert "let localTerrainWireBuffer = null;" in js
    assert "function rebuildLocalTerrain(payload)" in js
    assert "triangles.push(" in js
    assert "wires.push(" in js
    assert "gl.TRIANGLES" in js
    assert "localPlane.buffer" in js
    assert "Seeded Local terrain unavailable; using flat fallback." in js

    # Terrain has more breathing room than the old +/-3 local square.
    assert "const LOCAL_SURFACE_HALF_EXTENT = 3.45;" in js
    assert "const LOCAL_TERRAIN_PADDING_FACTOR = 1.55;" in js
    assert "distance: 4.85" in js
    assert 'if (mode === "local") return 10.5;' in js

    # Markers and routes are grounded on the surface instead of staying flat.
    assert "function terrainHeightMetersAt(xMeters, yMeters)" in js
    assert "function terrainWorldHeightAt(xMeters, yMeters)" in js
    assert "terrainWorldHeightAt(xMeters, yMeters) + offset" in js
    assert "const segments = clamp(Math.ceil(distanceMeters / 140), 8, 32);" in js
    assert "rebuildLocalRoutes();" in js

    assert "private world seed" in html
    assert "hidden deposit geometry" in html

    print("Agent City v1.1.0 seeded Local terrain mesh smoke passed.")


if __name__ == "__main__":
    main()
