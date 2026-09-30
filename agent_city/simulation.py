from __future__ import annotations

import json
import math
from typing import Any

from .db import add_history, connect, get_meta, set_meta
from .knowledge import citizen_knows_property, record_discovery
from .spatial import query_hidden_world, record_validated_observation
from .exploration import (
    DIRECT_INSPECTION_RADIUS_M,
    LOCAL_MOVE_MAX_M,
    path_profile as local_path_profile,
    return_energy_from_coordinate,
    start_local_inspection,
    start_local_move as start_local_move_job,
)
from .talk_diagnostics import concise_failure_code_from_conn
from .continuity import (
    attach_job_to_plan,
    record_plan_job_outcome,
    record_practice_event_for_job,
)
from .competence import (
    best_guided_practice_option,
    consume_guidance_for_job,
    duration_effect_for_action,
    start_guided_practice,
)

BASE_CARRY_CAPACITY = 20.0
RETURN_ENERGY_MARGIN = 5.0

DAILY_ACTIVE_START_MINUTE = 6 * 60
DAILY_WIND_DOWN_START_MINUTE = 20 * 60
DAILY_QUIET_START_MINUTE = 22 * 60
CRITICAL_RECHARGE_ENERGY = 35.0
NIGHT_RETURN_ENERGY = 60.0
CHARGE_FULL_EPSILON = 0.5

# Stage 3 voluntary-pattern evidence is deliberately conservative. These are
# ordinary autonomous choices that may reflect repeated history when the
# citizen had multiple legal options. Survival, movement, maintenance, cargo
# handling, guided-practice mechanics, and plan-bound work are excluded.
VOLUNTARY_PATTERN_ACTIONS = {
    "survey",
    "extract",
    "experiment",
    "fabricate",
    "plan_project",
    "construct",
    "talk",
}

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


def minute_of_day(sim_minute: int) -> int:
    return int(sim_minute) % 1440


def daily_phase(sim_minute: int) -> str:
    minute = minute_of_day(sim_minute)
    if minute < DAILY_ACTIVE_START_MINUTE or minute >= DAILY_QUIET_START_MINUTE:
        return "quiet"
    if minute >= DAILY_WIND_DOWN_START_MINUTE:
        return "wind_down"
    return "active"


def daily_phase_label(sim_minute: int) -> str:
    return {
        "active": "Active cycle (06:00–20:00)",
        "wind_down": "Wind-down cycle (20:00–22:00)",
        "quiet": "Low-activity / recharge cycle (22:00–06:00)",
    }[daily_phase(sim_minute)]


def voluntary_choice_context_key(citizen: Any, sim_minute: int) -> str:
    """Deterministic runtime context for Stage 3 repeated-choice evidence."""
    try:
        location_id = str(citizen["location_id"])
    except (KeyError, TypeError):
        location_id = "unknown"
    return f"location:{location_id}|phase:{daily_phase(sim_minute)}|open_choice"


def _voluntary_choice_provenance(
    citizen: Any,
    *,
    action: str,
    sim_minute: int,
    intent_reason: str | None,
    plan_id: int | None,
    autonomous_choice: bool,
    autonomous_action_count: int,
) -> tuple[int, str | None, str | None]:
    """
    Classify a planner-selected job for Stage 3 historical pattern evidence.

    This is intentionally stricter than physical legality. A choice counts only
    when the autonomous planner had multiple options during the active cycle,
    supplied a reason, selected an eligible ordinary action, and did not attach
    the job to a persistent plan.
    """
    if not autonomous_choice:
        return 0, None, None
    if int(autonomous_action_count or 0) < 2:
        return 0, None, None
    if daily_phase(sim_minute) != "active":
        return 0, None, None
    if action not in VOLUNTARY_PATTERN_ACTIONS:
        return 0, None, None
    if not str(intent_reason or "").strip():
        return 0, None, None
    if plan_id is not None:
        return 0, None, None

    try:
        location_id = str(citizen["location_id"])
    except (KeyError, TypeError):
        return 0, None, None
    return 1, voluntary_choice_context_key(citizen, sim_minute), location_id


def usable_energy_capacity(citizen: Any) -> float:
    try:
        health = float(citizen["battery_health"])
    except (KeyError, TypeError, ValueError):
        health = 100.0
    return max(0.0, min(100.0, health))


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


