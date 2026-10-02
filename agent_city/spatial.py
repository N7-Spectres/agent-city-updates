from __future__ import annotations

import hashlib
import math
from typing import Any

CHUNK_SIZE_M = 160.0
TERRAIN_NOISE_SCALE_M = 320.0
PUBLIC_TERRAIN_MIN_RADIUS_M = 800.0
PUBLIC_TERRAIN_MAX_RADIUS_M = 4200.0
PUBLIC_TERRAIN_MIN_RESOLUTION = 17
PUBLIC_TERRAIN_MAX_RESOLUTION = 49
PUBLIC_TERRAIN_ELEVATION_QUANTIZATION_M = 2.0
SPATIAL_FRAME_ID = "seed_site_local"

MATERIAL_FIELDS = (
    ("Ferrite Stone", "ferric"),
    ("Veyra Ore", "veyra"),
    ("Silicate", "silicate"),
    ("Copper-like Ore", "conductive"),
    ("Carbonaceous Rock", "carbon"),
    ("Clay", "clay"),
    ("Plant Fiber", "fiber"),
    ("Native Resin", "resin"),
)


def _hash_bytes(seed: str, namespace: str, *parts: object) -> bytes:
    payload = "|".join([seed, namespace, *(str(part) for part in parts)])
    return hashlib.sha256(payload.encode("utf-8")).digest()


def _u01(seed: str, namespace: str, *parts: object) -> float:
    raw = int.from_bytes(_hash_bytes(seed, namespace, *parts)[:8], "big")
    return raw / float(2**64 - 1)


def _stable_id(seed: str, namespace: str, *parts: object, prefix: str) -> str:
    digest = hashlib.sha256(
        "|".join([seed, namespace, *(str(part) for part in parts)]).encode("utf-8")
    ).hexdigest()
    return f"{prefix}_{digest[:20]}"


def _smooth(value: float) -> float:
    return value * value * (3.0 - 2.0 * value)


def _value_noise(seed: str, namespace: str, x_m: float, y_m: float, scale_m: float) -> float:
    gx = math.floor(x_m / scale_m)
    gy = math.floor(y_m / scale_m)
    tx = _smooth((x_m / scale_m) - gx)
    ty = _smooth((y_m / scale_m) - gy)

    n00 = _u01(seed, namespace, gx, gy)
    n10 = _u01(seed, namespace, gx + 1, gy)
    n01 = _u01(seed, namespace, gx, gy + 1)
    n11 = _u01(seed, namespace, gx + 1, gy + 1)

    nx0 = n00 + (n10 - n00) * tx
    nx1 = n01 + (n11 - n01) * tx
    return nx0 + (nx1 - nx0) * ty


def _planet_seed(conn) -> str:
    row = conn.execute("SELECT value FROM meta WHERE key = 'planet_seed'").fetchone()
    if not row:
        raise RuntimeError("Planet seed is not initialized.")
    return str(row["value"])


def chunk_for_coordinate(x_m: float, y_m: float) -> tuple[int, int]:
    return (math.floor(x_m / CHUNK_SIZE_M), math.floor(y_m / CHUNK_SIZE_M))


def _elevation_at(seed: str, x_m: float, y_m: float) -> float:
    """
    Deterministic elevation shared by Simulation terrain queries and the coarse
    Local presentation mesh.

    This helper intentionally contains no geology/deposit logic. Keeping the
    surface calculation separate lets the UI receive broad topography without
    exposing material fields, richness, hidden body geometry, or the seed.
    """
    broad = _value_noise(seed, "terrain_broad", x_m, y_m, TERRAIN_NOISE_SCALE_M * 2.0)
    local = _value_noise(seed, "terrain_local", x_m, y_m, TERRAIN_NOISE_SCALE_M)
    return (broad - 0.5) * 70.0 + (local - 0.5) * 24.0


