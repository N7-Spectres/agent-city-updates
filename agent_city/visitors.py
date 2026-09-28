from __future__ import annotations

from typing import Any

from .db import add_history, connect, get_meta
from .exploration import shared_activity_payload


def _location_name(conn, location_id: str) -> str:
    row = conn.execute("SELECT name FROM locations WHERE id = ?", (location_id,)).fetchone()
    return row["name"] if row else location_id


def _route_distance(conn, a: str, b: str) -> float | None:
    row = conn.execute(
        "SELECT distance_km FROM routes WHERE a = ? AND b = ?",
        (a, b),
    ).fetchone()
    return float(row["distance_km"]) if row else None


def _close_incompatible_open_visits(conn, visitor: str, presence: dict[str, Any], now: int) -> None:
    if presence.get("travel_end_minute") is not None:
        conn.execute(
            """
            UPDATE conversation_visits
            SET ended_minute = COALESCE(ended_minute, ?)
            WHERE visitor = ? AND ended_minute IS NULL
            """,
            (now, visitor),
        )
        return

    rows = conn.execute(
        """
        SELECT cv.id, c.location_id, j.action AS active_action
        FROM conversation_visits cv
        JOIN citizens c ON c.id = cv.citizen_id
        LEFT JOIN jobs j ON j.id = c.active_job_id
        WHERE cv.visitor = ? AND cv.ended_minute IS NULL
        """,
        (visitor,),
    ).fetchall()

    for row in rows:
        if row["location_id"] != presence["location_id"] or row["active_action"] == "travel":
            conn.execute(
                "UPDATE conversation_visits SET ended_minute = ? WHERE id = ? AND ended_minute IS NULL",
                (now, row["id"]),
            )


