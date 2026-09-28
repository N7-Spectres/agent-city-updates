from __future__ import annotations

from typing import Any

from .db import add_history, connect, get_meta


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
            conn.execute(
                """
                INSERT INTO visitor_presence(visitor, location_id)
                VALUES (?, 'seed_site')
                """,
                (visitor,),
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

        destinations = []
        if not presence.get("travel_end_minute"):
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
            conn.execute(
                """
                UPDATE visitor_presence
                SET location_id = ?,
                    from_location_id = NULL,
                    to_location_id = NULL,
                    travel_start_minute = NULL,
                    travel_end_minute = NULL
                WHERE visitor = ?
                """,
                (target, row["visitor"]),
            )
            add_history(
                conn,
                now,
                "visitor",
                f"{row['visitor']} arrived at {target_name}.",
            )

        conn.commit()


def can_visit_citizen(visitor: str, citizen_id: str) -> tuple[bool, str]:
    presence = ensure_visitor(visitor)
    with connect() as conn:
        citizen = conn.execute(
            """
            SELECT c.name, c.location_id, c.location, c.active_job_id,
                   j.action AS active_action, j.target AS active_target
            FROM citizens c
            LEFT JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()
        if not citizen:
            return False, "Citizen not found."
        if presence.get("travel_end_minute") is not None:
            return False, "You are currently traveling."
        if citizen["active_action"] == "travel":
            target_name = _location_name(conn, citizen["active_target"]) if citizen["active_target"] else "another location"
            return False, f"{citizen['name']} is currently traveling toward {target_name}."
        if presence["location_id"] != citizen["location_id"]:
            return False, f"{citizen['name']} is at {citizen['location']}; you are not there."
    return True, ""
