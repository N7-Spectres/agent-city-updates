from __future__ import annotations

import json
import math
from typing import Any

from .db import connect
from .world import format_sim_time

SOURCE_TYPE = "simulation_spatial_observation"
MAX_SPATIAL_CONTEXT_CHARS = 1400
MAX_SPATIAL_MEMORIES = 12
LOW_VALUE_KINDS = {
    "field_observation",
    "position_tick",
    "movement_sample",
    "passive_scan",
}


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _precision_step(radius_m: float) -> float:
    radius = max(0.1, float(radius_m))
    if radius >= 100:
        return 100.0
    if radius >= 10:
        return 10.0
    if radius >= 1:
        return 1.0
    return 0.1


def _bounded_coordinate(value: float, radius_m: float) -> float:
    step = _precision_step(radius_m)
    rounded = round(float(value) / step) * step
    return round(rounded, 1 if step < 1 else 0)


def _prior_subject_metadata(conn, owner_id: str, subject_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT metadata_json
        FROM memory_events
        WHERE owner_id = ? AND source_type = ?
        ORDER BY sim_minute DESC, id DESC
        LIMIT 80
        """,
        (owner_id, SOURCE_TYPE),
    ).fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        try:
            metadata = json.loads(str(row["metadata_json"] or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if str(metadata.get("subject_id") or "") == subject_id:
            result.append(metadata)
    return result


def _salience(conn, observation) -> tuple[bool, str]:
    kind = str(observation["observation_kind"] or "field_observation")
    deposit_id = str(observation["deposit_id"] or "").strip()
    radius_m = max(0.1, float(observation["radius_m"] or 1.0))
    owner_id = str(observation["observer_id"])

    if not deposit_id:
        if kind in LOW_VALUE_KINDS:
            return False, "routine_observation"
        return True, "explicit_spatial_milestone"

    priors = _prior_subject_metadata(conn, owner_id, deposit_id)
    if not priors:
        return True, "first_subject_encounter"

    prior_kinds = {str(meta.get("observation_kind") or "") for meta in priors}
    if kind not in prior_kinds:
        return True, "new_observation_method"

    prior_radii: list[float] = []
    for meta in priors:
        try:
            prior_radii.append(float(meta.get("precision_radius_m")))
        except (TypeError, ValueError):
            pass
    best_radius = min(prior_radii) if prior_radii else math.inf
    if radius_m <= best_radius * 0.75:
        return True, "improved_precision"

    return False, "repeat_no_new_spatial_value"


def _insert_memory(conn, observation, reason: str) -> None:
    owner_id = str(observation["observer_id"])
    deposit_id = str(observation["deposit_id"] or "").strip() or None
    radius_m = max(0.1, float(observation["radius_m"] or 1.0))
    x_m = _bounded_coordinate(float(observation["x_m"]), radius_m)
    y_m = _bounded_coordinate(float(observation["y_m"]), radius_m)
    kind = str(observation["observation_kind"] or "field_observation")
    material = str(observation["material"] or "").strip() or None
    summary = " ".join(str(observation["summary"] or "").split()).strip()
    if not summary:
        return

    metadata = {
        "verification": "verified",
        "channel": "personal_observation",
        "observation_id": int(observation["id"]),
        "source_job_id": observation["source_job_id"],
        "observation_kind": kind,
        "frame_id": str(observation["frame_id"]),
        "observed_x_m": x_m,
        "observed_y_m": y_m,
        "precision_radius_m": radius_m,
        "terrain_class": str(observation["terrain_class"]),
        "elevation_m": round(float(observation["elevation_m"]), 1),
        "geology_class": str(observation["geology_class"]),
        "subject_type": "generated_deposit" if deposit_id else "spatial_observation",
        "subject_id": deposit_id,
        "material": material,
        "salience_reason": reason,
    }

    subject_text = f"stable deposit {deposit_id}" if deposit_id else "observed area"
    bounded_summary = (
        f"{summary} Near ({x_m:g}, {y_m:g}) m in {metadata['frame_id']}, "
        f"observation radius ±{radius_m:g} m; subject: {subject_text}."
    )
    importance = 0.80 if reason == "first_subject_encounter" else 0.68
    if reason == "explicit_spatial_milestone":
        importance = 0.62

    conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status, metadata_json
        )
        VALUES (?, ?, 'spatial_observation', NULL, ?, ?, 'observer',
                ?, ?, 'verified', ?)
        """,
        (
            owner_id,
            int(observation["observed_minute"]),
            SOURCE_TYPE,
            int(observation["id"]),
            bounded_summary[:1200],
            importance,
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ),
    )