def _terrain_at(seed: str, x_m: float, y_m: float) -> dict[str, Any]:
    rough = _value_noise(seed, "terrain_rough", x_m, y_m, 120.0)
    moisture = _value_noise(seed, "surface_moisture", x_m, y_m, 420.0)

    elevation_m = round(_elevation_at(seed, x_m, y_m), 3)
    roughness = round(rough, 5)

    if rough > 0.72:
        terrain_class = "broken"
    elif elevation_m > 22:
        terrain_class = "ridge"
    elif elevation_m < -18:
        terrain_class = "basin"
    elif moisture > 0.68:
        terrain_class = "low_growth"
    else:
        terrain_class = "open_ground"

    geology_scores = {
        key: _value_noise(seed, f"geology_{key}", x_m, y_m, 520.0)
        for _, key in MATERIAL_FIELDS
    }
    geology_class = max(geology_scores.items(), key=lambda item: item[1])[0]

    return {
        "elevation_m": elevation_m,
        "roughness": roughness,
        "terrain_class": terrain_class,
        "geology_class": geology_class,
    }


def public_terrain_heightfield(
    conn,
    *,
    radius_m: float = 3200.0,
    resolution: int = 41,
) -> dict[str, Any]:
    """
    Return a coarse, seed-stable elevation field for the Local 3D renderer.

    This is deliberately narrower than query_hidden_world():
    - the planet seed never leaves the server;
    - no geology/material score is calculated or returned;
    - no deposit candidate is materialized or exposed;
    - elevations are spatially coarse and vertically quantized for presentation.

    The mesh therefore follows the same broad seeded topography as Simulation
    without becoming a free prospecting/scanning endpoint.
    """
    seed = _planet_seed(conn)

    requested_radius = float(radius_m)
    radius = max(
        PUBLIC_TERRAIN_MIN_RADIUS_M,
        min(PUBLIC_TERRAIN_MAX_RADIUS_M, requested_radius),
    )

    requested_resolution = int(resolution)
    grid = max(
        PUBLIC_TERRAIN_MIN_RESOLUTION,
        min(PUBLIC_TERRAIN_MAX_RESOLUTION, requested_resolution),
    )
    if grid % 2 == 0:
        grid = grid + 1 if grid < PUBLIC_TERRAIN_MAX_RESOLUTION else grid - 1

    seed_site = conn.execute(
        "SELECT x_m, y_m FROM locations WHERE id = 'seed_site'"
    ).fetchone()
    center_x = float(seed_site["x_m"] or 0.0) if seed_site else 0.0
    center_y = float(seed_site["y_m"] or 0.0) if seed_site else 0.0
    spacing = (radius * 2.0) / float(grid - 1)
    quant = PUBLIC_TERRAIN_ELEVATION_QUANTIZATION_M

    heights: list[float] = []
    minimum = float("inf")
    maximum = float("-inf")

    # Row 0 is north (+y), column 0 is west (-x).
    for row in range(grid):
        y_m = center_y + radius - (row * spacing)
        for column in range(grid):
            x_m = center_x - radius + (column * spacing)
            raw = _elevation_at(seed, x_m, y_m)
            display_elevation = round(raw / quant) * quant
            display_elevation = round(display_elevation, 3)
            heights.append(display_elevation)
            minimum = min(minimum, display_elevation)
            maximum = max(maximum, display_elevation)

    return {
        "frame_id": SPATIAL_FRAME_ID,
        "center_x_m": round(center_x, 4),
        "center_y_m": round(center_y, 4),
        "radius_m": round(radius, 3),
        "resolution": grid,
        "sample_spacing_m": round(spacing, 3),
        "elevation_quantization_m": quant,
        "min_elevation_m": minimum,
        "max_elevation_m": maximum,
        "heights_m": heights,
        "discovery_boundary": "surface_only_no_geology_or_deposits",
    }


