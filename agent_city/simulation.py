from __future__ import annotations

import json
import math
from typing import Any

from .db import add_history, connect, get_meta

BASE_CARRY_CAPACITY = 20.0
RETURN_ENERGY_MARGIN = 5.0

# These are starting mechanical processes supported by the already-existing Seed Site
# workbench/material stock. They are not a technology tree and do not imply future research.
FABRICATION_PROCESSES: dict[str, dict[str, Any]] = {
    "field_pack": {
        "name": "Field Cargo Pack",
        "kind": "cargo",
        "duration": 90,
        "energy_cost": 4.0,
        "materials": {
            "Processed structural material": 6.0,
            "Fasteners": 8.0,
            "Plant Fiber": 4.0,
        },
        "cargo_bonus": 12.0,
        "extraction_speed_multiplier": 1.0,
    },
    "extraction_tool": {
        "name": "Powered Extraction Tool",
        "kind": "extraction",
        "duration": 120,
        "energy_cost": 6.0,
        "materials": {
            "Mechanical components": 6.0,
            "Basic electronics": 3.0,
            "Fasteners": 4.0,
        },
        "cargo_bonus": 0.0,
        "extraction_speed_multiplier": 1.35,
    },
}

CONSTRUCTION_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "field_shelter": {
        "name": "Field Shelter",
        "kind": "shelter",
        "duration": 180,
        "energy_cost": 8.0,
        "materials": {
            "Processed structural material": 18.0,
            "Fasteners": 12.0,
            "Mechanical components": 3.0,
        },
        "provides_charging": 0,
    },
    "storage_annex": {
        "name": "Storage Annex",
        "kind": "storage",
        "duration": 210,
        "energy_cost": 9.0,
        "materials": {
            "Processed structural material": 22.0,
            "Fasteners": 16.0,
            "Mechanical components": 5.0,
        },
        "provides_charging": 0,
    },
}


def location_name(conn, location_id: str) -> str:
    row = conn.execute("SELECT name FROM locations WHERE id = ?", (location_id,)).fetchone()
    return row["name"] if row else location_id


def route_distance(conn, a: str, b: str) -> float | None:
    row = conn.execute("SELECT distance_km FROM routes WHERE a = ? AND b = ?", (a, b)).fetchone()
    return float(row["distance_km"]) if row else None


def shortest_route_distance(conn, start: str, destinations: set[str]) -> float | None:
    if start in destinations:
        return 0.0

    rows = conn.execute("SELECT a, b, distance_km FROM routes").fetchall()
    graph: dict[str, list[tuple[str, float]]] = {}
    for row in rows:
        graph.setdefault(row["a"], []).append((row["b"], float(row["distance_km"])))

    distances: dict[str, float] = {start: 0.0}
    visited: set[str] = set()
    while True:
        current = None
        current_distance = math.inf
        for node, distance in distances.items():
            if node not in visited and distance < current_distance:
                current = node
                current_distance = distance
        if current is None:
            return None
        if current in destinations:
            return current_distance
        visited.add(current)
        for neighbor, edge in graph.get(current, []):
            new_distance = current_distance + edge
            if new_distance < distances.get(neighbor, math.inf):
                distances[neighbor] = new_distance


def charging_locations(conn) -> set[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT location_id
        FROM structures
        WHERE provides_charging = 1
          AND condition > 0
          AND location_id IS NOT NULL
        """
    ).fetchall()
    return {row["location_id"] for row in rows}


def return_energy_required(conn, location_id: str) -> float | None:
    chargers = charging_locations(conn)
    distance = shortest_route_distance(conn, location_id, chargers)
    if distance is None:
        return None
    return max(0.0, distance * 3.0) + RETURN_ENERGY_MARGIN


def action_energy_safe(conn, location_id: str, current_energy: float, immediate_cost: float) -> bool:
    reserve = return_energy_required(conn, location_id)
    if reserve is None:
        return False
    return current_energy - immediate_cost >= reserve


def carried_amount(conn, citizen_id: str) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM citizen_inventory WHERE citizen_id = ?",
        (citizen_id,),
    ).fetchone()
    return float(row["total"] or 0)


def available_equipment(conn, citizen_id: str, location_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT *
        FROM equipment
        WHERE condition > 0
          AND (
              owner_citizen_id = ?
              OR (owner_citizen_id IS NULL AND location_id = ?)
          )
        ORDER BY id
        """,
        (citizen_id, location_id),
    ).fetchall()
    return [dict(row) for row in rows]