def sync_spatial_observations_in_conn(conn) -> None:
    """
    Project only safe validated observations into personal Memory.

    Never reads planet_seed, generated_deposits, richness, or hidden body geometry.
    """
    if not _table_exists(conn, "spatial_observations"):
        return

    rows = conn.execute(
        """
        SELECT id, observer_id, source_job_id, observation_kind, frame_id,
               x_m, y_m, radius_m, observed_minute, terrain_class,
               elevation_m, geology_class, deposit_id, material, summary
        FROM spatial_observations
        ORDER BY id
        """
    ).fetchall()

    for observation in rows:
        owner_id = str(observation["observer_id"])
        if not conn.execute("SELECT 1 FROM citizens WHERE id = ?", (owner_id,)).fetchone():
            continue
        if conn.execute(
            """
            SELECT 1 FROM memory_events
            WHERE owner_id = ? AND source_type = ? AND source_id = ?
              AND event_kind = 'spatial_observation' AND source_role = 'observer'
            LIMIT 1
            """,
            (owner_id, SOURCE_TYPE, int(observation["id"])),
        ).fetchone():
            continue

        salient, reason = _salience(conn, observation)
        if salient:
            _insert_memory(conn, observation, reason)


def sync_spatial_observations() -> None:
    with connect() as conn:
        sync_spatial_observations_in_conn(conn)
        conn.commit()


def _rows(citizen_id: str, scan_limit: int = 180) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, sim_minute, event_kind, source_type, source_id,
                   source_role, summary, importance, status, metadata_json
            FROM memory_events
            WHERE owner_id = ? AND source_type = ?
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (citizen_id, SOURCE_TYPE, max(1, scan_limit)),
        ).fetchall()
        return [dict(row) for row in rows]


def spatial_snapshot_for(
    citizen_id: str,
    *,
    subject_id: str | None = None,
    center_x_m: float | None = None,
    center_y_m: float | None = None,
    radius_m: float | None = None,
    limit: int = MAX_SPATIAL_MEMORIES,
) -> list[dict[str, Any]]:
    sync_spatial_observations()

    result: list[dict[str, Any]] = []
    has_center = center_x_m is not None and center_y_m is not None
    search_radius = max(0.0, float(radius_m or 0.0))

    for row in _rows(citizen_id):
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        if subject_id is not None and str(metadata.get("subject_id") or "") != str(subject_id):
            continue

        if has_center:
            try:
                dx = float(metadata["observed_x_m"]) - float(center_x_m)
                dy = float(metadata["observed_y_m"]) - float(center_y_m)
            except (KeyError, TypeError, ValueError):
                continue
            if math.hypot(dx, dy) > search_radius:
                continue

        item = dict(row)
        item["metadata"] = metadata
        item.pop("metadata_json", None)
        item["sim_label"] = format_sim_time(int(row["sim_minute"]))
        result.append(item)
        if len(result) >= max(1, limit):
            break

    return result


def spatial_context_for(
    citizen_id: str,
    *,
    subject_id: str | None = None,
    limit: int = 5,
) -> str:
    memories = spatial_snapshot_for(citizen_id, subject_id=subject_id, limit=limit)
    if not memories:
        return "- no retained salient spatial observations"

    parts: list[str] = []
    for memory in reversed(memories):
        meta = memory["metadata"]
        subject = meta.get("subject_id")
        subject_text = f" stable subject {subject};" if subject else ""
        parts.append(f"- {memory['sim_label']}:{subject_text} {memory['summary']}")
        if sum(len(part) + 1 for part in parts) >= MAX_SPATIAL_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_SPATIAL_CONTEXT_CHARS]