def ensure_visitor(visitor: str) -> dict[str, Any]:
    visitor = visitor.strip()[:40] or "Visitor"
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM visitor_presence WHERE visitor = ?",
            (visitor,),
        ).fetchone()
        if not row:
            seed = conn.execute(
                "SELECT x_m, y_m FROM locations WHERE id = 'seed_site'"
            ).fetchone()
            conn.execute(
                """
                INSERT INTO visitor_presence(visitor, location_id, x_m, y_m)
                VALUES (?, 'seed_site', ?, ?)
                """,
                (
                    visitor,
                    seed["x_m"] if seed else 0.0,
                    seed["y_m"] if seed else 0.0,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM visitor_presence WHERE visitor = ?",
                (visitor,),
            ).fetchone()

        presence = dict(row)
        now = int(get_meta(conn, "sim_minute") or "360")
        _close_incompatible_open_visits(conn, visitor, presence, now)
        conn.commit()
        return presence


def presence_payload(visitor: str) -> dict[str, Any]:
    presence = ensure_visitor(visitor)
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        loc_name = _location_name(conn, presence["location_id"])
        from_name = _location_name(conn, presence["from_location_id"]) if presence.get("from_location_id") else None
        to_name = _location_name(conn, presence["to_location_id"]) if presence.get("to_location_id") else None

        active_shared = conn.execute(
            """
            SELECT id FROM shared_activities
            WHERE visitor = ? AND status = 'active'
            ORDER BY id DESC LIMIT 1
            """,
            (visitor,),
        ).fetchone()
        shared_payload = (
            shared_activity_payload(conn, int(active_shared["id"]), now)
            if active_shared else None
        )
        if shared_payload and shared_payload.get("movement"):
            presence["x_m"] = shared_payload["movement"]["x_m"]
            presence["y_m"] = shared_payload["movement"]["y_m"]

        destinations = []
        if not presence.get("travel_end_minute") and not active_shared:
            rows = conn.execute(
                """
                SELECT r.b AS id, r.distance_km, l.name
                FROM routes r
                JOIN locations l ON l.id = r.b
                WHERE r.a = ?
                ORDER BY r.distance_km, l.name
                """,
                (presence["location_id"],),
            ).fetchall()
            destinations = [dict(r) for r in rows]

    start = presence.get("travel_start_minute")
    end = presence.get("travel_end_minute")
    traveling = start is not None and end is not None
    if traveling:
        total = max(1, int(end) - int(start))
        elapsed = min(total, max(0, now - int(start)))
        progress = elapsed / total
        remaining = max(0, int(end) - now)
    else:
        total = elapsed = remaining = 0
        progress = 0.0

    return {
        **presence,
        "location_name": loc_name,
        "from_location_name": from_name,
        "to_location_name": to_name,
        "traveling": traveling,
        "progress": progress,
        "elapsed_minutes": elapsed,
        "total_minutes": total,
        "remaining_minutes": remaining,
        "destinations": destinations,
        "shared_activity_id": int(active_shared["id"]) if active_shared else None,
        "shared_activity": shared_payload,
    }


def start_visitor_travel(visitor: str, target: str) -> tuple[bool, str]:
    visitor = visitor.strip()[:40] or "Visitor"
    ensure_visitor(visitor)

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM visitor_presence WHERE visitor = ?",
            (visitor,),
        ).fetchone()
        if not row:
            return False, "Visitor presence could not be created."
        if row["travel_end_minute"] is not None:
            return False, "You are already traveling."
        active_shared = conn.execute(
            """
            SELECT 1 FROM shared_activities
            WHERE visitor = ? AND status = 'active'
            LIMIT 1
            """,
            (visitor,),
        ).fetchone()
        if active_shared:
            return False, "You are already participating in an active shared physical activity."

        origin = row["location_id"]
        if target == origin:
            return False, "You are already there."

        distance = _route_distance(conn, origin, target)
        if distance is None:
            return False, "No known route connects those locations."

        now = int(get_meta(conn, "sim_minute") or "360")
        duration = max(25, int(distance * 45))
        conn.execute(
            """
            UPDATE visitor_presence
            SET from_location_id = ?,
                to_location_id = ?,
                travel_start_minute = ?,
                travel_end_minute = ?
            WHERE visitor = ?
            """,
            (origin, target, now, now + duration, visitor),
        )
        # Choosing to leave a location physically ends any open face-to-face visits.
        conn.execute(
            """
            UPDATE conversation_visits
            SET ended_minute = COALESCE(ended_minute, ?)
            WHERE visitor = ? AND ended_minute IS NULL
            """,
            (now, visitor),
        )
        add_history(
            conn,
            now,
            "visitor",
            f"{visitor} began traveling from {_location_name(conn, origin)} to {_location_name(conn, target)}.",
        )
        conn.commit()

    return True, f"Travel started. Estimated duration: {duration} simulated minutes."


