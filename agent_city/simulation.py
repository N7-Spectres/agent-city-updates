from __future__ import annotations

import json
import math
from typing import Any

from .db import add_history, connect, get_meta, set_meta
from .knowledge import citizen_knows_property, record_discovery

BASE_CARRY_CAPACITY = 20.0
RETURN_ENERGY_MARGIN = 5.0

MIN_OPERATIONAL_CONDITION = 20.0
SERVICE_DUE_CONDITION = 90.0
BATTERY_REPLACE_THRESHOLD = 85.0
CHASSIS_SERVICE_WEAR = 12.0
BATTERY_HEALTH_WEAR_PER_ENERGY = 0.003

PASSIVE_STRUCTURE_WEAR_PER_DAY = {
    "charger": 0.08,
    "workbench": 0.07,
    "smelter": 0.08,
    "storage": 0.03,
    "shelter": 0.04,
    "structure": 0.04,
}

# Generic starter assays are physical methods, not technologies or unlock nodes.
# Simulation knows which hidden property (if any) responds to each method; citizens do not.
EXPERIMENT_METHODS: dict[str, dict[str, Any]] = {
    "thermal_assay": {
        "label": "thermal-response assay",
        "duration": 120,
        "energy_cost": 5.0,
        "sample_amount": 1.0,
    },
    "electrical_assay": {
        "label": "electrical-response assay",
        "duration": 105,
        "energy_cost": 4.0,
        "sample_amount": 1.0,
    },
    "mechanical_assay": {
        "label": "mechanical-response assay",
        "duration": 90,
        "energy_cost": 4.0,
        "sample_amount": 1.0,
    },
}

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


def condition_factor(condition: float) -> float:
    if condition <= MIN_OPERATIONAL_CONDITION:
        return 0.0
    return max(0.0, min(1.0, condition / 100.0))


def condition_band(condition: float) -> str:
    if condition <= MIN_OPERATIONAL_CONDITION:
        return "critical"
    if condition < 60:
        return "degraded"
    if condition < SERVICE_DUE_CONDITION:
        return "service_due"
    return "nominal"


def structure_at(conn, name: str, location_id: str | None = None):
    if location_id is None:
        return conn.execute(
            "SELECT * FROM structures WHERE name = ? ORDER BY id LIMIT 1",
            (name,),
        ).fetchone()
    return conn.execute(
        """
        SELECT * FROM structures
        WHERE name = ? AND location_id = ?
        ORDER BY id LIMIT 1
        """,
        (name, location_id),
    ).fetchone()


def structure_operational(conn, name: str, location_id: str | None = None) -> bool:
    row = structure_at(conn, name, location_id)
    return bool(row and float(row["condition"]) > MIN_OPERATIONAL_CONDITION)


def structure_efficiency(conn, name: str, location_id: str | None = None) -> float:
    row = structure_at(conn, name, location_id)
    return condition_factor(float(row["condition"])) if row else 0.0


def equipment_service_requirements(condition: float) -> dict[str, float]:
    requirements: dict[str, float] = {"Lubricant": 1.0, "Fasteners": 1.0}
    if condition < 70:
        requirements["Mechanical components"] = 1.0
    if condition < 40:
        requirements["Mechanical components"] = 2.0
    return requirements


def structure_service_requirements(structure: Any) -> dict[str, float]:
    condition = float(structure["condition"])
    requirements: dict[str, float] = {"Lubricant": 1.0, "Fasteners": 2.0}
    if condition < 70:
        requirements["Processed structural material"] = 3.0
    if str(structure["kind"]) in {"charger", "workbench", "smelter"}:
        requirements["Mechanical components"] = 1.0
    if condition < 40:
        requirements["Processed structural material"] = (
            requirements.get("Processed structural material", 0.0) + 3.0
        )
        requirements["Mechanical components"] = (
            requirements.get("Mechanical components", 0.0) + 1.0
        )
    return requirements


