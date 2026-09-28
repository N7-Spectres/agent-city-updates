from __future__ import annotations

import json
import math
from typing import Any

from .db import add_history, get_meta
from .spatial import query_hidden_world, record_validated_observation

LOCAL_MOVE_MAX_M = 300.0
SHARED_WALK_MAX_M = 180.0
BASE_WALK_SPEED_M_PER_SIM_MIN = 22.0
BASE_ENERGY_PER_KM = 3.0
LOCAL_ENERGY_MARGIN = 5.0
DIRECT_INSPECTION_RADIUS_M = 1.5


def _terrain_multiplier(terrain_class: str, roughness: float) -> float:
    class_factor = {
        "open_ground": 1.00,
        "low_growth": 1.08,
        "ridge": 1.20,
        "basin": 1.12,
        "broken": 1.42,
    }.get(str(terrain_class), 1.15)
    return class_factor * (0.92 + max(0.0, min(1.0, float(roughness))) * 0.22)


def path_profile(conn, start_x_m: float, start_y_m: float, target_x_m: float, target_y_m: float) -> dict[str, float]:
    start_x = float(start_x_m)
    start_y = float(start_y_m)
    target_x = float(target_x_m)
    target_y = float(target_y_m)
    distance_m = math.hypot(target_x - start_x, target_y - start_y)

    if distance_m <= 0.001:
        return {
            "distance_m": 0.0,
            "terrain_multiplier": 1.0,
            "effective_distance_m": 0.0,
            "duration_minutes": 1.0,
            "energy_cost": 0.0,
        }

    sample_count = max(2, min(12, int(math.ceil(distance_m / 25.0)) + 1))
    multipliers = []
    for index in range(sample_count):
        t = index / (sample_count - 1)
        x = start_x + (target_x - start_x) * t
        y = start_y + (target_y - start_y) * t
        hidden = query_hidden_world(conn, x, y)
        multipliers.append(
            _terrain_multiplier(hidden["terrain_class"], float(hidden["roughness"]))
        )

    terrain_multiplier = sum(multipliers) / len(multipliers)
    effective_distance = distance_m * terrain_multiplier
    duration = max(2.0, effective_distance / BASE_WALK_SPEED_M_PER_SIM_MIN)
    energy_cost = max(0.2, (distance_m / 1000.0) * BASE_ENERGY_PER_KM * terrain_multiplier)

    return {
        "distance_m": round(distance_m, 4),
        "terrain_multiplier": round(terrain_multiplier, 6),
        "effective_distance_m": round(effective_distance, 4),
        "duration_minutes": round(duration, 4),
        "energy_cost": round(energy_cost, 4),
    }


def nearest_operational_charger(conn, x_m: float, y_m: float) -> dict[str, Any] | None:
    rows = conn.execute(
        """
        SELECT id, name, location_id, x_m, y_m, condition
        FROM structures
        WHERE provides_charging = 1
          AND condition > 20
          AND x_m IS NOT NULL
          AND y_m IS NOT NULL
        ORDER BY id
        """
    ).fetchall()

    best = None
    for row in rows:
        distance = math.hypot(float(row["x_m"]) - float(x_m), float(row["y_m"]) - float(y_m))
        if best is None or distance < best["distance_m"]:
            best = {**dict(row), "distance_m": distance}
    return best


def return_energy_from_coordinate(conn, x_m: float, y_m: float) -> float | None:
    charger = nearest_operational_charger(conn, x_m, y_m)
    if charger is None:
        return None
    profile = path_profile(conn, x_m, y_m, float(charger["x_m"]), float(charger["y_m"]))
    return float(profile["energy_cost"]) + LOCAL_ENERGY_MARGIN


def movement_position(
    start_x_m: float,
    start_y_m: float,
    target_x_m: float,
    target_y_m: float,
    start_minute: int,
    end_minute: int,
    now: int,
) -> dict[str, float]:
    total = max(1, int(end_minute) - int(start_minute))
    elapsed = min(total, max(0, int(now) - int(start_minute)))
    progress = elapsed / total
    x = float(start_x_m) + (float(target_x_m) - float(start_x_m)) * progress
    y = float(start_y_m) + (float(target_y_m) - float(start_y_m)) * progress
    return {
        "x_m": round(x, 4),
        "y_m": round(y, 4),
        "progress": progress,
        "elapsed_minutes": elapsed,
        "total_minutes": total,
        "remaining_minutes": max(0, int(end_minute) - int(now)),
    }