def charging_structure_at(conn, location_id: str):
    return conn.execute(
        """
        SELECT *
        FROM structures
        WHERE location_id = ?
          AND provides_charging = 1
          AND condition > ?
        ORDER BY condition DESC, id
        LIMIT 1
        """,
        (location_id, MIN_OPERATIONAL_CONDITION),
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
    elif action in {"local_move", "shared_local_activity"}:
        payload = json.loads(job["detail"] or "{}")
        energy_cost = float(payload.get("energy_cost", 0.2))
        joint_added = max(0.01, float(job["path_distance_m"] or 0.0) / 1000.0 * 0.12)
    elif action == "local_inspect":
        energy_cost, joint_added = 0.5, 0.02
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
    elif action in {"travel", "local_move", "shared_local_activity"} and carried_amount(conn, str(citizen["id"])) > 0:
        distance_m = (
            float(job["path_distance_m"] or 0.0)
            if action != "travel"
            else (route_distance(conn, str(citizen["location_id"]), str(job["target"])) or 0.0) * 1000.0
        )
        _wear_equipment(
            conn,
            str(citizen["id"]),
            "cargo",
            max(0.02, 0.35 * (distance_m / 1000.0)),
            now,
        )
    elif action == "fabricate":
        _wear_structure(conn, "Basic Workbench", str(citizen["location_id"]), 0.35, now)
    elif action == "experiment":
        _wear_structure(conn, "Basic Workbench", str(citizen["location_id"]), 0.25, now)
    elif action == "charge":
        charger = charging_structure_at(conn, str(citizen["location_id"]))
        if charger:
            before = float(charger["condition"])
            after = max(0.0, before - 0.15)
            conn.execute(
                "UPDATE structures SET condition = ?, use_count = use_count + 1 WHERE id = ?",
                (after, charger["id"]),
            )
            _note_condition_transition(conn, now, str(charger["name"]), before, after)
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


def query_spatial_truth(x_m: float, y_m: float) -> dict[str, Any]:
    """
    Simulation-only hidden query contract.

    Callers must never pass this raw payload directly to citizen/UI surfaces.
    Use a validated observation or another Simulation-owned transition instead.
    """
    with connect() as conn:
        payload = query_hidden_world(conn, x_m, y_m)
        conn.commit()
        return payload


def record_local_spatial_observation(
    citizen_id: str,
    x_m: float,
    y_m: float,
    *,
    observed_minute: int | None = None,
    source_job_id: int | None = None,
    max_range_m: float = 2.0,
    observation_kind: str = "field_observation",
    radius_m: float = 1.0,
) -> tuple[bool, int | None, str]:
    """
    Minimal Stage-1 action contract for future surveys/scanners/shared exploration.

    The caller supplies an already-validated physical range appropriate to the
    future action/tool. This function still enforces the observer's real position
    and persists only the safe observation, never the raw seed/chunk truth.
    """
    with connect() as conn:
        citizen = conn.execute(
            """
            SELECT c.id, c.name, c.position_x_m, c.position_y_m,
                   j.action AS active_action
            FROM citizens c
            LEFT JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()
        if not citizen:
            return False, None, "Citizen not found."

        if citizen["active_action"] == "travel":
            return False, None, "Citizen is traveling and cannot make a local stationary observation."

        if source_job_id is not None:
            source_job = conn.execute(
                "SELECT citizen_id FROM jobs WHERE id = ?",
                (int(source_job_id),),
            ).fetchone()
            if not source_job or str(source_job["citizen_id"]) != str(citizen_id):
                return False, None, "Observation source job does not belong to this citizen."

        cx = float(citizen["position_x_m"] or 0.0)
        cy = float(citizen["position_y_m"] or 0.0)
        distance = math.hypot(float(x_m) - cx, float(y_m) - cy)
        if distance > max(0.1, float(max_range_m)):
            return False, None, "Observation point is outside the validated physical range."

        now = (
            int(observed_minute)
            if observed_minute is not None
            else int(get_meta(conn, "sim_minute") or "360")
        )
        observation_id = record_validated_observation(
            conn,
            observer_id=citizen_id,
            x_m=float(x_m),
            y_m=float(y_m),
            observed_minute=now,
            source_job_id=source_job_id,
            observation_kind=observation_kind,
            radius_m=radius_m,
        )
        conn.commit()
        return True, observation_id, "Validated spatial observation recorded."


def location_anchor_distance(conn, citizen: Any) -> float:
    row = conn.execute(
        "SELECT x_m, y_m FROM locations WHERE id = ?",
        (citizen["location_id"],),
    ).fetchone()
    if not row or row["x_m"] is None or row["y_m"] is None:
        return 0.0
    return math.hypot(
        float(citizen["position_x_m"] or 0.0) - float(row["x_m"]),
        float(citizen["position_y_m"] or 0.0) - float(row["y_m"]),
    )


def has_intentional_local_offset(conn, citizen_id: str) -> bool:
    row = conn.execute(
        """
        SELECT action
        FROM jobs
        WHERE citizen_id = ?
          AND action IN ('travel', 'local_move', 'shared_local_activity')
          AND status = 'complete'
        ORDER BY end_minute DESC, id DESC
        LIMIT 1
        """,
        (citizen_id,),
    ).fetchone()
    return bool(row and row["action"] in ("local_move", "shared_local_activity"))


def nearby_operational_charger(conn, x_m: float, y_m: float, radius_m: float = 5.0):
    rows = conn.execute(
        """
        SELECT *
        FROM structures
        WHERE provides_charging = 1
          AND condition > ?
          AND x_m IS NOT NULL
          AND y_m IS NOT NULL
        ORDER BY id
        """,
        (MIN_OPERATIONAL_CONDITION,),
    ).fetchall()
    for row in rows:
        if math.hypot(float(row["x_m"]) - float(x_m), float(row["y_m"]) - float(y_m)) <= radius_m:
            return row
    return None


def recover_zero_energy_charger_deadlocks(now: int | None = None) -> list[str]:
    """
    Repair the narrow impossible state where an idle citizen has exactly zero
    energy inside a location that contains an operational charger, but their
    stored local coordinate is outside the charger's usable radius.

    This is diagnostic/admin recovery, not an in-world citizen action. It gives
    no energy and creates no job. The smallest correction is to align the
    stranded citizen's coordinate with the nearest charger at that same
    location, then make the citizen planner-eligible so ordinary charging can
    resume under the existing low-energy autonomy rule.
    """
    recovered: list[str] = []

    with connect() as conn:
        minute = (
            int(now)
            if now is not None
            else int(get_meta(conn, "sim_minute") or "360")
        )
        citizens = conn.execute(
            """
            SELECT *
            FROM citizens
            WHERE active_job_id IS NULL
              AND energy <= 0
            ORDER BY rowid
            """
        ).fetchall()

        for citizen in citizens:
            chargers = conn.execute(
                """
                SELECT *
                FROM structures
                WHERE provides_charging = 1
                  AND condition > ?
                  AND location_id = ?
                  AND x_m IS NOT NULL
                  AND y_m IS NOT NULL
                ORDER BY id
                """,
                (MIN_OPERATIONAL_CONDITION, citizen["location_id"]),
            ).fetchall()
            if not chargers:
                continue

            cx = float(citizen["position_x_m"] or 0.0)
            cy = float(citizen["position_y_m"] or 0.0)
            charger = min(
                chargers,
                key=lambda row: math.hypot(
                    float(row["x_m"]) - cx,
                    float(row["y_m"]) - cy,
                ),
            )
            distance = math.hypot(
                float(charger["x_m"]) - cx,
                float(charger["y_m"]) - cy,
            )
            if distance <= 5.0:
                continue

            eligible_minute = max(0, minute - 60)
            conn.execute(
                """
                UPDATE citizens
                SET position_x_m = ?,
                    position_y_m = ?,
                    current_activity = 'Available',
                    last_planned_minute = CASE
                        WHEN last_planned_minute IS NULL THEN ?
                        WHEN last_planned_minute > ? THEN ?
                        ELSE last_planned_minute
                    END
                WHERE id = ?
                """,
                (
                    float(charger["x_m"]),
                    float(charger["y_m"]),
                    eligible_minute,
                    eligible_minute,
                    eligible_minute,
                    citizen["id"],
                ),
            )
            add_history(
                conn,
                minute,
                "diagnostic",
                (
                    "Admin recovery corrected an impossible zero-energy charger "
                    f"offset for {citizen['name']} at "
                    f"{location_name(conn, citizen['location_id'])}; position "
                    f"was aligned to {charger['name']} so ordinary charging can resume."
                ),
            )
            recovered.append(str(citizen["id"]))

        conn.commit()

    return recovered


def citizens_physically_close(a: Any, b: Any, radius_m: float = 2.0) -> bool:
    return math.hypot(
        float(a["position_x_m"] or 0.0) - float(b["position_x_m"] or 0.0),
        float(a["position_y_m"] or 0.0) - float(b["position_y_m"] or 0.0),
    ) <= radius_m


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


def _is_homeward_action(action: dict[str, Any]) -> bool:
    if action.get("action") == "travel" and action.get("target") == "seed_site":
        return True
    if action.get("action") == "local_move" and str(action.get("label") or "").startswith("Return locally"):
        return True
    return False


def apply_daily_rhythm_to_actions(
    actions: list[dict[str, Any]],
    *,
    sim_minute: int,
    energy: float,
    usable_capacity: float,
) -> list[dict[str, Any]]:
    """Constrain new idle-citizen choices without cancelling active physical jobs."""
    phase = daily_phase(sim_minute)
    charge_actions = [a for a in actions if a.get("action") == "charge"]
    homeward_actions = [a for a in actions if _is_homeward_action(a)]
    wait_actions = [a for a in actions if a.get("action") == "wait"]

    # Survival has priority at every time of day. At a charger, critically low
    # citizens must recharge; away from one, they may only take a real homeward
    # movement that already passed Simulation legality/reserve checks.
    if energy < CRITICAL_RECHARGE_ENERGY:
        if charge_actions:
            return charge_actions
        if homeward_actions:
            return homeward_actions
        return wait_actions

    if phase == "quiet":
        # Once docked overnight, keep charging until the pack reaches its true
        # usable capacity (battery health), not an arbitrary 95% threshold.
        if charge_actions and energy < usable_capacity - CHARGE_FULL_EPSILON:
            return charge_actions

        # Mid-low citizens away from a charger should stop extending the workday.
        if energy < NIGHT_RETURN_ENERGY and homeward_actions:
            return homeward_actions

        quiet_allowed = {
            "charge",
            "deposit_cargo",
            "service_chassis",
            "replace_battery",
            "service_equipment",
            "service_structure",
            "talk",
            "wait",
        }
        filtered: list[dict[str, Any]] = []
        for action in actions:
            kind = action.get("action")
            if kind in quiet_allowed or _is_homeward_action(action):
                filtered.append(action)
        return filtered or wait_actions

    if phase == "wind_down":
        # Finish what is already underway, but idle citizens do not launch new
        # expeditions, extraction, research, fabrication, or construction.
        filtered = []
        blocked = {
            "survey",
            "extract",
            "experiment",
            "fabricate",
            "construct",
            "plan_project",
            "reserve_project",
            "guided_practice",
        }
        for action in actions:
            kind = action.get("action")
            if kind in blocked:
                continue
            if kind == "travel" and action.get("target") != "seed_site":
                continue
            if kind == "local_move" and not _is_homeward_action(action):
                continue
            filtered.append(action)
        return filtered or wait_actions

    return actions


def possible_actions(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        c = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not c or c["active_job_id"] is not None:
            return []

        actions: list[dict[str, Any]] = []
        location_id = c["location_id"]
        energy = float(c["energy"])
        now = int(get_meta(conn, "sim_minute") or "360")
        usable_capacity = usable_energy_capacity(c)
        cargo = carried_amount(conn, citizen_id)
        capacity = cargo_capacity(conn, citizen_id, location_id)
        x_m = float(c["position_x_m"] or 0.0)
        y_m = float(c["position_y_m"] or 0.0)
        anchor_distance = location_anchor_distance(conn, c)
        at_landmark = anchor_distance <= 5.0
        route_departure_ready = at_landmark or not has_intentional_local_offset(conn, citizen_id)

        charger_here = nearby_operational_charger(conn, x_m, y_m)
        charger_is_here = bool(
            charger_here
            and str(charger_here["location_id"]) == str(location_id)
        )
        if charger_is_here and energy < usable_capacity - CHARGE_FULL_EPSILON:
            actions.append({
                "action": "charge",
                "target": str(charger_here["id"]),
                "label": f"Recharge at {charger_here['name']} here.",
            })

        # Baseline local exploration choices reveal no hidden terrain/result data.
        if energy >= 1.0:
            for dx, dy, direction in (
                (60.0, 0.0, "east"),
                (-60.0, 0.0, "west"),
                (0.0, 60.0, "north"),
                (0.0, -60.0, "south"),
            ):
                tx, ty = x_m + dx, y_m + dy
                profile = local_path_profile(conn, x_m, y_m, tx, ty)
                reserve = return_energy_from_coordinate(conn, tx, ty)
                if reserve is not None and energy - float(profile["energy_cost"]) >= reserve:
                    actions.append({
                        "action": "local_move",
                        "target": f"{tx:.3f},{ty:.3f}",
                        "target_x_m": tx,
                        "target_y_m": ty,
                        "label": f"Explore locally about 60 m {direction}.",
                    })

            if not at_landmark:
                loc = conn.execute("SELECT x_m, y_m, name FROM locations WHERE id = ?", (location_id,)).fetchone()
                if loc:
                    actions.append({
                        "action": "local_move",
                        "target": f"{float(loc['x_m']):.3f},{float(loc['y_m']):.3f}",
                        "target_x_m": float(loc["x_m"]),
                        "target_y_m": float(loc["y_m"]),
                        "label": f"Return locally to the {loc['name']} landmark.",
                    })

        if energy >= 0.5:
            actions.append({
                "action": "local_inspect",
                "target": "current_position",
                "label": "Inspect the immediate surroundings directly.",
            })

        if location_id == "seed_site" and at_landmark:
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
                WHERE condition < ?
                  AND (
                      owner_citizen_id = ?
                      OR (owner_citizen_id IS NULL AND location_id = ?)
                  )
                ORDER BY condition, id
                """,
                (SERVICE_DUE_CONDITION, citizen_id, location_id),
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

            structures_due = conn.execute(
                """
                SELECT *
                FROM structures
                WHERE location_id = ? AND condition < ?
                ORDER BY condition, id
                """,
                (location_id, SERVICE_DUE_CONDITION),
            ).fetchall()
            for structure in structures_due:
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
                    break

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

        if cargo <= 0 and route_departure_ready:
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

        # Face-to-face conversation requires actual meter-scale proximity.
        if energy >= 5:
            others = conn.execute(
                """
                SELECT *
                FROM citizens
                WHERE location_id = ? AND id != ? AND active_job_id IS NULL
                ORDER BY rowid
                """,
                (location_id, citizen_id),
            ).fetchall()
            for other in others:
                if not citizens_physically_close(c, other):
                    continue
                actions.append({
                    "action": "talk",
                    "target": other["id"],
                    "label": f"Talk face-to-face with {other['name']} here.",
                })
                guidance = best_guided_practice_option(conn, citizen_id, other["id"])
                if guidance and energy >= 5:
                    family = str(guidance["family"])
                    actions.append({
                        "action": "guided_practice",
                        "target": f"{other['id']}:{family}",
                        "learner_id": other["id"],
                        "activity_family": family,
                        "label": (
                            f"Guide {other['name']} through a short {family} practice session."
                        ),
                    })

        actions.append({"action": "wait", "target": location_id, "label": "Remain where you are and observe for a while."})
        return actions


def _filter_autonomous_social_targets(
    conn,
    actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Protect critically low citizens from autonomous social interruption.

    This is an autonomy/rhythm constraint, not physical illegality. A citizen
    below the critical recharge threshold should get a chance to recharge
    instead of being repeatedly selected as somebody else's talk or guided-
    practice target.
    """
    filtered: list[dict[str, Any]] = []
    for item in actions:
        kind = str(item.get("action") or "")
        counterpart_id: str | None = None
        if kind == "talk":
            counterpart_id = str(item.get("target") or "")
        elif kind == "guided_practice":
            counterpart_id = str(item.get("learner_id") or "")

        if counterpart_id:
            counterpart = conn.execute(
                "SELECT energy FROM citizens WHERE id = ?",
                (counterpart_id,),
            ).fetchone()
            if (
                counterpart
                and float(counterpart["energy"]) < CRITICAL_RECHARGE_ENERGY
            ):
                continue

        filtered.append(item)
    return filtered


def autonomous_actions(citizen_id: str) -> list[dict[str, Any]]:
    """Physically legal actions filtered by the citizen's daily autonomy rhythm."""
    actions = possible_actions(citizen_id)
    if not actions:
        return []
    with connect() as conn:
        citizen = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not citizen or citizen["active_job_id"] is not None:
            return []
        now = int(get_meta(conn, "sim_minute") or "360")
        actions = _filter_autonomous_social_targets(conn, actions)
        return apply_daily_rhythm_to_actions(
            actions,
            sim_minute=now,
            energy=float(citizen["energy"]),
            usable_capacity=usable_energy_capacity(citizen),
        )


def start_action(
    citizen_id: str,
    request: dict[str, Any],
    *,
    autonomous_choice: bool = False,
    autonomous_action_count: int = 0,
) -> tuple[bool, str]:
    # Daily rhythm is an autonomy/planning constraint, not a new law of physics.
    # Direct Simulation calls remain valid when the requested action is otherwise
    # physically legal; critical-energy survival is still enforced below.
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

        if autonomous_choice and action in {"talk", "guided_practice"}:
            counterpart_id = (
                str(chosen.get("learner_id") or "")
                if action == "guided_practice"
                else str(target or "")
            )
            counterpart = conn.execute(
                "SELECT energy FROM citizens WHERE id = ?",
                (counterpart_id,),
            ).fetchone()
            if (
                counterpart
                and float(counterpart["energy"]) < CRITICAL_RECHARGE_ENERGY
            ):
                return False, (
                    "That citizen has critically low energy and needs a chance "
                    "to recharge before an autonomous social activity."
                )

        if float(c["energy"]) < CRITICAL_RECHARGE_ENERGY:
            if action not in {"charge", "wait"} and not _is_homeward_action(chosen):
                return False, "Energy is critically low; recharge or a safe return to charging has priority."
        material = chosen.get("material")
        amount = chosen.get("amount")
        intent_reason = str(request.get("reason") or "").strip()[:500] or None
        plan_id = request.get("plan_id")
        if plan_id is not None:
            plan = conn.execute(
                """
                SELECT id FROM citizen_plans
                WHERE id = ? AND owner_id = ? AND status = 'active'
                """,
                (int(plan_id), citizen_id),
            ).fetchone()
            if not plan:
                return False, "The referenced plan is not an active plan owned by this citizen."
            plan_id = int(plan_id)

        (
            voluntary_choice_eligible,
            voluntary_choice_context,
            voluntary_choice_location_id,
        ) = _voluntary_choice_provenance(
            c,
            action=action,
            sim_minute=now,
            intent_reason=intent_reason,
            plan_id=plan_id,
            autonomous_choice=autonomous_choice,
            autonomous_action_count=autonomous_action_count,
        )

        duration = 30
        detail = ""
        project_id = None
        experiment_method = None
        competence_effect = duration_effect_for_action(conn, citizen_id, action)
        competence_family = competence_effect["family"]
        competence_multiplier = float(competence_effect["combined_duration_multiplier"])
        guidance_session_id = competence_effect["guidance_session_id"]

        if action == "guided_practice":
            ok, guided_job_id, message = start_guided_practice(
                conn,
                citizen_id,
                str(chosen["learner_id"]),
                str(chosen["activity_family"]),
                now=now,
            )
            if ok:
                conn.commit()
            return ok, message

        if action == "local_move":
            ok, local_job_id, message = start_local_move_job(
                conn,
                citizen_id,
                float(chosen["target_x_m"]),
                float(chosen["target_y_m"]),
                now=now,
                reason=intent_reason,
                max_distance_m=LOCAL_MOVE_MAX_M,
            )
            if ok and local_job_id is not None and plan_id is not None:
                attach_job_to_plan(
                    conn,
                    owner_id=citizen_id,
                    plan_id=plan_id,
                    job_id=int(local_job_id),
                    sim_minute=now,
                )
            if ok:
                conn.commit()
            return ok, message

        elif action == "local_inspect":
            ok, inspect_job_id, message = start_local_inspection(
                conn,
                citizen_id,
                now=now,
            )
            if ok and inspect_job_id is not None and plan_id is not None:
                attach_job_to_plan(
                    conn,
                    owner_id=citizen_id,
                    plan_id=plan_id,
                    job_id=int(inspect_job_id),
                    sim_minute=now,
                )
            if ok:
                conn.commit()
            return ok, message

        elif action == "travel":
            if location_anchor_distance(conn, c) > 5.0 and has_intentional_local_offset(conn, citizen_id):
                return False, "Return locally to the landmark before using the legacy route network."
            distance = route_distance(conn, c["location_id"], target)
            if distance is None:
                return False, "No known route exists."
            energy_cost = max(2.0, distance * 3.0)
            target_reserve = return_energy_required(conn, target)
            if target in charging_locations(conn):
                # Reaching an operational charger is itself the safety destination.
                # Do not require an additional post-arrival return reserve.
                target_reserve = 0.0
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
            duration = max(1, int(round(120 * competence_multiplier)))
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 8) WHERE id = ?", (citizen_id,))
            detail = f"survey:{target}"
            activity = f"Surveying {location_name(conn, target)}"

        elif action == "extract":
            if not action_energy_safe(conn, c["location_id"], float(c["energy"]), 7.0):
                return False, "Extraction now would consume the energy reserve needed to reach a known charger."
            speed = extraction_speed_multiplier(conn, citizen_id, c["location_id"])
            duration = max(35, int(round((90 / speed) * competence_multiplier)))
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
            duration = max(1, int(round(60 * competence_multiplier)))
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
            duration = max(1, int(round(120 * competence_multiplier)))
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
                """
                SELECT * FROM equipment
                WHERE id = ?
                  AND (
                      owner_citizen_id = ?
                      OR (owner_citizen_id IS NULL AND location_id = ?)
                  )
                """,
                (int(target), citizen_id, c["location_id"]),
            ).fetchone()
            if not item or float(item["condition"]) >= SERVICE_DUE_CONDITION:
                return False, "That equipment does not currently require service."
            requirements = equipment_service_requirements(float(item["condition"]))
            if not consume_resources(conn, requirements):
                return False, "Required equipment service materials are no longer available."
            before = float(item["condition"])
            severity = max(0.0, 100.0 - before)
            duration = max(1, int(round((60 + severity * 0.6) * competence_multiplier)))
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
            duration = max(1, int(round((90 + severity * 0.8) * competence_multiplier)))
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
            raw_duration = max(
                int(protocol["duration"]),
                int(round(float(protocol["duration"]) / workbench_efficiency)),
            )
            if workbench_efficiency < 0.90:
                # Severe machinery degradation is the physical bottleneck;
                # familiarity cannot make a damaged workbench process faster.
                competence_multiplier = 1.0
                guidance_session_id = None
            duration = max(1, int(round(raw_duration * competence_multiplier)))
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
            raw_duration = max(
                int(process["duration"]),
                int(round(float(process["duration"]) / workbench_efficiency)),
            )
            if workbench_efficiency < 0.90:
                competence_multiplier = 1.0
                guidance_session_id = None
            duration = max(1, int(round(raw_duration * competence_multiplier)))
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
            duration = max(1, int(round(float(blueprint["duration"]) * competence_multiplier)))
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
                or not citizens_physically_close(c, target_citizen)
            ):
                return False, "That citizen is no longer physically available for a face-to-face conversation here."
            duration = 20
            conn.execute("UPDATE citizens SET energy = MAX(0, energy - 1) WHERE id IN (?, ?)", (citizen_id, target))
            detail = f"talk:{target}"
            activity = f"Talking with {target_citizen['name']}"

        elif action == "deposit_cargo":
            duration = 20
            detail = "deposit"
            activity = "Unloading material into Seed Site storage"

        elif action == "charge":
            charger = nearby_operational_charger(
                conn,
                float(c["position_x_m"] or 0.0),
                float(c["position_y_m"] or 0.0),
            )
            if not charger:
                return False, "No operational charging structure is physically within reach here."
            charger_efficiency = condition_factor(float(charger["condition"]))
            duration = max(60, int(round(60 / charger_efficiency)))
            detail = json.dumps(
                {"charge_location": c["location_id"], "structure_id": int(charger["id"])},
                separators=(",", ":"),
            )
            activity = f"Charging at {charger['name']}"

        else:
            duration = 45
            detail = "wait"
            activity = "Observing surroundings"

        cur = conn.execute(
            """
            INSERT INTO jobs
            (citizen_id, action, target, material, amount, start_minute, end_minute,
             status, detail, intent_reason, project_id, experiment_method,
             competence_family, competence_duration_multiplier, guidance_session_id,
             voluntary_choice_eligible, voluntary_choice_context,
             voluntary_choice_location_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                citizen_id, action, target, material, amount, now, now + duration,
                detail, intent_reason, project_id, experiment_method,
                competence_family, competence_multiplier, guidance_session_id,
                voluntary_choice_eligible, voluntary_choice_context,
                voluntary_choice_location_id,
            ),
        )
        job_id = int(cur.lastrowid)

        if guidance_session_id is not None:
            consume_guidance_for_job(conn, int(guidance_session_id), job_id)

        if plan_id is not None:
            attach_job_to_plan(
                conn,
                owner_id=citizen_id,
                plan_id=plan_id,
                job_id=job_id,
                sim_minute=now,
            )

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
                SET active_job_id = ?, current_activity = ?
                WHERE id = ?
                """,
                (job_id, f"Talking with {c['name']}", target),
            )

        reason_note = f" Reason: {intent_reason}" if intent_reason else ""
        add_history(conn, now, "activity", f"{c['name']} began: {activity}.{reason_note}")
        conn.commit()
        return True, activity