def _candidate_body(seed: str, chunk_x: int, chunk_y: int, slot: int) -> dict[str, Any] | None:
    presence = _u01(seed, "deposit_presence", chunk_x, chunk_y, slot)
    threshold = 0.44 if slot == 0 else 0.79
    if presence < threshold:
        return None

    chunk_origin_x = chunk_x * CHUNK_SIZE_M
    chunk_origin_y = chunk_y * CHUNK_SIZE_M
    center_x = chunk_origin_x + CHUNK_SIZE_M * (0.15 + 0.70 * _u01(seed, "deposit_x", chunk_x, chunk_y, slot))
    center_y = chunk_origin_y + CHUNK_SIZE_M * (0.15 + 0.70 * _u01(seed, "deposit_y", chunk_x, chunk_y, slot))

    geology_scores = [
        (
            material,
            _value_noise(seed, f"geology_{field}", center_x, center_y, 520.0)
            + (_u01(seed, "deposit_material_bias", chunk_x, chunk_y, slot, field) - 0.5) * 0.10,
        )
        for material, field in MATERIAL_FIELDS
    ]
    material = max(geology_scores, key=lambda item: item[1])[0]

    radius_m = 22.0 + 58.0 * _u01(seed, "deposit_radius", chunk_x, chunk_y, slot)
    long_axis_m = radius_m * (1.15 + 0.85 * _u01(seed, "deposit_long_axis", chunk_x, chunk_y, slot))
    short_axis_m = radius_m * (0.55 + 0.35 * _u01(seed, "deposit_short_axis", chunk_x, chunk_y, slot))
    angle_rad = math.tau * _u01(seed, "deposit_angle", chunk_x, chunk_y, slot)
    richness = 0.25 + 0.75 * _u01(seed, "deposit_richness", chunk_x, chunk_y, slot)

    return {
        "id": _stable_id(seed, "deposit", chunk_x, chunk_y, slot, prefix="gdep"),
        "source_kind": "procedural",
        "material": material,
        "source_chunk_x": chunk_x,
        "source_chunk_y": chunk_y,
        "center_x_m": round(center_x, 4),
        "center_y_m": round(center_y, 4),
        "long_axis_m": round(long_axis_m, 4),
        "short_axis_m": round(short_axis_m, 4),
        "angle_rad": round(angle_rad, 7),
        "richness": round(richness, 6),
    }


def legacy_body_geometry(
    seed: str,
    deposit_id: str,
    material: str,
    anchor_x_m: float,
    anchor_y_m: float,
) -> dict[str, Any]:
    """
    Give a pre-v0.8 named deposit deterministic local geometry around its legacy
    landmark without changing its existing stable deposit ID.
    """
    offset_radius = 22.0 + 42.0 * _u01(seed, "legacy_offset_radius", deposit_id)
    offset_angle = math.tau * _u01(seed, "legacy_offset_angle", deposit_id)
    center_x = float(anchor_x_m) + math.cos(offset_angle) * offset_radius
    center_y = float(anchor_y_m) + math.sin(offset_angle) * offset_radius
    base = 32.0 + 38.0 * _u01(seed, "legacy_radius", deposit_id)
    return {
        "id": str(deposit_id),
        "source_kind": "legacy",
        "material": str(material),
        "source_chunk_x": chunk_for_coordinate(center_x, center_y)[0],
        "source_chunk_y": chunk_for_coordinate(center_x, center_y)[1],
        "center_x_m": round(center_x, 4),
        "center_y_m": round(center_y, 4),
        "long_axis_m": round(base * (1.20 + 0.45 * _u01(seed, "legacy_long", deposit_id)), 4),
        "short_axis_m": round(base * (0.62 + 0.25 * _u01(seed, "legacy_short", deposit_id)), 4),
        "angle_rad": round(math.tau * _u01(seed, "legacy_angle", deposit_id), 7),
        "richness": round(0.45 + 0.45 * _u01(seed, "legacy_richness", deposit_id), 6),
    }


def _inside_body(body: dict[str, Any], x_m: float, y_m: float) -> bool:
    dx = x_m - float(body["center_x_m"])
    dy = y_m - float(body["center_y_m"])
    angle = float(body["angle_rad"])
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    local_x = dx * cos_a + dy * sin_a
    local_y = -dx * sin_a + dy * cos_a
    long_axis = max(1.0, float(body["long_axis_m"]))
    short_axis = max(1.0, float(body["short_axis_m"]))
    return (local_x / long_axis) ** 2 + (local_y / short_axis) ** 2 <= 1.0


def _materialize_body(conn, body: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO generated_deposits
        (id, source_kind, material, source_chunk_x, source_chunk_y, center_x_m, center_y_m,
         long_axis_m, short_axis_m, angle_rad, richness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            body["id"],
            body.get("source_kind", "procedural"),
            body["material"],
            body["source_chunk_x"],
            body["source_chunk_y"],
            body["center_x_m"],
            body["center_y_m"],
            body["long_axis_m"],
            body["short_axis_m"],
            body["angle_rad"],
            body["richness"],
        ),
    )