def active_local_movement_payload(conn, citizen_id: str, now: int | None = None) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT j.*
        FROM citizens c
        JOIN jobs j ON j.id = c.active_job_id
        WHERE c.id = ?
          AND j.status = 'active'
          AND j.action IN ('local_move', 'shared_local_activity')
        """,
        (citizen_id,),
    ).fetchone()
    if not row:
        return None

    if row["start_x_m"] is None or row["target_x_m"] is None:
        return None

    minute = int(now) if now is not None else int(get_meta(conn, "sim_minute") or "360")
    pos = movement_position(
        float(row["start_x_m"]),
        float(row["start_y_m"]),
        float(row["target_x_m"]),
        float(row["target_y_m"]),
        int(row["start_minute"]),
        int(row["end_minute"]),
        minute,
    )
    return {
        "job_id": int(row["id"]),
        "action": row["action"],
        "frame_id": row["spatial_frame_id"] or "seed_site_local",
        "start_x_m": float(row["start_x_m"]),
        "start_y_m": float(row["start_y_m"]),
        "target_x_m": float(row["target_x_m"]),
        "target_y_m": float(row["target_y_m"]),
        "path_distance_m": float(row["path_distance_m"] or 0),
        "terrain_multiplier": float(row["terrain_multiplier"] or 1),
        "start_minute": int(row["start_minute"]),
        "end_minute": int(row["end_minute"]),
        **pos,
    }


def start_local_move(
    conn,
    citizen_id: str,
    target_x_m: float,
    target_y_m: float,
    *,
    now: int,
    reason: str | None = None,
    max_distance_m: float = LOCAL_MOVE_MAX_M,
) -> tuple[bool, int | None, str]:
    citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    if not citizen:
        return False, None, "Citizen not found."
    if citizen["active_job_id"] is not None:
        return False, None, "Citizen is already occupied."

    start_x = float(citizen["position_x_m"] or 0.0)
    start_y = float(citizen["position_y_m"] or 0.0)
    profile = path_profile(conn, start_x, start_y, float(target_x_m), float(target_y_m))
    distance = float(profile["distance_m"])
    if distance < 0.5:
        return False, None, "Target point is effectively the current position."
    if distance > float(max_distance_m):
        return False, None, f"Target exceeds the local movement limit of {float(max_distance_m):.0f} m."

    return_reserve = return_energy_from_coordinate(conn, float(target_x_m), float(target_y_m))
    if return_reserve is None:
        return False, None, "No operational charger is reachable from that point."
    energy = float(citizen["energy"])
    energy_cost = float(profile["energy_cost"])
    if energy - energy_cost < return_reserve:
        return False, None, "That local movement would consume the reserve needed to reach a charger."

    duration = max(2, int(math.ceil(float(profile["duration_minutes"]))))
    cur = conn.execute(
        """
        INSERT INTO jobs
        (citizen_id, action, target, start_minute, end_minute, status, detail,
         intent_reason, spatial_frame_id, start_x_m, start_y_m, target_x_m, target_y_m,
         path_distance_m, terrain_multiplier)
        VALUES (?, 'local_move', ?, ?, ?, 'active', ?, ?, 'seed_site_local',
                ?, ?, ?, ?, ?, ?)
        """,
        (
            citizen_id,
            f"{float(target_x_m):.3f},{float(target_y_m):.3f}",
            int(now),
            int(now) + duration,
            json.dumps({"energy_cost": energy_cost}, separators=(",", ":")),
            (reason or "")[:500] or None,
            start_x,
            start_y,
            float(target_x_m),
            float(target_y_m),
            distance,
            float(profile["terrain_multiplier"]),
        ),
    )
    job_id = int(cur.lastrowid)
    conn.execute(
        """
        UPDATE citizens
        SET active_job_id = ?, current_activity = ?, last_planned_minute = ?,
            energy = MAX(0, energy - ?)
        WHERE id = ?
        """,
        (
            job_id,
            f"Walking locally toward ({float(target_x_m):.0f} m, {float(target_y_m):.0f} m)",
            int(now),
            energy_cost,
            citizen_id,
        ),
    )
    add_history(
        conn,
        int(now),
        "activity",
        f"{citizen['name']} began a {distance:.0f} m local movement.",
    )
    return True, job_id, "Local movement started."


def start_local_inspection(
    conn,
    citizen_id: str,
    *,
    now: int,
    source_kind: str = "direct_inspection",
) -> tuple[bool, int | None, str]:
    citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    if not citizen:
        return False, None, "Citizen not found."
    if citizen["active_job_id"] is not None:
        return False, None, "Citizen is already occupied."
    if float(citizen["energy"]) < 0.5:
        return False, None, "Insufficient energy for a local inspection."

    cur = conn.execute(
        """
        INSERT INTO jobs
        (citizen_id, action, target, start_minute, end_minute, status, detail,
         intent_reason, spatial_frame_id, start_x_m, start_y_m, target_x_m, target_y_m,
         path_distance_m, terrain_multiplier)
        VALUES (?, 'local_inspect', 'current_position', ?, ?, 'active', ?, ?,
                'seed_site_local', ?, ?, ?, ?, 0, 1)
        """,
        (
            citizen_id,
            int(now),
            int(now) + 15,
            json.dumps({"observation_kind": source_kind}, separators=(",", ":")),
            "Inspect the immediate surroundings.",
            float(citizen["position_x_m"] or 0.0),
            float(citizen["position_y_m"] or 0.0),
            float(citizen["position_x_m"] or 0.0),
            float(citizen["position_y_m"] or 0.0),
        ),
    )
    job_id = int(cur.lastrowid)
    conn.execute(
        """
        UPDATE citizens
        SET active_job_id = ?, current_activity = 'Inspecting immediate surroundings',
            last_planned_minute = ?, energy = MAX(0, energy - 0.5)
        WHERE id = ?
        """,
        (job_id, int(now), citizen_id),
    )
    add_history(conn, int(now), "activity", f"{citizen['name']} began a local field inspection.")
    return True, job_id, "Local inspection started."


def propose_shared_activity(
    conn,
    *,
    visitor: str,
    citizen_id: str,
    target_x_m: float,
    target_y_m: float,
    objective: str,
    source_visit_id: int | None,
    source_exchange_id: int | None,
    now: int,
    tool_equipment_id: int | None = None,
) -> tuple[bool, int | None, str]:
    visitor_name = (visitor or "Visitor").strip()[:40] or "Visitor"
    citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    presence = conn.execute(
        "SELECT * FROM visitor_presence WHERE visitor = ?",
        (visitor_name,),
    ).fetchone()
    if not citizen or not presence:
        return False, None, "Visitor or citizen physical presence is missing."
    if presence["travel_end_minute"] is not None or citizen["active_job_id"] is not None:
        return False, None, "Participants are not currently available."
    if presence["location_id"] != citizen["location_id"]:
        return False, None, "Visitor and citizen are not at the same location."

    cx = float(citizen["position_x_m"] or 0.0)
    cy = float(citizen["position_y_m"] or 0.0)
    vx = float(presence["x_m"] or 0.0)
    vy = float(presence["y_m"] or 0.0)
    if math.hypot(cx - vx, cy - vy) > 2.0:
        return False, None, "Visitor and citizen are not physically close enough to start together."

    if source_visit_id is not None:
        visit = conn.execute(
            """
            SELECT * FROM conversation_visits
            WHERE id = ? AND visitor = ? AND citizen_id = ?
            """,
            (int(source_visit_id), visitor_name, citizen_id),
        ).fetchone()
        if not visit:
            return False, None, "Proposal source visit does not belong to these participants."

    if source_exchange_id is not None:
        exchange = conn.execute(
            """
            SELECT * FROM conversations
            WHERE id = ?
              AND visitor = ?
              AND citizen_id = ?
              AND (? IS NULL OR visit_id = ?)
            """,
            (
                int(source_exchange_id),
                visitor_name,
                citizen_id,
                source_visit_id,
                source_visit_id,
            ),
        ).fetchone()
        if not exchange:
            return False, None, "Proposal source exchange does not belong to these participants."

    profile = path_profile(conn, cx, cy, float(target_x_m), float(target_y_m))
    if float(profile["distance_m"]) > SHARED_WALK_MAX_M:
        return False, None, f"Shared Stage-2 walk exceeds the {SHARED_WALK_MAX_M:.0f} m local limit."
    if float(profile["distance_m"]) < 0.5:
        return False, None, "Shared target is effectively the current position."

    if tool_equipment_id is not None:
        tool = conn.execute(
            "SELECT * FROM equipment WHERE id = ? AND condition > 20",
            (int(tool_equipment_id),),
        ).fetchone()
        tool_available = bool(tool and tool["owner_citizen_id"] == citizen_id)
        if tool and tool["owner_citizen_id"] is None and tool["location_id"] == citizen["location_id"]:
            landmark = conn.execute(
                "SELECT x_m, y_m FROM locations WHERE id = ?",
                (citizen["location_id"],),
            ).fetchone()
            if landmark:
                tool_available = math.hypot(
                    cx - float(landmark["x_m"] or 0.0),
                    cy - float(landmark["y_m"] or 0.0),
                ) <= 5.0
        if not tool_available:
            return False, None, "Requested equipment is not physically available to the citizen."

    cur = conn.execute(
        """
        INSERT INTO shared_activities
        (visitor, citizen_id, activity_type, objective, frame_id,
         start_x_m, start_y_m, target_x_m, target_y_m,
         status, proposed_minute, source_visit_id, source_exchange_id,
         tool_equipment_id)
        VALUES (?, ?, 'walk_inspect', ?, 'seed_site_local',
                ?, ?, ?, ?, 'proposed', ?, ?, ?, ?)
        """,
        (
            visitor_name,
            citizen_id,
            (objective or "Walk together and inspect the destination.")[:500],
            cx,
            cy,
            float(target_x_m),
            float(target_y_m),
            int(now),
            source_visit_id,
            source_exchange_id,
            tool_equipment_id,
        ),
    )
    activity_id = int(cur.lastrowid)
    add_history(
        conn,
        int(now),
        "activity",
        f"A shared local walk/inspection proposal #{activity_id} was recorded for {visitor_name} and {citizen['name']}.",
    )
    return True, activity_id, "Shared activity proposed; explicit visitor acceptance is required."


def accept_shared_activity(conn, activity_id: int, visitor: str, *, now: int) -> tuple[bool, int | None, str]:
    row = conn.execute(
        "SELECT * FROM shared_activities WHERE id = ?",
        (int(activity_id),),
    ).fetchone()
    if not row:
        return False, None, "Shared activity not found."
    if row["status"] != "proposed":
        return False, None, f"Shared activity is already {row['status']}."

    visitor_name = (visitor or "Visitor").strip()[:40] or "Visitor"
    if visitor_name != row["visitor"]:
        return False, None, "Only the proposed visitor may accept this activity."

    conn.execute(
        """
        UPDATE shared_activities
        SET status = 'accepted', accepted_minute = ?
        WHERE id = ?
        """,
        (int(now), int(activity_id)),
    )
    add_history(
        conn,
        int(now),
        "activity",
        f"{visitor_name} accepted shared activity #{activity_id}; no physical movement has started yet.",
    )
    return True, None, "Shared activity accepted; a separate Simulation start is still required."


def reject_shared_activity(conn, activity_id: int, visitor: str, *, now: int) -> tuple[bool, str]:
    row = conn.execute(
        "SELECT * FROM shared_activities WHERE id = ?",
        (int(activity_id),),
    ).fetchone()
    if not row:
        return False, "Shared activity not found."

    visitor_name = (visitor or "Visitor").strip()[:40] or "Visitor"
    if visitor_name != row["visitor"]:
        return False, "Only the proposed visitor may reject this activity."
    if row["status"] not in ("proposed", "accepted"):
        return False, f"Shared activity cannot be rejected from status {row['status']}."

    conn.execute(
        """
        UPDATE shared_activities
        SET status = 'rejected',
            completed_minute = ?,
            outcome = 'rejected',
            failure_reason = 'Visitor rejected the proposal before physical start.'
        WHERE id = ?
        """,
        (int(now), int(activity_id)),
    )
    add_history(
        conn,
        int(now),
        "activity",
        f"{visitor_name} rejected shared activity #{activity_id} before physical start.",
    )
    return True, "Shared activity rejected; no physical movement occurred."


def start_shared_activity(conn, activity_id: int, visitor: str, *, now: int) -> tuple[bool, int | None, str]:
    row = conn.execute(
        "SELECT * FROM shared_activities WHERE id = ?",
        (int(activity_id),),
    ).fetchone()
    if not row:
        return False, None, "Shared activity not found."
    if row["status"] != "accepted":
        return False, None, f"Shared activity must be accepted before start; current status is {row['status']}."

    visitor_name = (visitor or "Visitor").strip()[:40] or "Visitor"
    if visitor_name != row["visitor"]:
        return False, None, "Only the accepted visitor may start this activity."

    citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (row["citizen_id"],)).fetchone()
    presence = conn.execute(
        "SELECT * FROM visitor_presence WHERE visitor = ?",
        (visitor_name,),
    ).fetchone()
    if not citizen or not presence:
        return False, None, "Participant physical state is unavailable."
    if citizen["active_job_id"] is not None or presence["travel_end_minute"] is not None:
        return False, None, "Participants are no longer available."
    if citizen["location_id"] != presence["location_id"]:
        return False, None, "Participants are no longer co-located."

    cx = float(citizen["position_x_m"] or 0.0)
    cy = float(citizen["position_y_m"] or 0.0)
    vx = float(presence["x_m"] or 0.0)
    vy = float(presence["y_m"] or 0.0)
    if math.hypot(cx - vx, cy - vy) > 2.0:
        return False, None, "Participants are no longer physically together."

    if row["tool_equipment_id"] is not None:
        tool = conn.execute(
            "SELECT * FROM equipment WHERE id = ? AND condition > 20",
            (int(row["tool_equipment_id"]),),
        ).fetchone()
        tool_available = bool(tool and tool["owner_citizen_id"] == citizen["id"])
        if tool and tool["owner_citizen_id"] is None and tool["location_id"] == citizen["location_id"]:
            landmark = conn.execute(
                "SELECT x_m, y_m FROM locations WHERE id = ?",
                (citizen["location_id"],),
            ).fetchone()
            if landmark:
                tool_available = math.hypot(
                    cx - float(landmark["x_m"] or 0.0),
                    cy - float(landmark["y_m"] or 0.0),
                ) <= 5.0
        if not tool_available:
            return False, None, "Requested equipment is no longer physically available."

    target_x = float(row["target_x_m"])
    target_y = float(row["target_y_m"])
    profile = path_profile(conn, cx, cy, target_x, target_y)
    if float(profile["distance_m"]) > SHARED_WALK_MAX_M:
        return False, None, "Shared target is no longer within the allowed local range."

    return_reserve = return_energy_from_coordinate(conn, target_x, target_y)
    if return_reserve is None:
        return False, None, "No operational charger is reachable from the shared destination."
    energy_cost = float(profile["energy_cost"])
    if float(citizen["energy"]) - energy_cost < return_reserve:
        return False, None, "Citizen lacks the return-energy reserve for this shared activity."

    duration = max(2, int(math.ceil(float(profile["duration_minutes"]))))
    cur = conn.execute(
        """
        INSERT INTO jobs
        (citizen_id, action, target, start_minute, end_minute, status, detail,
         intent_reason, spatial_frame_id, start_x_m, start_y_m, target_x_m, target_y_m,
         path_distance_m, terrain_multiplier, shared_activity_id)
        VALUES (?, 'shared_local_activity', ?, ?, ?, 'active', ?, ?,
                'seed_site_local', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            citizen["id"],
            f"{target_x:.3f},{target_y:.3f}",
            int(now),
            int(now) + duration,
            json.dumps({"energy_cost": energy_cost, "inspect_on_arrival": True}, separators=(",", ":")),
            str(row["objective"] or "")[:500] or None,
            cx,
            cy,
            target_x,
            target_y,
            float(profile["distance_m"]),
            float(profile["terrain_multiplier"]),
            int(activity_id),
        ),
    )
    job_id = int(cur.lastrowid)

    conn.execute(
        """
        UPDATE shared_activities
        SET status = 'active',
            started_minute = ?,
            citizen_job_id = ?
        WHERE id = ?
        """,
        (int(now), job_id, int(activity_id)),
    )
    conn.execute(
        """
        UPDATE citizens
        SET active_job_id = ?, current_activity = ?, last_planned_minute = ?,
            energy = MAX(0, energy - ?)
        WHERE id = ?
        """,
        (
            job_id,
            f"Walking with {visitor_name} toward a local inspection point",
            int(now),
            energy_cost,
            citizen["id"],
        ),
    )
    add_history(
        conn,
        int(now),
        "activity",
        f"Shared activity #{activity_id} physically started for {visitor_name} and {citizen['name']}.",
    )
    return True, job_id, "Shared activity physically started."


def shared_activity_payload(conn, activity_id: int, now: int | None = None) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM shared_activities WHERE id = ?",
        (int(activity_id),),
    ).fetchone()
    if not row:
        return None
    payload = dict(row)

    if row["status"] == "active" and row["citizen_job_id"] is not None:
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (row["citizen_job_id"],),
        ).fetchone()
        if job and job["start_x_m"] is not None:
            minute = int(now) if now is not None else int(get_meta(conn, "sim_minute") or "360")
            payload["movement"] = movement_position(
                float(job["start_x_m"]),
                float(job["start_y_m"]),
                float(job["target_x_m"]),
                float(job["target_y_m"]),
                int(job["start_minute"]),
                int(job["end_minute"]),
                minute,
            )
            payload["movement"].update({
                "job_id": int(job["id"]),
                "start_x_m": float(job["start_x_m"]),
                "start_y_m": float(job["start_y_m"]),
                "target_x_m": float(job["target_x_m"]),
                "target_y_m": float(job["target_y_m"]),
                "path_distance_m": float(job["path_distance_m"] or 0),
                "terrain_multiplier": float(job["terrain_multiplier"] or 1),
            })
    return payload