def cargo_capacity(conn, citizen_id: str, location_id: str) -> float:
    bonus = sum(float(item["cargo_bonus"] or 0) for item in available_equipment(conn, citizen_id, location_id))
    return BASE_CARRY_CAPACITY + bonus


def extraction_speed_multiplier(conn, citizen_id: str, location_id: str) -> float:
    multipliers = [
        float(item["extraction_speed_multiplier"] or 1.0)
        for item in available_equipment(conn, citizen_id, location_id)
        if float(item["extraction_speed_multiplier"] or 1.0) > 1.0
    ]
    return max(multipliers, default=1.0)


def resources_available(conn, requirements: dict[str, float]) -> bool:
    for material, amount in requirements.items():
        row = conn.execute("SELECT amount FROM resources WHERE name = ?", (material,)).fetchone()
        if not row or float(row["amount"]) + 1e-9 < float(amount):
            return False
    return True


def consume_resources(conn, requirements: dict[str, float]) -> bool:
    if not resources_available(conn, requirements):
        return False
    for material, amount in requirements.items():
        conn.execute(
            "UPDATE resources SET amount = amount - ? WHERE name = ? AND amount >= ?",
            (float(amount), material, float(amount)),
        )
    return True


def _unique_structure_name(conn, base_name: str) -> str:
    existing = conn.execute("SELECT COUNT(*) AS n FROM structures WHERE name LIKE ?", (f"{base_name}%",)).fetchone()
    n = int(existing["n"] or 0)
    return base_name if n == 0 else f"{base_name} {n + 1}"


