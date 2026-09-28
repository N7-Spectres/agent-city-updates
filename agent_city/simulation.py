from __future__ import annotations

from typing import Any

from .db import add_history, connect, get_meta

CARRY_CAPACITY = 20.0


def location_name(conn, location_id: str) -> str:
    row = conn.execute("SELECT name FROM locations WHERE id = ?", (location_id,)).fetchone()
    return row["name"] if row else location_id


def route_distance(conn, a: str, b: str) -> float | None:
    row = conn.execute("SELECT distance_km FROM routes WHERE a = ? AND b = ?", (a, b)).fetchone()
    return float(row["distance_km"]) if row else None


def carried_amount(conn, citizen_id: str) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM citizen_inventory WHERE citizen_id = ?",
        (citizen_id,),
    ).fetchone()
    return float(row["total"] or 0)


def possible_actions(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        c = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not c or c["active_job_id"] is not None:
            return []

        actions: list[dict[str, Any]] = []
        location_id = c["location_id"]
        energy = float(c["energy"])
        cargo = carried_amount(conn, citizen_id)

        if location_id == "seed_site":
            if energy < 95:
                actions.append({"action": "charge", "target": "seed_site", "label": "Recharge at the Seed Site charging station."})
            if cargo > 0:
                actions.append({"action": "deposit_cargo", "target": "seed_site", "label": f"Deposit {cargo:g} carried material into Seed Site storage."})
        else:
            distance = route_distance(conn, location_id, "seed_site")
            if distance is not None:
                actions.append({"action": "travel", "target": "seed_site", "label": f"Travel back to Seed Site ({distance:.1f} km)."})

        rows = conn.execute(
            """
            SELECT r.b AS target, r.distance_km, l.name
            FROM routes r JOIN locations l ON l.id = r.b
            WHERE r.a = ?
            ORDER BY r.distance_km
            """,
            (location_id,),
        ).fetchall()

        if energy >= 15 and cargo <= 0:
            for row in rows:
                actions.append({"action": "travel", "target": row["target"], "label": f"Travel to {row['name']} ({row['distance_km']:.1f} km)."})

        if location_id != "seed_site" and energy >= 12:
            loc = conn.execute("SELECT surveyed, name FROM locations WHERE id = ?", (location_id,)).fetchone()
            if loc and not loc["surveyed"]:
                actions.append({"action": "survey", "target": location_id, "label": f"Survey {loc['name']} for geological or biological material."})

        free_capacity = max(0.0, CARRY_CAPACITY - cargo)
        if location_id != "seed_site" and energy >= 10 and free_capacity >= 1:
            deps = conn.execute(
                """
                SELECT id, material, amount
                FROM deposits
                WHERE location_id = ? AND discovered = 1 AND amount > 0
                ORDER BY material
                """,
                (location_id,),
            ).fetchall()
            for dep in deps:
                amount = min(10.0, float(dep["amount"]), free_capacity)
                actions.append({
                    "action": "extract",
                    "target": dep["id"],
                    "material": dep["material"],
                    "amount": amount,
                    "label": f"Extract {amount:g} units of {dep['material']}.",
                })

        # Face-to-face conversation is possible only with a co-located citizen who is also free.
        if energy >= 5:
            others = conn.execute(
                """
                SELECT id, name
                FROM citizens
                WHERE location_id = ? AND id != ? AND active_job_id IS NULL
                ORDER BY rowid
                """,
                (location_id, citizen_id),
            ).fetchall()
            for other in others:
                actions.append({
                    "action": "talk",
                    "target": other["id"],
                    "label": f"Talk face-to-face with {other['name']} here at {c['location']}.",
                })

        actions.append({"action": "wait", "target": location_id, "label": "Remain where you are and observe for a while."})
        return actions


def start_action(citizen_id: str, request: dict[str, Any]) -> tuple[bool, str]:
    legal = possible_actions(citizen_id)
    chosen = None

    for action in legal:
        if (
            action["action"] == request.get("action")
            and action.get("target") == request.get("target")
            and (action["action"] != "extract" or action.get("material") == request.get("material"))
        ):
            chosen = action
            break

    if not chosen:
        return False, "That action is not currently legal in the physical world."

    with connect() as conn:
        c = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        now = int(get_meta(conn, "sim_minute") or "360")
        action = chosen["action"]
        target = chosen.get("target")
        material = chosen.get("material")
        amount = chosen.get("amount")
        intent_reason = str(request.get("reason") or "").strip()[:500] or None

        duration = 30
        detail = ""

        if action == "travel":
            distance = route_distance(conn, c["location_id"], target)
            if distance is None:
                return False, "No known route exists."
            duration = max(25, int(distance * 45))
            # A citizen physically departing ends any open face-to-face visitor sessions with them.
            conn.execute(
                """
                UPDATE conversation_visits
                SET ended_minute = COALESCE(ended_minute, ?)
                WHERE citizen_id = ? AND ended_minute IS NULL
                """,
                (now, citizen_id),
            )
            energy_cost = max(2.0, distance * 3.0)
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - ?) WHERE id = ?", (energy_cost, citizen_id))
            detail = f"travel:{c['location_id']}->{target}"
            activity = f"Traveling to {location_name(conn, target)}"

        elif action == "survey":
            duration = 120
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 8) WHERE id = ?", (citizen_id,))
            detail = f"survey:{target}"
            activity = f"Surveying {location_name(conn, target)}"

        elif action == "extract":
            duration = 90
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 7) WHERE id = ?", (citizen_id,))
            detail = f"extract:{target}"
            activity = f"Extracting {material}"

        elif action == "talk":
            target_citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (target,)).fetchone()
            if (
                not target_citizen
                or target_citizen["location_id"] != c["location_id"]
                or target_citizen["active_job_id"] is not None
            ):
                return False, "That citizen is no longer available for a face-to-face conversation here."
            duration = 20
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 1) WHERE id IN (?, ?)", (citizen_id, target))
            detail = f"talk:{target}"
            activity = f"Talking with {target_citizen['name']}"

        elif action == "deposit_cargo":
            duration = 20
            detail = "deposit"
            activity = "Unloading material into Seed Site storage"

        elif action == "charge":
            duration = 60
            detail = "charge"
            activity = "Charging at Seed Site"

        else:
            duration = 45
            detail = "wait"
            activity = "Observing surroundings"

        cur = conn.execute(
            """
            INSERT INTO jobs
            (citizen_id, action, target, material, amount, start_minute, end_minute, status, detail, intent_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (citizen_id, action, target, material, amount, now, now + duration, detail, intent_reason),
        )
        job_id = cur.lastrowid

        conn.execute(
            """
            UPDATE citizens
            SET active_job_id = ?, current_activity = ?, last_planned_minute = ?
            WHERE id = ?
            """,
            (job_id, activity, now, citizen_id),
        )

        if action == "talk":
            conn.execute(
                """
                UPDATE citizens
                SET active_job_id = ?, current_activity = ?, last_planned_minute = ?
                WHERE id = ?
                """,
                (job_id, f"Talking with {c['name']}", now, target),
            )

        reason_note = f" Reason: {intent_reason}" if intent_reason else ""
        add_history(conn, now, "activity", f"{c['name']} began: {activity}.{reason_note}")
        conn.commit()
        return True, activity


def complete_due_jobs(now: int) -> None:
    with connect() as conn:
        jobs = conn.execute(
            "SELECT * FROM jobs WHERE status = 'active' AND end_minute <= ? ORDER BY id",
            (now,),
        ).fetchall()

        for job in jobs:
            c = conn.execute("SELECT * FROM citizens WHERE id = ?", (job["citizen_id"],)).fetchone()
            if not c:
                continue

            action = job["action"]
            message = None
            job_status = "complete"

            if action == "travel":
                target = job["target"]
                name = location_name(conn, target)
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = ?, location = ?, current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (target, name, c["id"]),
                )
                message = f"{c['name']} arrived at {name}."

            elif action == "survey":
                loc_id = job["target"]
                loc_name = location_name(conn, loc_id)
                conn.execute("UPDATE locations SET surveyed = 1 WHERE id = ?", (loc_id,))
                undiscovered = conn.execute(
                    "SELECT * FROM deposits WHERE location_id = ? AND discovered = 0 ORDER BY id",
                    (loc_id,),
                ).fetchall()
                if undiscovered:
                    dep = undiscovered[0]
                    conn.execute(
                        """
                        UPDATE deposits
                        SET discovered = 1, discoverer_id = ?, discovered_minute = ?
                        WHERE id = ?
                        """,
                        (c["id"], now, dep["id"]),
                    )
                    message = f"{c['name']} surveyed {loc_name} and confirmed a deposit of {dep['material']}."
                else:
                    message = f"{c['name']} completed a survey of {loc_name}; no new deposit was confirmed."
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "extract":
                dep = conn.execute("SELECT * FROM deposits WHERE id = ?", (job["target"],)).fetchone()
                amount = min(float(job["amount"] or 0), float(dep["amount"] if dep else 0))
                if dep and dep["discovered"] and amount > 0:
                    conn.execute("UPDATE deposits SET amount = amount - ? WHERE id = ?", (amount, dep["id"]))
                    conn.execute(
                        """
                        INSERT INTO citizen_inventory(citizen_id, material, amount)
                        VALUES (?, ?, ?)
                        ON CONFLICT(citizen_id, material)
                        DO UPDATE SET amount = amount + excluded.amount
                        """,
                        (c["id"], dep["material"], amount),
                    )
                    message = f"{c['name']} extracted {amount:g} units of {dep['material']}."
                else:
                    message = f"{c['name']}'s extraction attempt produced no usable material."
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "talk":
                target_id = job["target"]
                target_citizen = conn.execute(
                    "SELECT name FROM citizens WHERE id = ?",
                    (target_id,),
                ).fetchone()
                conversation = conn.execute(
                    """
                    SELECT id
                    FROM citizen_conversations
                    WHERE source_job_id = ?
                    """,
                    (job["id"],),
                ).fetchone()

                conn.execute(
                    """
                    UPDATE citizens
                    SET current_activity = 'Available', active_job_id = NULL
                    WHERE id IN (?, ?) AND active_job_id = ?
                    """,
                    (c["id"], target_id, job["id"]),
                )

                target_name = target_citizen["name"] if target_citizen else target_id
                if conversation:
                    message = (
                        f"{c['name']} and {target_name} finished talking at "
                        f"{c['location']} (conversation #{int(conversation['id'])})."
                    )
                else:
                    job_status = "failed"
                    message = (
                        f"{c['name']} and {target_name}'s conversation attempt at "
                        f"{c['location']} ended without a recorded exchange."
                    )

            elif action == "deposit_cargo":
                cargo = conn.execute(
                    "SELECT material, amount FROM citizen_inventory WHERE citizen_id = ? AND amount > 0",
                    (c["id"],),
                ).fetchall()
                materials = []
                for row in cargo:
                    materials.append(f"{row['amount']:g} {row['material']}")
                    conn.execute(
                        """
                        INSERT INTO resources(name, amount) VALUES (?, ?)
                        ON CONFLICT(name) DO UPDATE SET amount = amount + excluded.amount
                        """,
                        (row["material"], row["amount"]),
                    )
                conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = ?", (c["id"],))
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))
                message = (
                    f"{c['name']} deposited " + ", ".join(materials) + " into Seed Site storage."
                    if materials else f"{c['name']} had no cargo to deposit."
                )

            elif action == "charge":
                conn.execute(
                    """
                    UPDATE citizens
                    SET energy = MIN(100, energy + 25), current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (c["id"],),
                )
                message = f"{c['name']} completed a charging cycle."

            else:
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))
                message = f"{c['name']} finished observing the area."

            conn.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                (job_status, job["id"]),
            )
            if message:
                add_history(conn, now, "activity", message)

        conn.commit()