def _maintenance_in_progress(conn, action: str, target: str) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM jobs
        WHERE status = 'active' AND action = ? AND target = ?
        LIMIT 1
        """,
        (action, str(target)),
    ).fetchone()
    return bool(row)


def _note_condition_transition(
    conn,
    now: int,
    entity_name: str,
    before: float,
    after: float,
) -> None:
    before_band = condition_band(before)
    after_band = condition_band(after)
    if before_band == after_band:
        return
    if after_band == "degraded":
        add_history(
            conn,
            now,
            "maintenance",
            f"{entity_name} entered degraded condition ({after:.0f}%).",
        )
    elif after_band == "critical":
        add_history(
            conn,
            now,
            "maintenance",
            f"{entity_name} became non-operational pending repair ({after:.0f}%).",
        )


def _wear_equipment(
    conn,
    citizen_id: str,
    kind: str,
    amount: float,
    now: int,
) -> None:
    rows = conn.execute(
        """
        SELECT * FROM equipment
        WHERE owner_citizen_id = ? AND kind = ?
        ORDER BY id
        """,
        (citizen_id, kind),
    ).fetchall()
    for item in rows:
        before = float(item["condition"])
        if before <= 0:
            continue
        after = max(0.0, before - amount)
        conn.execute(
            "UPDATE equipment SET condition = ?, use_count = use_count + 1 WHERE id = ?",
            (after, item["id"]),
        )
        _note_condition_transition(conn, now, str(item["name"]), before, after)


def _wear_structure(
    conn,
    structure_name: str,
    location_id: str,
    amount: float,
    now: int,
) -> None:
    structure = structure_at(conn, structure_name, location_id)
    if not structure:
        return
    before = float(structure["condition"])
    if before <= 0:
        return
    after = max(0.0, before - amount)
    conn.execute(
        "UPDATE structures SET condition = ?, use_count = use_count + 1 WHERE id = ?",
        (after, structure["id"]),
    )
    _note_condition_transition(conn, now, str(structure["name"]), before, after)


def apply_passive_wear(now: int) -> None:
    """
    Gradual structure aging while the city clock runs.

    Time does not advance while Agent City is closed, so passive wear does not
    silently accrue while the simulation is stopped.
    """
    with connect() as conn:
        last = int(get_meta(conn, "maintenance_wear_minute") or str(now))
        elapsed = max(0, now - last)
        if elapsed < 60:
            return

        days = elapsed / 1440.0
        rows = conn.execute("SELECT * FROM structures ORDER BY id").fetchall()
        for structure in rows:
            before = float(structure["condition"])
            if before <= 0:
                continue
            rate = PASSIVE_STRUCTURE_WEAR_PER_DAY.get(
                str(structure["kind"]),
                PASSIVE_STRUCTURE_WEAR_PER_DAY["structure"],
            )
            after = max(0.0, before - rate * days)
            if after == before:
                continue
            conn.execute(
                "UPDATE structures SET condition = ? WHERE id = ?",
                (after, structure["id"]),
            )
            _note_condition_transition(conn, now, str(structure["name"]), before, after)

        set_meta(conn, "maintenance_wear_minute", now)
        conn.commit()


def _apply_citizen_job_wear(conn, citizen: Any, job: Any, now: int) -> None:
    action = str(job["action"])
    if action in {"service_chassis", "replace_battery", "service_equipment", "service_structure"}:
        return

    energy_cost = 0.0
    joint_added = 0.0

    if action == "travel":
        distance = route_distance(conn, str(citizen["location_id"]), str(job["target"])) or 0.0
        energy_cost = max(2.0, distance * 3.0)
        joint_added = distance * 0.12
    elif action == "survey":
        energy_cost, joint_added = 8.0, 0.30
    elif action == "extract":
        energy_cost, joint_added = 7.0, 0.45
    elif action == "experiment":
        protocol = EXPERIMENT_METHODS.get(str(job["experiment_method"] or ""))
        energy_cost = float(protocol["energy_cost"]) if protocol else 4.0
        joint_added = 0.10
    elif action == "fabricate":
        process = FABRICATION_PROCESSES.get(str(job["target"]))
        energy_cost = float(process["energy_cost"]) if process else 4.0
        joint_added = 0.12
    elif action == "construct":
        project = conn.execute(
            "SELECT blueprint_id FROM projects WHERE id = ?",
            (job["project_id"],),
        ).fetchone()
        blueprint = CONSTRUCTION_BLUEPRINTS.get(project["blueprint_id"]) if project else None
        energy_cost = float(blueprint["energy_cost"]) if blueprint else 8.0
        joint_added = 0.30
    elif action == "talk":
        energy_cost, joint_added = 1.0, 0.01
    else:
        return

    current = conn.execute(
        "SELECT battery_health, joint_wear FROM citizens WHERE id = ?",
        (citizen["id"],),
    ).fetchone()
    if not current:
        return

    before_battery = float(current["battery_health"])
    before_joint = float(current["joint_wear"])
    after_battery = max(40.0, before_battery - energy_cost * BATTERY_HEALTH_WEAR_PER_ENERGY)
    after_joint = min(100.0, before_joint + joint_added)

    conn.execute(
        """
        UPDATE citizens
        SET battery_health = ?,
            energy = MIN(energy, ?),
            joint_wear = ?
        WHERE id = ?
        """,
        (after_battery, after_battery, after_joint, citizen["id"]),
    )

    if before_battery >= BATTERY_REPLACE_THRESHOLD > after_battery:
        add_history(
            conn,
            now,
            "maintenance",
            f"{citizen['name']}'s battery health reached the replacement-service range ({after_battery:.0f}%).",
        )
    if before_joint < CHASSIS_SERVICE_WEAR <= after_joint:
        add_history(
            conn,
            now,
            "maintenance",
            f"{citizen['name']}'s chassis accumulated enough joint wear to benefit from service.",
        )


def _apply_post_job_asset_wear(conn, citizen: Any, job: Any, now: int) -> None:
    action = str(job["action"])
    if action == "extract":
        _wear_equipment(conn, str(citizen["id"]), "extraction", 1.5, now)
    elif action == "travel" and carried_amount(conn, str(citizen["id"])) > 0:
        _wear_equipment(conn, str(citizen["id"]), "cargo", 0.35, now)
    elif action == "fabricate":
        _wear_structure(conn, "Basic Workbench", str(citizen["location_id"]), 0.35, now)
    elif action == "experiment":
        _wear_structure(conn, "Basic Workbench", str(citizen["location_id"]), 0.25, now)
    elif action == "charge":
        _wear_structure(conn, "Charging Station", str(citizen["location_id"]), 0.15, now)
    elif action == "deposit_cargo":
        _wear_structure(conn, "Storage Unit", str(citizen["location_id"]), 0.05, now)


def _record_maintenance_event(
    conn,
    *,
    job_id: int,
    citizen_id: str,
    event_type: str,
    target_type: str,
    target_id: str,
    before_value: float | None,
    after_value: float | None,
    materials: dict[str, float],
    outcome: str,
    now: int,
    summary: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO maintenance_events
        (job_id, citizen_id, event_type, target_type, target_id,
         before_value, after_value, materials_json, outcome, sim_minute, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            citizen_id,
            event_type,
            target_type,
            str(target_id),
            before_value,
            after_value,
            json.dumps(materials, sort_keys=True, separators=(",", ":")),
            outcome,
            now,
            summary[:1200],
        ),
    )
    event_id = int(cur.lastrowid)
    conn.execute(
        "UPDATE jobs SET maintenance_event_id = ? WHERE id = ?",
        (event_id, job_id),
    )
    return event_id


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
          AND condition > ?
          AND location_id IS NOT NULL
        """
    , (MIN_OPERATIONAL_CONDITION,)).fetchall()
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
        WHERE condition > ?
          AND (
              owner_citizen_id = ?
              OR (owner_citizen_id IS NULL AND location_id = ?)
          )
        ORDER BY id
        """,
        (MIN_OPERATIONAL_CONDITION, citizen_id, location_id),
    ).fetchall()
    return [dict(row) for row in rows]


def cargo_capacity(conn, citizen_id: str, location_id: str) -> float:
    bonus = sum(
        float(item["cargo_bonus"] or 0) * condition_factor(float(item["condition"]))
        for item in available_equipment(conn, citizen_id, location_id)
    )
    return BASE_CARRY_CAPACITY + bonus


def extraction_speed_multiplier(conn, citizen_id: str, location_id: str) -> float:
    multipliers = []
    for item in available_equipment(conn, citizen_id, location_id):
        base = float(item["extraction_speed_multiplier"] or 1.0)
        if base <= 1.0:
            continue
        factor = condition_factor(float(item["condition"]))
        multipliers.append(1.0 + (base - 1.0) * factor)
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

        if location_id in charging_locations(conn) and energy < 95:
            actions.append({
                "action": "charge",
                "target": location_id,
                "label": f"Recharge at an operational charging structure here at {location_name(conn, location_id)}.",
            })

        if location_id == "seed_site":
            if cargo > 0 and structure_operational(conn, "Storage Unit", location_id):
                actions.append({
                    "action": "deposit_cargo",
                    "target": "seed_site",
                    "label": f"Deposit {cargo:g} carried material into Seed Site storage.",
                })

            if float(c["joint_wear"] or 0) >= CHASSIS_SERVICE_WEAR:
                requirements = {"Lubricant": 1.0}
                if resources_available(conn, requirements):
                    actions.append({
                        "action": "service_chassis",
                        "target": citizen_id,
                        "label": (
                            f"Service chassis joints with lubricant "
                            f"(current joint wear {float(c['joint_wear']):.0f}%)."
                        ),
                    })

            if float(c["battery_health"] or 100) < BATTERY_REPLACE_THRESHOLD:
                requirements = {"Battery cells": 4.0, "Mechanical components": 2.0}
                if resources_available(conn, requirements):
                    actions.append({
                        "action": "replace_battery",
                        "target": citizen_id,
                        "label": (
                            f"Replace the degraded battery pack "
                            f"(health {float(c['battery_health']):.0f}%)."
                        ),
                    })

            equipment_rows = conn.execute(
                """
                SELECT *
                FROM equipment
                WHERE owner_citizen_id = ? AND condition < ?
                ORDER BY condition, id
                LIMIT 3
                """,
                (citizen_id, SERVICE_DUE_CONDITION),
            ).fetchall()
            for item in equipment_rows:
                target_id = str(item["id"])
                requirements = equipment_service_requirements(float(item["condition"]))
                if (
                    resources_available(conn, requirements)
                    and not _maintenance_in_progress(conn, "service_equipment", target_id)
                ):
                    actions.append({
                        "action": "service_equipment",
                        "target": target_id,
                        "label": (
                            f"Service {item['name']} "
                            f"(condition {float(item['condition']):.0f}%)."
                        ),
                    })

            structure = conn.execute(
                """
                SELECT *
                FROM structures
                WHERE location_id = ? AND condition < ?
                ORDER BY condition, id
                LIMIT 1
                """,
                (location_id, SERVICE_DUE_CONDITION),
            ).fetchone()
            if structure:
                target_id = str(structure["id"])
                requirements = structure_service_requirements(structure)
                if (
                    resources_available(conn, requirements)
                    and not _maintenance_in_progress(conn, "service_structure", target_id)
                ):
                    actions.append({
                        "action": "service_structure",
                        "target": target_id,
                        "label": (
                            f"Service {structure['name']} "
                            f"(condition {float(structure['condition']):.0f}%)."
                        ),
                    })

            workbench_ok = structure_operational(conn, "Basic Workbench", location_id)
            if workbench_ok:
                assay_materials = conn.execute(
                    """
                    SELECT DISTINCT wp.subject_id AS material
                    FROM world_properties wp
                    JOIN resources r ON r.name = wp.subject_id
                    WHERE wp.subject_type = 'material'
                      AND r.amount >= 1
                    ORDER BY wp.subject_id
                    """
                ).fetchall()
                for row in assay_materials:
                    for method_id, method in EXPERIMENT_METHODS.items():
                        if action_energy_safe(conn, location_id, energy, float(method["energy_cost"])):
                            material_name = str(row["material"])
                            actions.append({
                                "action": "experiment",
                                "target": f"{method_id}:{material_name}",
                                "material": material_name,
                                "experiment_method": method_id,
                                "label": (
                                    f"Run a {method['label']} on "
                                    f"{method['sample_amount']:g} unit of stored {material_name}."
                                ),
                            })

                for process_id, process in FABRICATION_PROCESSES.items():
                    already_owned = conn.execute(
                        """
                        SELECT 1 FROM equipment
                        WHERE template_id = ? AND owner_citizen_id = ? AND condition > ?
                        LIMIT 1
                        """,
                        (process_id, citizen_id, MIN_OPERATIONAL_CONDITION),
                    ).fetchone()
                    if not already_owned and resources_available(conn, process["materials"]) and action_energy_safe(
                        conn, location_id, energy, float(process["energy_cost"])
                    ):
                        actions.append({
                            "action": "fabricate",
                            "target": process_id,
                            "label": f"Fabricate one {process['name']} at the Basic Workbench.",
                        })

            for blueprint_id, blueprint in CONSTRUCTION_BLUEPRINTS.items():
                unfinished = conn.execute(
                    """
                    SELECT 1 FROM projects
                    WHERE blueprint_id = ? AND location_id = ? AND status != 'complete'
                    LIMIT 1
                    """,
                    (blueprint_id, location_id),
                ).fetchone()
                if not unfinished:
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
            if loc and action_energy_safe(conn, location_id, energy, 8.0):
                survey_label = (
                    f"Repeat a field survey of {loc['name']} for additional validated observations."
                    if loc["surveyed"]
                    else f"Survey {loc['name']} for geological or biological material."
                )
                actions.append({"action": "survey", "target": location_id, "label": survey_label})

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
        experiment_method = None

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

        elif action == "service_chassis":
            if c["location_id"] != "seed_site" or float(c["joint_wear"] or 0) < CHASSIS_SERVICE_WEAR:
                return False, "Chassis service is not currently required or available here."
            requirements = {"Lubricant": 1.0}
            if not consume_resources(conn, requirements):
                return False, "Required lubricant is no longer available."
            before = float(c["joint_wear"] or 0)
            duration = 60
            detail = json.dumps(
                {
                    "maintenance": "chassis_service",
                    "before": before,
                    "materials": requirements,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            activity = "Servicing chassis joints"

        elif action == "replace_battery":
            if c["location_id"] != "seed_site" or float(c["battery_health"] or 100) >= BATTERY_REPLACE_THRESHOLD:
                return False, "Battery replacement is not currently required or available here."
            requirements = {"Battery cells": 4.0, "Mechanical components": 2.0}
            if not consume_resources(conn, requirements):
                return False, "Required battery replacement parts are no longer available."
            before = float(c["battery_health"] or 0)
            duration = 120
            detail = json.dumps(
                {
                    "maintenance": "battery_replacement",
                    "before": before,
                    "materials": requirements,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            activity = "Replacing battery pack"

        elif action == "service_equipment":
            if c["location_id"] != "seed_site":
                return False, "Equipment service currently requires the Seed Site workshop."
            item = conn.execute(
                "SELECT * FROM equipment WHERE id = ? AND owner_citizen_id = ?",
                (int(target), citizen_id),
            ).fetchone()
            if not item or float(item["condition"]) >= SERVICE_DUE_CONDITION:
                return False, "That equipment does not currently require service."
            requirements = equipment_service_requirements(float(item["condition"]))
            if not consume_resources(conn, requirements):
                return False, "Required equipment service materials are no longer available."
            before = float(item["condition"])
            severity = max(0.0, 100.0 - before)
            duration = 60 + int(severity * 0.6)
            detail = json.dumps(
                {
                    "maintenance": "equipment_service",
                    "equipment_id": int(item["id"]),
                    "before": before,
                    "materials": requirements,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            activity = f"Servicing {item['name']}"

        elif action == "service_structure":
            structure = conn.execute(
                "SELECT * FROM structures WHERE id = ?",
                (int(target),),
            ).fetchone()
            if (
                not structure
                or structure["location_id"] != c["location_id"]
                or c["location_id"] != "seed_site"
                or float(structure["condition"]) >= SERVICE_DUE_CONDITION
            ):
                return False, "That structure does not currently require service here."
            requirements = structure_service_requirements(structure)
            if not consume_resources(conn, requirements):
                return False, "Required structure service materials are no longer available."
            before = float(structure["condition"])
            severity = max(0.0, 100.0 - before)
            duration = 90 + int(severity * 0.8)
            detail = json.dumps(
                {
                    "maintenance": "structure_service",
                    "structure_id": int(structure["id"]),
                    "before": before,
                    "materials": requirements,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            activity = f"Servicing {structure['name']}"

        elif action == "experiment":
            experiment_method = str(chosen.get("experiment_method") or "")
            protocol = EXPERIMENT_METHODS.get(experiment_method)
            material = str(chosen.get("material") or "")
            if not protocol or not material or c["location_id"] != "seed_site":
                return False, "That experiment is not physically available here."
            if not action_energy_safe(
                conn,
                c["location_id"],
                float(c["energy"]),
                float(protocol["energy_cost"]),
            ):
                return False, "That experiment would leave insufficient energy reserve."
            sample_amount = float(protocol["sample_amount"])
            if not consume_resources(conn, {material: sample_amount}):
                return False, "The required physical sample is no longer available."
            workbench_efficiency = structure_efficiency(conn, "Basic Workbench", c["location_id"])
            if workbench_efficiency <= 0:
                return False, "The Basic Workbench is not operational."
            duration = max(
                int(protocol["duration"]),
                int(round(float(protocol["duration"]) / workbench_efficiency)),
            )
            conn.execute(
                "UPDATE citizens SET energy = MAX(0, energy - ?) WHERE id = ?",
                (float(protocol["energy_cost"]), citizen_id),
            )
            detail = "experiment:" + json.dumps(
                {"method": experiment_method, "material": material, "sample": sample_amount},
                separators=(",", ":"),
            )
            activity = f"Testing {material} with a {protocol['label']}"

        elif action == "fabricate":
            process = FABRICATION_PROCESSES.get(str(target))
            if not process or c["location_id"] != "seed_site":
                return False, "That fabrication process is not available here."
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), float(process["energy_cost"])):
                return False, "Fabrication would leave insufficient return-energy reserve."
            if not consume_resources(conn, process["materials"]):
                return False, "Required fabrication materials are no longer available."
            workbench_efficiency = structure_efficiency(conn, "Basic Workbench", c["location_id"])
            if workbench_efficiency <= 0:
                return False, "The Basic Workbench is not operational."
            duration = max(
                int(process["duration"]),
                int(round(float(process["duration"]) / workbench_efficiency)),
            )
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
            if c["location_id"] not in charging_locations(conn):
                return False, "No operational charging structure is available here."
            charger_efficiency = structure_efficiency(conn, "Charging Station", c["location_id"])
            if charger_efficiency <= 0:
                return False, "No operational charging structure is available here."
            duration = max(60, int(round(60 / charger_efficiency)))
            detail = f"charge:{c['location_id']}"
            activity = f"Charging at {location_name(conn, c['location_id'])}"

        else:
            duration = 45
            detail = "wait"
            activity = "Observing surroundings"

        cur = conn.execute(
            """
            INSERT INTO jobs
            (citizen_id, action, target, material, amount, start_minute, end_minute,
             status, detail, intent_reason, project_id, experiment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
            """,
            (
                citizen_id, action, target, material, amount, now, now + duration,
                detail, intent_reason, project_id, experiment_method,
            ),
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
            job_status = "complete"
            outcome = "success"

            if action == "service_chassis":
                payload = json.loads(job["detail"] or "{}")
                before = float(payload.get("before", c["joint_wear"] or 0))
                materials = dict(payload.get("materials") or {})
                conn.execute(
                    """
                    UPDATE citizens
                    SET joint_wear = 0, last_service_minute = ?,
                        current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (now, c["id"]),
                )
                message = f"{c['name']} completed chassis lubrication and joint service."
                _record_maintenance_event(
                    conn,
                    job_id=int(job["id"]),
                    citizen_id=str(c["id"]),
                    event_type="chassis_service",
                    target_type="citizen",
                    target_id=str(c["id"]),
                    before_value=before,
                    after_value=0.0,
                    materials=materials,
                    outcome="success",
                    now=now,
                    summary=message,
                )

            elif action == "replace_battery":
                payload = json.loads(job["detail"] or "{}")
                before = float(payload.get("before", c["battery_health"] or 0))
                materials = dict(payload.get("materials") or {})
                conn.execute(
                    """
                    UPDATE citizens
                    SET battery_health = 100,
                        energy = MIN(energy, 100),
                        last_service_minute = ?,
                        current_activity = 'Available',
                        active_job_id = NULL
                    WHERE id = ?
                    """,
                    (now, c["id"]),
                )
                message = f"{c['name']} completed a battery-pack replacement."
                _record_maintenance_event(
                    conn,
                    job_id=int(job["id"]),
                    citizen_id=str(c["id"]),
                    event_type="battery_replacement",
                    target_type="citizen",
                    target_id=str(c["id"]),
                    before_value=before,
                    after_value=100.0,
                    materials=materials,
                    outcome="success",
                    now=now,
                    summary=message,
                )

            elif action == "service_equipment":
                payload = json.loads(job["detail"] or "{}")
                equipment_id = int(payload.get("equipment_id") or job["target"] or 0)
                before = float(payload.get("before", 0))
                materials = dict(payload.get("materials") or {})
                item = conn.execute(
                    "SELECT * FROM equipment WHERE id = ?",
                    (equipment_id,),
                ).fetchone()
                if item:
                    conn.execute(
                        """
                        UPDATE equipment
                        SET condition = 100, last_service_minute = ?
                        WHERE id = ?
                        """,
                        (now, equipment_id),
                    )
                    message = f"{c['name']} restored {item['name']} to full service condition."
                    _record_maintenance_event(
                        conn,
                        job_id=int(job["id"]),
                        citizen_id=str(c["id"]),
                        event_type="equipment_service",
                        target_type="equipment",
                        target_id=str(equipment_id),
                        before_value=before,
                        after_value=100.0,
                        materials=materials,
                        outcome="success",
                        now=now,
                        summary=message,
                    )
                else:
                    job_status = "failed"
                    outcome = "failed"
                    message = f"{c['name']}'s equipment service ended because the target equipment no longer existed."
                conn.execute(
                    "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                    (c["id"],),
                )

            elif action == "service_structure":
                payload = json.loads(job["detail"] or "{}")
                structure_id = int(payload.get("structure_id") or job["target"] or 0)
                before = float(payload.get("before", 0))
                materials = dict(payload.get("materials") or {})
                structure = conn.execute(
                    "SELECT * FROM structures WHERE id = ?",
                    (structure_id,),
                ).fetchone()
                if structure:
                    conn.execute(
                        """
                        UPDATE structures
                        SET condition = 100, last_service_minute = ?
                        WHERE id = ?
                        """,
                        (now, structure_id),
                    )
                    message = f"{c['name']} restored {structure['name']} to full service condition."
                    _record_maintenance_event(
                        conn,
                        job_id=int(job["id"]),
                        citizen_id=str(c["id"]),
                        event_type="structure_service",
                        target_type="structure",
                        target_id=str(structure_id),
                        before_value=before,
                        after_value=100.0,
                        materials=materials,
                        outcome="success",
                        now=now,
                        summary=message,
                    )
                else:
                    job_status = "failed"
                    outcome = "failed"
                    message = f"{c['name']}'s structure service ended because the target structure no longer existed."
                conn.execute(
                    "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                    (c["id"],),
                )

            elif action == "travel":
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
                findings: list[str] = []

                # A repeat survey may independently confirm a deposit that another
                # citizen found earlier, or reveal a deposit still hidden globally.
                dep = conn.execute(
                    """
                    SELECT d.*
                    FROM deposits d
                    WHERE d.location_id = ?
                      AND d.amount > 0
                      AND NOT EXISTS (
                          SELECT 1
                          FROM citizen_knowledge ck
                          JOIN discoveries dx ON dx.id = ck.discovery_id
                          WHERE ck.citizen_id = ?
                            AND dx.discovery_kind = 'deposit'
                            AND dx.subject_id = d.id
                      )
                    ORDER BY d.discovered ASC, d.id
                    LIMIT 1
                    """,
                    (loc_id, c["id"]),
                ).fetchone()
                if dep:
                    if not dep["discovered"]:
                        conn.execute(
                            """
                            UPDATE deposits
                            SET discovered = 1, discoverer_id = ?, discovered_minute = ?
                            WHERE id = ?
                            """,
                            (c["id"], now, dep["id"]),
                        )
                    discovery_id = record_discovery(
                        conn,
                        discovery_kind="deposit",
                        subject_type="deposit",
                        subject_id=str(dep["id"]),
                        citizen_id=str(c["id"]),
                        location_id=str(loc_id),
                        source_job_id=int(job["id"]),
                        discovered_minute=now,
                        summary=f"Confirmed deposit of {dep['material']} at {loc_name}.",
                        acquisition_kind="direct_survey",
                    )
                    findings.append(f"confirmed a deposit of {dep['material']} (discovery #{discovery_id})")

                prop = None
                for candidate in conn.execute(
                    """
                    SELECT *
                    FROM world_properties
                    WHERE subject_type = 'location'
                      AND subject_id = ?
                      AND assay_method = 'field_survey'
                    ORDER BY id
                    """,
                    (loc_id,),
                ).fetchall():
                    if not citizen_knows_property(conn, str(c["id"]), str(candidate["id"])):
                        prop = candidate
                        break

                if prop:
                    discovery_id = record_discovery(
                        conn,
                        discovery_kind="world_property",
                        subject_type="location",
                        subject_id=str(loc_id),
                        property_id=str(prop["id"]),
                        citizen_id=str(c["id"]),
                        location_id=str(loc_id),
                        source_job_id=int(job["id"]),
                        discovered_minute=now,
                        summary=f"{loc_name}: {prop['property_key']} — {prop['value_text']}.",
                        acquisition_kind="direct_survey",
                    )
                    findings.append(
                        f"recorded {prop['property_key']}: {prop['value_text']} (discovery #{discovery_id})"
                    )

                if findings:
                    message = f"{c['name']} surveyed {loc_name} and " + "; ".join(findings) + "."
                else:
                    outcome = "no_new_finding"
                    message = f"{c['name']} completed a survey of {loc_name}; it produced no new validated finding."
                conn.execute(
                    "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                    (c["id"],),
                )

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

            elif action == "experiment":
                method = str(job["experiment_method"] or "")
                material_name = str(job["material"] or "")
                protocol = EXPERIMENT_METHODS.get(method)
                matching = conn.execute(
                    """
                    SELECT *
                    FROM world_properties
                    WHERE subject_type = 'material'
                      AND subject_id = ?
                      AND assay_method = ?
                    ORDER BY id
                    """,
                    (material_name, method),
                ).fetchall()

                new_property = None
                for candidate in matching:
                    if not citizen_knows_property(conn, str(c["id"]), str(candidate["id"])):
                        new_property = candidate
                        break

                discovery_id = None
                if new_property:
                    discovery_id = record_discovery(
                        conn,
                        discovery_kind="world_property",
                        subject_type="material",
                        subject_id=material_name,
                        property_id=str(new_property["id"]),
                        citizen_id=str(c["id"]),
                        location_id=str(c["location_id"]),
                        source_job_id=int(job["id"]),
                        discovered_minute=now,
                        summary=(
                            f"{material_name}: {new_property['property_key']} — "
                            f"{new_property['value_text']}."
                        ),
                        acquisition_kind="direct_experiment",
                    )
                    outcome = "discovery"
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO learned_processes
                        (citizen_id, process_key, name, process_kind, source_discovery_id, learned_minute)
                        VALUES (?, ?, ?, 'verification', ?, ?)
                        """,
                        (
                            c["id"],
                            f"verify:{new_property['id']}",
                            (
                                f"Repeatable {protocol['label'] if protocol else method} "
                                f"for {material_name}"
                            ),
                            discovery_id,
                            now,
                        ),
                    )
                    summary = (
                        f"{c['name']} discovered {new_property['property_key']} in {material_name}: "
                        f"{new_property['value_text']}."
                    )
                    message = summary + f" Discovery #{discovery_id} is now a validated knowledge anchor."
                elif matching:
                    outcome = "verified"
                    summary = (
                        f"{c['name']} repeated the {protocol['label'] if protocol else method} "
                        f"on {material_name} and reproduced a property already known to them."
                    )
                    message = summary
                else:
                    outcome = "inconclusive"
                    summary = (
                        f"{c['name']}'s {protocol['label'] if protocol else method} on "
                        f"{material_name} produced no validated new property."
                    )
                    message = summary

                cur_result = conn.execute(
                    """
                    INSERT INTO experiment_results
                    (job_id, citizen_id, location_id, material, method, outcome,
                     discovery_id, summary, completed_minute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(job["id"]), c["id"], c["location_id"], material_name, method,
                        outcome, discovery_id, summary, now,
                    ),
                )
                if discovery_id is not None:
                    conn.execute(
                        "UPDATE jobs SET result_discovery_id = ? WHERE id = ?",
                        (discovery_id, job["id"]),
                    )
                conn.execute(
                    "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                    (c["id"],),
                )

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
                    outcome = "failed"
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
                "UPDATE jobs SET status = ?, outcome = ? WHERE id = ?",
                (job_status, outcome, job["id"]),
            )
            if message:
                add_history(conn, now, "activity", message)

        conn.commit()