def _project_requirements(conn, project_id: int) -> dict[str, float]:
    rows = conn.execute(
        "SELECT material, required_amount FROM project_materials WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    return {row["material"]: float(row["required_amount"]) for row in rows}


def create_project(conn, citizen_id: str, blueprint_id: str, now: int) -> int | None:
    blueprint = CONSTRUCTION_BLUEPRINTS.get(blueprint_id)
    if not blueprint:
        return None

    c = conn.execute("SELECT location_id FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    if not c:
        return None
    # v0.5 material logistics are settlement-local. Remote construction will require
    # explicit project-material transport rather than teleporting reserved stock.
    if c["location_id"] != "seed_site":
        return None

    loc = conn.execute("SELECT x_km, y_km FROM locations WHERE id = ?", (c["location_id"],)).fetchone()
    cur = conn.execute(
        """
        INSERT INTO projects
        (blueprint_id, name, location_id, x_km, y_km, status, created_by, created_minute)
        VALUES (?, ?, ?, ?, ?, 'planned', ?, ?)
        """,
        (
            blueprint_id,
            blueprint["name"],
            c["location_id"],
            float(loc["x_km"] or 0.0) if loc else 0.0,
            float(loc["y_km"] or 0.0) if loc else 0.0,
            citizen_id,
            now,
        ),
    )
    project_id = int(cur.lastrowid)
    for material, amount in blueprint["materials"].items():
        conn.execute(
            """
            INSERT INTO project_materials(project_id, material, required_amount, reserved_amount)
            VALUES (?, ?, ?, 0)
            """,
            (project_id, material, float(amount)),
        )
    return project_id


def reserve_project_materials(conn, project_id: int, now: int) -> bool:
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project or project["status"] != "planned":
        return False
    requirements = _project_requirements(conn, project_id)
    if not consume_resources(conn, requirements):
        return False
    for material, amount in requirements.items():
        conn.execute(
            "UPDATE project_materials SET reserved_amount = ? WHERE project_id = ? AND material = ?",
            (float(amount), project_id, material),
        )
    conn.execute(
        "UPDATE projects SET status = 'reserved', reserved_minute = ? WHERE id = ?",
        (now, project_id),
    )
    return True


def possible_actions(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        c = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not c or c["active_job_id"] is not None:
            return []

        actions: list[dict[str, Any]] = []
        location_id = c["location_id"]
        energy = float(c["energy"])
        cargo = carried_amount(conn, citizen_id)
        capacity = cargo_capacity(conn, citizen_id, location_id)

        if location_id == "seed_site":
            if energy < 95:
                actions.append({"action": "charge", "target": "seed_site", "label": "Recharge at the Seed Site charging station."})
            if cargo > 0:
                actions.append({"action": "deposit_cargo", "target": "seed_site", "label": f"Deposit {cargo:g} carried material into Seed Site storage."})

            for process_id, process in FABRICATION_PROCESSES.items():
                if resources_available(conn, process["materials"]) and action_energy_safe(
                    conn, location_id, energy, float(process["energy_cost"])
                ):
                    actions.append({
                        "action": "fabricate",
                        "target": process_id,
                        "label": f"Fabricate one {process['name']} at the Basic Workbench.",
                    })

            for blueprint_id, blueprint in CONSTRUCTION_BLUEPRINTS.items():
                actions.append({
                    "action": "plan_project",
                    "target": blueprint_id,
                    "label": f"Plan a {blueprint['name']} project at Seed Site.",
                })

            planned = conn.execute(
                "SELECT id, name FROM projects WHERE status = 'planned' AND location_id = ? ORDER BY id",
                (location_id,),
            ).fetchall()
            for project in planned:
                requirements = _project_requirements(conn, int(project["id"]))
                if resources_available(conn, requirements):
                    actions.append({
                        "action": "reserve_project",
                        "target": str(project["id"]),
                        "label": f"Reserve settlement materials for {project['name']} project #{project['id']}.",
                    })

            reserved = conn.execute(
                "SELECT id, name, blueprint_id FROM projects WHERE status = 'reserved' AND location_id = ? ORDER BY id",
                (location_id,),
            ).fetchall()
            for project in reserved:
                blueprint = CONSTRUCTION_BLUEPRINTS.get(project["blueprint_id"])
                if blueprint and action_energy_safe(conn, location_id, energy, float(blueprint["energy_cost"])):
                    actions.append({
                        "action": "construct",
                        "target": str(project["id"]),
                        "label": f"Construct reserved {project['name']} project #{project['id']}.",
                    })
        else:
            distance = route_distance(conn, location_id, "seed_site")
            if distance is not None:
                travel_cost = max(2.0, distance * 3.0)
                if energy >= travel_cost:
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

        if cargo <= 0:
            for row in rows:
                travel_cost = max(2.0, float(row["distance_km"]) * 3.0)
                target_reserve = return_energy_required(conn, row["target"])
                if target_reserve is not None and energy - travel_cost >= target_reserve:
                    actions.append({
                        "action": "travel",
                        "target": row["target"],
                        "label": f"Travel to {row['name']} ({row['distance_km']:.1f} km).",
                    })

        if location_id != "seed_site":
            loc = conn.execute("SELECT surveyed, name FROM locations WHERE id = ?", (location_id,)).fetchone()
            if loc and not loc["surveyed"] and action_energy_safe(conn, location_id, energy, 8.0):
                actions.append({"action": "survey", "target": location_id, "label": f"Survey {loc['name']} for geological or biological material."})

        free_capacity = max(0.0, capacity - cargo)
        if location_id != "seed_site" and free_capacity >= 1 and action_energy_safe(conn, location_id, energy, 7.0):
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
                    "label": f"Extract {amount:g} units of {dep['material']} (capacity {capacity:g}).",
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
            and str(action.get("target")) == str(request.get("target"))
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
        project_id = None

        if action == "travel":
            distance = route_distance(conn, c["location_id"], target)
            if distance is None:
                return False, "No known route exists."
            energy_cost = max(2.0, distance * 3.0)
            target_reserve = return_energy_required(conn, target)
            if target_reserve is None or float(c["energy"]) - energy_cost < target_reserve:
                return False, "That journey would not leave enough energy to reach a known charger safely."
            duration = max(25, int(distance * 45))
            conn.execute(
                """
                UPDATE conversation_visits
                SET ended_minute = COALESCE(ended_minute, ?)
                WHERE citizen_id = ? AND ended_minute IS NULL
                """,
                (now, citizen_id),
            )
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - ?) WHERE id = ?", (energy_cost, citizen_id))
            detail = f"travel:{c['location_id']}->{target}"
            activity = f"Traveling to {location_name(conn, target)}"

        elif action == "survey":
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), 8.0):
                return False, "Surveying now would consume the energy reserve needed to reach a known charger."
            duration = 120
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 8) WHERE id = ?", (citizen_id,))
            detail = f"survey:{target}"
            activity = f"Surveying {location_name(conn, target)}"

        elif action == "extract":
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), 7.0):
                return False, "Extraction now would consume the energy reserve needed to reach a known charger."
            speed = extraction_speed_multiplier(conn, citizen_id, c["location_id"])
            duration = max(35, int(round(90 / speed)))
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 7) WHERE id = ?", (citizen_id,))
            detail = f"extract:{target}:speed={speed:.2f}"
            activity = f"Extracting {material}"

        elif action == "fabricate":
            process = FABRICATION_PROCESSES.get(str(target))
            if not process or c["location_id"] != "seed_site":
                return False, "That fabrication process is not available here."
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), float(process["energy_cost"])):
                return False, "Fabrication would leave insufficient return-energy reserve."
            if not consume_resources(conn, process["materials"]):
                return False, "Required fabrication materials are no longer available."
            duration = int(process["duration"])
            conn.execute(
                "UPDATE citizens SET energy = MAX(0, energy - ?) WHERE id = ?",
                (float(process["energy_cost"]), citizen_id),
            )
            detail = "fabricate:" + json.dumps({"process_id": target}, separators=(",", ":"))
            activity = f"Fabricating {process['name']}"

        elif action == "plan_project":
            project_id = create_project(conn, citizen_id, str(target), now)
            if project_id is None:
                return False, "That construction project cannot be planned at the current site."
            duration = 20
            detail = f"plan_project:{project_id}"
            activity = f"Planning {CONSTRUCTION_BLUEPRINTS[str(target)]['name']} project #{project_id}"

        elif action == "reserve_project":
            project_id = int(target)
            if not reserve_project_materials(conn, project_id, now):
                return False, "The project cannot reserve its required materials."
            duration = 15
            detail = f"reserve_project:{project_id}"
            project = conn.execute("SELECT name FROM projects WHERE id = ?", (project_id,)).fetchone()
            activity = f"Staging materials for {project['name']} project #{project_id}"

        elif action == "construct":
            project_id = int(target)
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if not project or project["status"] != "reserved" or project["location_id"] != c["location_id"]:
                return False, "That project is not ready for construction here."
            blueprint = CONSTRUCTION_BLUEPRINTS.get(project["blueprint_id"])
            if not blueprint:
                return False, "The project blueprint is unavailable."
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), float(blueprint["energy_cost"])):
                return False, "Construction would consume the energy reserve needed to reach a known charger."
            duration = int(blueprint["duration"])
            conn.execute(
                "UPDATE citizens SET energy = MAX(0, energy - ?) WHERE id = ?",
                (float(blueprint["energy_cost"]), citizen_id),
            )
            detail = f"construct:{project_id}"
            activity = f"Constructing {project['name']} project #{project_id}"

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
            (citizen_id, action, target, material, amount, start_minute, end_minute, status, detail, intent_reason, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
            """,
            (citizen_id, action, target, material, amount, now, now + duration, detail, intent_reason, project_id),
        )
        job_id = int(cur.lastrowid)

        if action == "construct" and project_id is not None:
            conn.execute(
                """
                UPDATE projects
                SET status = 'underway', started_minute = ?, active_job_id = ?
                WHERE id = ?
                """,
                (now, job_id, project_id),
            )

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
            outcome = "success"

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
                capacity = cargo_capacity(conn, c["id"], c["location_id"])
                remaining_capacity = max(0.0, capacity - carried_amount(conn, c["id"]))
                amount = min(float(job["amount"] or 0), float(dep["amount"] if dep else 0), remaining_capacity)
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
                    outcome = "no_yield"
                    message = f"{c['name']}'s extraction attempt produced no usable material."
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "fabricate":
                process = FABRICATION_PROCESSES.get(str(job["target"]))
                if process:
                    conn.execute(
                        """
                        INSERT INTO equipment
                        (template_id, name, kind, owner_citizen_id, location_id, condition,
                         extraction_speed_multiplier, cargo_bonus, created_job_id, created_minute)
                        VALUES (?, ?, ?, ?, ?, 100, ?, ?, ?, ?)
                        """,
                        (
                            str(job["target"]),
                            process["name"],
                            process["kind"],
                            c["id"],
                            c["location_id"],
                            float(process["extraction_speed_multiplier"]),
                            float(process["cargo_bonus"]),
                            int(job["id"]),
                            now,
                        ),
                    )
                    message = f"{c['name']} completed fabrication of a real {process['name']} at {c['location']}."
                else:
                    outcome = "failed"
                    message = f"{c['name']}'s fabrication job could not resolve its physical process."
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "plan_project":
                project_id = int(job["project_id"] or 0)
                project = conn.execute("SELECT name FROM projects WHERE id = ?", (project_id,)).fetchone()
                message = (
                    f"{c['name']} completed the plan for {project['name']} project #{project_id}."
                    if project else f"{c['name']} completed a construction planning job."
                )
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "reserve_project":
                project_id = int(job["project_id"] or 0)
                project = conn.execute("SELECT name FROM projects WHERE id = ?", (project_id,)).fetchone()
                message = (
                    f"{c['name']} staged and reserved materials for {project['name']} project #{project_id}."
                    if project else f"{c['name']} completed material staging."
                )
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "construct":
                project_id = int(job["project_id"] or 0)
                project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
                blueprint = CONSTRUCTION_BLUEPRINTS.get(project["blueprint_id"]) if project else None
                if project and blueprint and project["status"] == "underway":
                    structure_name = _unique_structure_name(conn, blueprint["name"])
                    cur = conn.execute(
                        """
                        INSERT INTO structures
                        (name, condition, location_id, x_km, y_km, kind, provides_charging, project_id)
                        VALUES (?, 100, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            structure_name,
                            project["location_id"],
                            project["x_km"],
                            project["y_km"],
                            blueprint["kind"],
                            int(blueprint["provides_charging"]),
                            project_id,
                        ),
                    )
                    structure_id = int(cur.lastrowid)
                    conn.execute(
                        """
                        UPDATE projects
                        SET status = 'complete', completed_minute = ?, active_job_id = NULL,
                            resulting_structure_id = ?
                        WHERE id = ?
                        """,
                        (now, structure_id, project_id),
                    )
                    message = f"{c['name']} completed {structure_name} at {location_name(conn, project['location_id'])}."
                else:
                    outcome = "failed"
                    if project:
                        conn.execute(
                            "UPDATE projects SET status = 'reserved', active_job_id = NULL WHERE id = ?",
                            (project_id,),
                        )
                    message = f"{c['name']}'s construction job ended without creating a structure."
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))

            elif action == "talk":
                target_id = job["target"]
                target_citizen = conn.execute("SELECT name FROM citizens WHERE id = ?", (target_id,)).fetchone()
                conn.execute(
                    """
                    UPDATE citizens
                    SET current_activity = 'Available', active_job_id = NULL
                    WHERE id IN (?, ?) AND active_job_id = ?
                    """,
                    (c["id"], target_id, job["id"]),
                )
                target_name = target_citizen["name"] if target_citizen else target_id
                message = f"{c['name']} and {target_name} finished talking at {c['location']}."

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
                "UPDATE jobs SET status = 'complete', outcome = ? WHERE id = ?",
                (outcome, job["id"]),
            )
            if message:
                add_history(conn, now, "activity", message)

        conn.commit()