def complete_due_visitor_travel(now: int) -> None:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM visitor_presence
            WHERE travel_end_minute IS NOT NULL
              AND travel_end_minute <= ?
            """,
            (now,),
        ).fetchall()

        for row in rows:
            target = row["to_location_id"]
            if not target:
                continue
            target_name = _location_name(conn, target)
            target_loc = conn.execute(
                "SELECT x_m, y_m FROM locations WHERE id = ?",
                (target,),
            ).fetchone()
            conn.execute(
                """
                UPDATE visitor_presence
                SET location_id = ?,
                    x_m = COALESCE(?, x_m),
                    y_m = COALESCE(?, y_m),
                    from_location_id = NULL,
                    to_location_id = NULL,
                    travel_start_minute = NULL,
                    travel_end_minute = NULL
                WHERE visitor = ?
                """,
                (
                    target,
                    target_loc["x_m"] if target_loc else None,
                    target_loc["y_m"] if target_loc else None,
                    row["visitor"],
                ),
            )
            add_history(
                conn,
                now,
                "visitor",
                f"{row['visitor']} arrived at {target_name}.",
            )

        conn.commit()


def visit_access_payload(visitor: str, citizen_id: str) -> dict[str, Any]:
    """
    Return structured physical availability for a face-to-face visitor interaction.

    Status is intentionally separate from the human-readable reason so the UI can
    distinguish remote, traveling, talking, and otherwise-busy states.
    """
    presence = ensure_visitor(visitor)
    with connect() as conn:
        citizen = conn.execute(
            """
            SELECT c.id, c.name, c.location_id, c.location, c.current_activity,
                   c.active_job_id, c.position_x_m, c.position_y_m,
                   j.action AS active_action,
                   j.citizen_id AS job_initiator_id,
                   j.target AS active_target,
                   j.shared_activity_id
            FROM citizens c
            LEFT JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()

        if not citizen:
            return {
                "accessible": False,
                "status": "missing",
                "reason": "Citizen not found.",
            }

        if presence.get("travel_end_minute") is not None:
            return {
                "accessible": False,
                "status": "visitor_traveling",
                "reason": "You are currently traveling.",
            }

        if citizen["active_action"] in ("travel", "local_move"):
            target_name = (
                _location_name(conn, citizen["active_target"])
                if citizen["active_action"] == "travel" and citizen["active_target"]
                else "a nearby local point"
            )
            return {
                "accessible": False,
                "status": "citizen_traveling",
                "reason": f"{citizen['name']} is currently traveling toward {target_name}.",
            }

        # If the visitor is elsewhere, do not leak the citizen's local busy/talk
        # details as a substitute for physical co-location.
        if presence["location_id"] != citizen["location_id"]:
            return {
                "accessible": False,
                "status": "remote",
                "reason": f"{citizen['name']} is at {citizen['location']}; you are not there.",
            }

        active_shared = conn.execute(
            """
            SELECT * FROM shared_activities
            WHERE visitor = ? AND citizen_id = ? AND status = 'active'
            ORDER BY id DESC LIMIT 1
            """,
            (visitor, citizen_id),
        ).fetchone()
        if active_shared:
            return {
                "accessible": False,
                "status": "shared_activity_active",
                "reason": f"You and {citizen['name']} are currently moving together in shared activity #{active_shared['id']}.",
                "shared_activity_id": int(active_shared["id"]),
            }

        visitor_x = float(presence.get("x_m") or 0.0)
        visitor_y = float(presence.get("y_m") or 0.0)
        citizen_x = float(citizen["position_x_m"] or 0.0)
        citizen_y = float(citizen["position_y_m"] or 0.0)
        separation = ((visitor_x - citizen_x) ** 2 + (visitor_y - citizen_y) ** 2) ** 0.5
        if separation > 2.0:
            return {
                "accessible": False,
                "status": "remote",
                "reason": f"{citizen['name']} is about {separation:.0f} m away within {citizen['location']}.",
                "distance_m": round(separation, 2),
            }

        if citizen["active_action"] == "talk":
            initiator_id = str(citizen["job_initiator_id"] or "")
            target_id = str(citizen["active_target"] or "")

            if str(citizen["id"]) == initiator_id:
                other_id = target_id
            elif str(citizen["id"]) == target_id:
                other_id = initiator_id
            else:
                other_id = ""

            other = (
                conn.execute(
                    "SELECT id, name FROM citizens WHERE id = ?",
                    (other_id,),
                ).fetchone()
                if other_id
                else None
            )
            other_name = other["name"] if other else "another citizen"

            return {
                "accessible": False,
                "status": "citizen_talking",
                "reason": f"{citizen['name']} is currently speaking with {other_name}.",
                "other_citizen_id": other["id"] if other else other_id or None,
                "other_citizen_name": other_name,
            }

        if citizen["active_job_id"] is not None:
            activity = str(citizen["current_activity"] or "occupied").strip()
            return {
                "accessible": False,
                "status": "citizen_busy",
                "reason": f"{citizen['name']} is currently busy: {activity}.",
                "activity": activity,
            }

        return {
            "accessible": True,
            "status": "available",
            "reason": "",
        }


def can_visit_citizen(visitor: str, citizen_id: str) -> tuple[bool, str]:
    access = visit_access_payload(visitor, citizen_id)
    return bool(access["accessible"]), str(access.get("reason") or "")

