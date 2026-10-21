"""
Settlement timeline: a read-only, long-view summary of what the civilization
has actually done, assembled from authoritative Simulation records.

Built for checking in after weeks or months away: milestones (first builds,
first production of each part, discoveries, first conversations between each
pair, breakdowns), activity per period, per-citizen totals, and how the
finite starter stores have changed.

Hidden world truth is never read here. Only completed, public records are used:
the same information the Records views already expose piece by piece.
"""

from __future__ import annotations

from typing import Any

from .db import STARTING_RESOURCES, connect, get_meta
from .world import format_sim_time

ACTION_FAMILIES: dict[str, str] = {
    "extract": "work",
    "process_material": "work",
    "fabricate": "work",
    "construct": "work",
    "plan_project": "work",
    "reserve_project": "work",
    "deposit_cargo": "work",
    "travel": "explore",
    "survey": "explore",
    "local_move": "explore",
    "local_inspect": "explore",
    "experiment": "explore",
    "talk": "social",
    "guided_practice": "social",
    "charge": "upkeep",
    "service_chassis": "upkeep",
    "service_battery": "upkeep",
    "service_structure": "upkeep",
    "service_equipment": "upkeep",
}
FAMILIES = ("work", "explore", "social", "upkeep", "other")
MAX_MILESTONES = 400


def _family(action: str) -> str:
    action = str(action or "")
    if action in ACTION_FAMILIES:
        return ACTION_FAMILIES[action]
    if action.startswith("service_") or action.startswith("replace_"):
        return "upkeep"
    return "other"


def _table_exists(conn, name: str) -> bool:
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (name,),
        ).fetchone()
    )


def _columns(conn, table: str) -> set[str]:
    return {str(row["name"]) for row in conn.execute(f"PRAGMA table_info({table})")}


def _day(minute: int) -> int:
    return int(minute) // 1440 + 1