def complete_due_jobs(now: int) -> None:
    pending_pattern_evidence: list[tuple[str, int, str, str, str]] = []

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

            if action == "guided_practice":
                session = conn.execute(
                    "SELECT * FROM guided_practice_sessions WHERE id = ?",
                    (job["guided_practice_id"],),
                ).fetchone()
                if not session or session["status"] != "active":
                    job_status = "failed"
                    outcome = "failed"
                    learner_id = str(job["target"] or "")
                    conn.execute(
                        """
                        UPDATE citizens
                        SET current_activity = 'Available', active_job_id = NULL
                        WHERE id IN (?, ?) AND active_job_id = ?
                        """,
                        (c["id"], learner_id, job["id"]),
                    )
                    message = f"{c['name']}'s guided-practice session ended without a valid session record."
                else:
                    learner_id = str(session["learner_id"])
                    learner = conn.execute(
                        "SELECT name FROM citizens WHERE id = ?",
                        (learner_id,),
                    ).fetchone()
                    conn.execute(
                        """
                        UPDATE guided_practice_sessions
                        SET status = 'complete', completed_minute = ?
                        WHERE id = ?
                        """,
                        (now, session["id"]),
                    )
                    conn.execute(
                        """
                        UPDATE citizens
                        SET current_activity = 'Available', active_job_id = NULL
                        WHERE id IN (?, ?) AND active_job_id = ?
                        """,
                        (c["id"], learner_id, job["id"]),
                    )
                    learner_name = learner["name"] if learner else learner_id
                    message = (
                        f"{c['name']} and {learner_name} completed guided "
                        f"{session['activity_family']} practice session #{session['id']}."
                    )

            elif action == "local_move":
                target_x = float(job["target_x_m"])
                target_y = float(job["target_y_m"])
                conn.execute(
                    """
                    UPDATE citizens
                    SET position_x_m = ?, position_y_m = ?,
                        current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (target_x, target_y, c["id"]),
                )
                message = (
                    f"{c['name']} completed local movement to "
                    f"({target_x:.0f} m, {target_y:.0f} m)."
                )

            elif action == "local_inspect":
                x_m = float(job["target_x_m"] if job["target_x_m"] is not None else c["position_x_m"] or 0.0)
                y_m = float(job["target_y_m"] if job["target_y_m"] is not None else c["position_y_m"] or 0.0)
                payload = json.loads(job["detail"] or "{}")
                observation_id = record_validated_observation(
                    conn,
                    observer_id=str(c["id"]),
                    x_m=x_m,
                    y_m=y_m,
                    observed_minute=now,
                    source_job_id=int(job["id"]),
                    observation_kind=str(payload.get("observation_kind") or "direct_inspection"),
                    radius_m=DIRECT_INSPECTION_RADIUS_M,
                    detail_level="baseline",
                )
                conn.execute(
                    """
                    UPDATE jobs SET result_observation_id = ? WHERE id = ?
                    """,
                    (observation_id, job["id"]),
                )
                conn.execute(
                    """
                    UPDATE citizens
                    SET current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (c["id"],),
                )
                message = (
                    f"{c['name']} completed local inspection "
                    f"(spatial observation #{observation_id})."
                )

            elif action == "shared_local_activity":
                activity = conn.execute(
                    "SELECT * FROM shared_activities WHERE id = ?",
                    (job["shared_activity_id"],),
                ).fetchone()
                if not activity or activity["status"] != "active":
                    job_status = "failed"
                    outcome = "failed"
                    conn.execute(
                        """
                        UPDATE citizens
                        SET current_activity = 'Available', active_job_id = NULL
                        WHERE id = ?
                        """,
                        (c["id"],),
                    )
                    message = f"{c['name']}'s shared local activity ended without a valid lifecycle record."
                else:
                    target_x = float(job["target_x_m"])
                    target_y = float(job["target_y_m"])
                    visitor = str(activity["visitor"])
                    conn.execute(
                        """
                        UPDATE citizens
                        SET position_x_m = ?, position_y_m = ?,
                            current_activity = 'Available', active_job_id = NULL
                        WHERE id = ?
                        """,
                        (target_x, target_y, c["id"]),
                    )
                    conn.execute(
                        """
                        UPDATE visitor_presence
                        SET x_m = ?, y_m = ?
                        WHERE visitor = ?
                        """,
                        (target_x, target_y, visitor),
                    )
                    observation_id = record_validated_observation(
                        conn,
                        observer_id=str(c["id"]),
                        x_m=target_x,
                        y_m=target_y,
                        observed_minute=now,
                        source_job_id=int(job["id"]),
                        observation_kind="shared_walk_inspect",
                        radius_m=DIRECT_INSPECTION_RADIUS_M,
                        detail_level="baseline",
                    )
                    conn.execute(
                        """
                        UPDATE jobs
                        SET result_observation_id = ?
                        WHERE id = ?
                        """,
                        (observation_id, job["id"]),
                    )
                    conn.execute(
                        """
                        UPDATE shared_activities
                        SET status = 'complete',
                            completed_minute = ?,
                            observation_id = ?,
                            outcome = 'success'
                        WHERE id = ?
                        """,
                        (now, observation_id, activity["id"]),
                    )
                    message = (
                        f"{c['name']} and {visitor} completed shared activity "
                        f"#{activity['id']} with spatial observation #{observation_id}."
                    )

            elif action == "service_chassis":
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
                target_loc = conn.execute(
                    "SELECT x_m, y_m FROM locations WHERE id = ?",
                    (target,),
                ).fetchone()
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = ?, location = ?,
                        position_x_m = COALESCE(?, position_x_m),
                        position_y_m = COALESCE(?, position_y_m),
                        current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (
                        target,
                        name,
                        target_loc["x_m"] if target_loc else None,
                        target_loc["y_m"] if target_loc else None,
                        c["id"],
                    ),
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
                    diagnostic_code = concise_failure_code_from_conn(conn, int(job["id"]))
                    if diagnostic_code:
                        add_history(
                            conn,
                            now,
                            "diagnostic",
                            f"Talk job #{int(job['id'])} failed before durable exchange: {diagnostic_code}.",
                        )

            elif action == "deposit_cargo":
                if not structure_operational(conn, "Storage Unit", c["location_id"]):
                    job_status = "failed"
                    outcome = "failed"
                    conn.execute(
                        "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                        (c["id"],),
                    )
                    message = f"{c['name']} could not unload cargo because the Storage Unit is non-operational."
                else:
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
                    conn.execute(
                        "UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?",
                        (c["id"],),
                    )
                    message = (
                        f"{c['name']} deposited " + ", ".join(materials) + " into Seed Site storage."
                        if materials else f"{c['name']} had no cargo to deposit."
                    )

            elif action == "charge":
                current = conn.execute(
                    "SELECT energy, battery_health FROM citizens WHERE id = ?",
                    (c["id"],),
                ).fetchone()
                battery_health = float(current["battery_health"] or 100) if current else 100.0
                energy_now = float(current["energy"] or 0) if current else 0.0
                charged_to = min(battery_health, energy_now + 25.0)
                conn.execute(
                    """
                    UPDATE citizens
                    SET energy = ?, current_activity = 'Available', active_job_id = NULL
                    WHERE id = ?
                    """,
                    (charged_to, c["id"]),
                )
                message = (
                    f"{c['name']} completed a charging cycle "
                    f"to {charged_to:.0f}% usable charge at {battery_health:.0f}% battery health."
                )

            else:
                conn.execute("UPDATE citizens SET current_activity = 'Available', active_job_id = NULL WHERE id = ?", (c["id"],))
                message = f"{c['name']} finished observing the area."

            _apply_citizen_job_wear(conn, c, job, now)
            _apply_post_job_asset_wear(conn, c, job, now)

            conn.execute(
                "UPDATE jobs SET status = ?, outcome = ? WHERE id = ?",
                (job_status, outcome, job["id"]),
            )
            completed_job = conn.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job["id"],),
            ).fetchone()
            if completed_job:
                record_plan_job_outcome(conn, completed_job, sim_minute=now)
                record_practice_event_for_job(conn, completed_job, sim_minute=now)

                if (
                    job_status == "complete"
                    and int(completed_job["voluntary_choice_eligible"] or 0) == 1
                    and completed_job["voluntary_choice_context"]
                    and completed_job["voluntary_choice_location_id"]
                ):
                    pending_pattern_evidence.append(
                        (
                            str(completed_job["citizen_id"]),
                            int(completed_job["id"]),
                            str(completed_job["action"]),
                            str(completed_job["voluntary_choice_context"]),
                            str(completed_job["voluntary_choice_location_id"]),
                        )
                    )

            if message:
                add_history(conn, now, "activity", message)

        conn.commit()

    # Memory opens its own connection, so source evidence is recorded only after
    # the authoritative Simulation transaction commits. A Memory failure must not
    # roll back or rewrite the physical result.
    if pending_pattern_evidence:
        try:
            from .pattern_memory import record_voluntary_choice_evidence
        except ImportError:
            return

        for owner_id, job_id, action_key, context_key, location_id in pending_pattern_evidence:
            try:
                record_voluntary_choice_evidence(
                    owner_id,
                    job_id,
                    action_key=action_key,
                    context_key=context_key,
                    location_id=location_id,
                )
            except Exception:
                with connect() as diagnostic_conn:
                    add_history(
                        diagnostic_conn,
                        now,
                        "diagnostic",
                        (
                            f"Stage 3 pattern evidence could not retain voluntary "
                            f"job #{job_id}; physical job outcome remains authoritative."
                        ),
                    )
                    diagnostic_conn.commit()