def query_hidden_world(conn, x_m: float, y_m: float) -> dict[str, Any]:
    """
    Authoritative hidden-world query.

    This function may be called by Simulation-owned future survey/scanner/shared-
    exploration actions. Its result is hidden truth and must not be passed
    directly to UI/LLM surfaces.
    """
    seed = _planet_seed(conn)
    x_m = float(x_m)
    y_m = float(y_m)
    chunk_x, chunk_y = chunk_for_coordinate(x_m, y_m)

    # Materialize procedural candidates in neighboring source chunks so an
    # ellipse crossing a chunk edge keeps one identity from either side.
    for source_x in range(chunk_x - 1, chunk_x + 2):
        for source_y in range(chunk_y - 1, chunk_y + 2):
            for slot in (0, 1):
                body = _candidate_body(seed, source_x, source_y, slot)
                if body:
                    _materialize_body(conn, body)

    # Read all persisted bodies that could plausibly cover this point. This
    # includes deterministic legacy bodies anchored around pre-v0.8 landmarks.
    rows = conn.execute(
        """
        SELECT *
        FROM generated_deposits
        WHERE center_x_m BETWEEN ? AND ?
          AND center_y_m BETWEEN ? AND ?
        ORDER BY id
        """,
        (
            x_m - CHUNK_SIZE_M,
            x_m + CHUNK_SIZE_M,
            y_m - CHUNK_SIZE_M,
            y_m + CHUNK_SIZE_M,
        ),
    ).fetchall()
    bodies = [dict(row) for row in rows if _inside_body(dict(row), x_m, y_m)]
    terrain = _terrain_at(seed, x_m, y_m)
    return {
        "frame_id": SPATIAL_FRAME_ID,
        "x_m": round(x_m, 4),
        "y_m": round(y_m, 4),
        "chunk_x": chunk_x,
        "chunk_y": chunk_y,
        **terrain,
        "deposit_bodies": bodies,
    }


def record_validated_observation(
    conn,
    *,
    observer_id: str,
    x_m: float,
    y_m: float,
    observed_minute: int,
    source_job_id: int | None = None,
    observation_kind: str = "field_observation",
    radius_m: float = 1.0,
    detail_level: str = "field",
) -> int:
    """
    Convert a hidden query into one safe, persisted physical observation.

    The observation reveals only what was validated at the queried point. It does
    not expose planet seed, hidden richness, or full hidden deposit geometry.
    """
    hidden = query_hidden_world(conn, x_m, y_m)
    primary = hidden["deposit_bodies"][0] if hidden["deposit_bodies"] else None

    baseline = detail_level == "baseline"
    summary_parts = [
        f"Terrain {hidden['terrain_class']}",
        f"elevation {hidden['elevation_m']:.1f} m",
    ]
    if not baseline:
        summary_parts.append(f"geology {hidden['geology_class']}")
    if primary:
        if baseline:
            summary_parts.append(f"contact with distinct physical body {primary['id']}")
        else:
            summary_parts.append(f"contact with {primary['material']} body {primary['id']}")

    cur = conn.execute(
        """
        INSERT INTO spatial_observations
        (observer_id, source_job_id, observation_kind, detail_level, frame_id,
         x_m, y_m, radius_m, observed_minute, terrain_class, elevation_m,
         geology_class, deposit_id, material, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            observer_id,
            source_job_id,
            observation_kind,
            detail_level,
            SPATIAL_FRAME_ID,
            round(float(x_m), 4),
            round(float(y_m), 4),
            max(0.1, float(radius_m)),
            int(observed_minute),
            hidden["terrain_class"],
            hidden["elevation_m"],
            "unclassified" if baseline else hidden["geology_class"],
            primary["id"] if primary else None,
            None if baseline else (primary["material"] if primary else None),
            "; ".join(summary_parts),
        ),
    )
    return int(cur.lastrowid)


def safe_observation_payload(row: Any) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "observer_id": row["observer_id"],
        "source_job_id": row["source_job_id"],
        "observation_kind": row["observation_kind"],
        "detail_level": row["detail_level"],
        "frame_id": row["frame_id"],
        "x_m": float(row["x_m"]),
        "y_m": float(row["y_m"]),
        "radius_m": float(row["radius_m"]),
        "observed_minute": int(row["observed_minute"]),
        "terrain_class": row["terrain_class"],
        "elevation_m": float(row["elevation_m"]),
        "geology_class": row["geology_class"],
        "deposit_id": row["deposit_id"],
        "material": row["material"],
        "summary": row["summary"],
    }