def settlement_timeline(bucket_days: int | None = None) -> dict[str, Any]:
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        names = {
            str(row["id"]): str(row["name"])
            for row in conn.execute("SELECT id, name FROM citizens")
        }

        def who(citizen_id: Any) -> str:
            return names.get(str(citizen_id or ""), str(citizen_id or "unknown"))

        milestones: list[dict[str, Any]] = []

        def milestone(minute: Any, kind: str, title: str, citizen_id: Any = None) -> None:
            if minute is None:
                return
            milestones.append(
                {
                    "sim_minute": int(minute),
                    "day": _day(int(minute)),
                    "label": format_sim_time(int(minute)),
                    "kind": kind,
                    "title": title,
                    "citizen": who(citizen_id) if citizen_id else None,
                }
            )

        # Completed construction projects.
        builds = conn.execute(
            """
            SELECT name, created_by, completed_minute
            FROM projects
            WHERE status IN ('complete', 'completed') AND completed_minute IS NOT NULL
            ORDER BY completed_minute, id
            """
        ).fetchall()
        for row in builds:
            milestone(row["completed_minute"], "build", f"Built {row['name']}", row["created_by"])

        # First successful run of each production process.
        production_rows = []
        if _table_exists(conn, "production_events"):
            production_rows = conn.execute(
                """
                SELECT citizen_id, process_key, process_name, outputs_json, outcome, sim_minute
                FROM production_events
                ORDER BY sim_minute, id
                """
            ).fetchall()
        seen_processes: set[str] = set()
        for row in production_rows:
            if row["process_key"] in seen_processes:
                continue
            seen_processes.add(row["process_key"])
            milestone(
                row["sim_minute"],
                "production",
                f"First time: {row['process_name']}",
                row["citizen_id"],
            )

        # Equipment fabricated by citizens (starter equipment has no source job).
        for row in conn.execute(
            """
            SELECT name, owner_citizen_id, created_minute
            FROM equipment
            WHERE created_job_id IS NOT NULL
            ORDER BY created_minute, id
            """
        ):
            milestone(row["created_minute"], "equipment", f"Made a {row['name']}", row["owner_citizen_id"])

        # Discoveries: confirmed deposits and the first validation of each property.
        discovery_rows = conn.execute(
            """
            SELECT d.discovery_kind, d.subject_id, d.property_id, d.citizen_id,
                   d.discovered_minute, d.summary, l.name AS location_name
            FROM discoveries d
            LEFT JOIN locations l ON l.id = d.location_id
            ORDER BY d.discovered_minute, d.id
            """
        ).fetchall()
        seen_discoveries: set[tuple[str, str]] = set()
        first_discoveries: list[Any] = []
        for row in discovery_rows:
            key = (
                str(row["discovery_kind"]),
                str(row["property_id"] or row["subject_id"]),
            )
            if key in seen_discoveries:
                continue
            seen_discoveries.add(key)
            first_discoveries.append(row)
            kind = "deposit" if row["discovery_kind"] == "deposit" else "knowledge"
            milestone(row["discovered_minute"], kind, str(row["summary"]), row["citizen_id"])

        # First recorded conversation between each pair of citizens.
        conversation_rows = conn.execute(
            """
            SELECT initiator_id, target_id, sim_minute, summary
            FROM citizen_conversations
            ORDER BY sim_minute, id
            """
        ).fetchall()
        seen_pairs: set[tuple[str, str]] = set()
        for row in conversation_rows:
            pair = tuple(sorted((str(row["initiator_id"]), str(row["target_id"]))))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            milestone(
                row["sim_minute"],
                "social",
                f"First conversation: {who(pair[0])} and {who(pair[1])}",
                row["initiator_id"],
            )

        # Persistent plans that were created or completed.
        if _table_exists(conn, "citizen_plans"):
            for row in conn.execute(
                "SELECT owner_id, created_minute, updated_minute, status, current_intent "
                "FROM citizen_plans ORDER BY created_minute, id"
            ):
                milestone(row["created_minute"], "plan", f"New plan: {row['current_intent']}", row["owner_id"])
                if row["status"] == "completed":
                    milestone(
                        row["updated_minute"],
                        "plan",
                        f"Completed plan: {row['current_intent']}",
                        row["owner_id"],
                    )

        # Breakdowns are recorded as maintenance history.
        for row in conn.execute(
            """
            SELECT sim_minute, message
            FROM history
            WHERE category = 'maintenance' AND message LIKE '%non-operational%'
            ORDER BY sim_minute, id
            """
        ):
            milestone(row["sim_minute"], "breakdown", str(row["message"]))

        milestones.sort(key=lambda item: (item["sim_minute"], item["kind"]))
        milestones_total = len(milestones)
        if milestones_total > MAX_MILESTONES:
            milestones = milestones[-MAX_MILESTONES:]

        # Completed jobs drive the activity charts and per-citizen totals.
        job_rows = conn.execute(
            """
            SELECT citizen_id, action, end_minute
            FROM jobs
            WHERE status = 'complete'
            ORDER BY end_minute, id
            """
        ).fetchall()

        days_elapsed = max(1, _day(now))
        if bucket_days is None:
            bucket_days = 30 if days_elapsed > 120 else 7
        bucket_days = max(1, min(int(bucket_days), 90))
        bucket_count = max(1, (days_elapsed + bucket_days - 1) // bucket_days)

        def empty_bucket(index: int) -> dict[str, Any]:
            first_day = index * bucket_days + 1
            return {
                "first_day": first_day,
                "last_day": min(days_elapsed, first_day + bucket_days - 1),
                "jobs": {family: 0 for family in FAMILIES},
                "conversations": 0,
                "discoveries": 0,
                "builds": 0,
                "production_runs": 0,
            }

        buckets = [empty_bucket(i) for i in range(bucket_count)]

        def bucket_for(minute: Any) -> dict[str, Any] | None:
            if minute is None:
                return None
            index = (_day(int(minute)) - 1) // bucket_days
            return buckets[index] if 0 <= index < len(buckets) else None

        citizens: dict[str, dict[str, Any]] = {
            cid: {
                "id": cid,
                "name": name,
                "jobs_completed": 0,
                "jobs": {family: 0 for family in FAMILIES},
                "conversations": 0,
                "discoveries": 0,
                "builds": 0,
                "production_runs": 0,
                "top_actions": {},
            }
            for cid, name in names.items()
        }

        for row in job_rows:
            family = _family(row["action"])
            bucket = bucket_for(row["end_minute"])
            if bucket:
                bucket["jobs"][family] += 1
            person = citizens.get(str(row["citizen_id"]))
            if person:
                person["jobs_completed"] += 1
                person["jobs"][family] += 1
                actions = person["top_actions"]
                actions[row["action"]] = actions.get(row["action"], 0) + 1

        for row in conversation_rows:
            bucket = bucket_for(row["sim_minute"])
            if bucket:
                bucket["conversations"] += 1
            for cid in (row["initiator_id"], row["target_id"]):
                if str(cid) in citizens:
                    citizens[str(cid)]["conversations"] += 1

        for row in first_discoveries:
            bucket = bucket_for(row["discovered_minute"])
            if bucket:
                bucket["discoveries"] += 1
            if str(row["citizen_id"]) in citizens:
                citizens[str(row["citizen_id"])]["discoveries"] += 1

        for row in builds:
            bucket = bucket_for(row["completed_minute"])
            if bucket:
                bucket["builds"] += 1
            if str(row["created_by"]) in citizens:
                citizens[str(row["created_by"])]["builds"] += 1

        for row in production_rows:
            bucket = bucket_for(row["sim_minute"])
            if bucket:
                bucket["production_runs"] += 1
            if str(row["citizen_id"]) in citizens:
                citizens[str(row["citizen_id"])]["production_runs"] += 1

        for person in citizens.values():
            ranked = sorted(person["top_actions"].items(), key=lambda kv: (-kv[1], kv[0]))
            person["top_actions"] = [{"action": a, "count": n} for a, n in ranked[:3]]

        # Finite starter stores: where they started versus now.
        current_stores = {
            str(row["name"]): float(row["amount"])
            for row in conn.execute("SELECT name, amount FROM resources")
        }
        stores = [
            {
                "material": material,
                "start": float(start),
                "now": round(current_stores.get(material, 0.0), 2),
            }
            for material, start in STARTING_RESOURCES.items()
        ]

        structures_standing = int(
            conn.execute("SELECT COUNT(*) AS n FROM structures").fetchone()["n"]
        )
        equipment_made = sum(1 for m in milestones if m["kind"] == "equipment")

    return {
        "now": {
            "sim_minute": now,
            "label": format_sim_time(now),
            "days_elapsed": days_elapsed,
        },
        "totals": {
            "population": len(names),
            "structures_standing": structures_standing,
            "buildings_completed": len(builds),
            "equipment_made": equipment_made,
            "production_runs": len(production_rows),
            "processes_mastered": len(seen_processes),
            "deposits_confirmed": sum(1 for r in first_discoveries if r["discovery_kind"] == "deposit"),
            "properties_validated": sum(1 for r in first_discoveries if r["discovery_kind"] != "deposit"),
            "conversations": len(conversation_rows),
            "citizen_pairs_met": len(seen_pairs),
            "jobs_completed": len(job_rows),
        },
        "bucket_days": bucket_days,
        "buckets": buckets,
        "milestones": milestones,
        "milestones_total": milestones_total,
        "citizens": sorted(citizens.values(), key=lambda p: p["name"]),
        "stores": stores,
    }
