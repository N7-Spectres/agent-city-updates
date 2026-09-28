from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def set_time(conn, minute: int) -> None:
    from agent_city.db import set_meta
    set_meta(conn, "sim_minute", minute)
    conn.commit()


def active_job(citizen_id: str) -> dict:
    from agent_city.db import connect
    with connect() as conn:
        row = conn.execute(
            """
            SELECT j.*
            FROM citizens c
            JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()
        assert row is not None
        return dict(row)


def finish(citizen_id: str) -> dict:
    from agent_city.simulation import complete_due_jobs
    job = active_job(citizen_id)
    complete_due_jobs(int(job["end_minute"]))
    return job


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import (
            MIN_OPERATIONAL_CONDITION,
            apply_passive_wear,
            cargo_capacity,
            extraction_speed_multiplier,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()  # migrations remain idempotent

        state = snapshot()
        assert "maintenance_events" in state
        assert all(float(c["battery_health"]) == 100 for c in state["citizens"])
        assert all(c["battery_state"] == "nominal" for c in state["citizens"])

        # Fabricate a real extraction tool first.
        with connect() as conn:
            set_time(conn, 400)
        ok, _ = start_action(
            "bex",
            {
                "action": "fabricate",
                "target": "extraction_tool",
                "reason": "Create a physical extraction tool for field work.",
            },
        )
        assert ok
        finish("bex")

        with connect() as conn:
            tool = conn.execute(
                "SELECT * FROM equipment WHERE owner_citizen_id = 'bex' AND template_id = 'extraction_tool'"
            ).fetchone()
            assert tool is not None
            tool_id = int(tool["id"])
            assert float(tool["condition"]) < 100  # fabrication itself wears the workbench, not the new tool
            # New equipment remains pristine.
            assert float(tool["condition"]) == 100

            # Prepare a real extraction site.
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'rocky_basin', location = 'Rocky Basin',
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            conn.execute("UPDATE deposits SET discovered = 1 WHERE id = 'dep_silicate'")
            set_time(conn, 800)

        # Real use reduces equipment condition and citizen maintenance state gradually.
        extract = next(
            a for a in possible_actions("bex")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        ok, _ = start_action(
            "bex",
            {
                "action": "extract",
                "target": extract["target"],
                "material": extract["material"],
                "reason": "Use the powered extraction tool on the confirmed deposit.",
            },
        )
        assert ok
        first_extract = active_job("bex")
        finish("bex")

        with connect() as conn:
            tool = conn.execute("SELECT * FROM equipment WHERE id = ?", (tool_id,)).fetchone()
            bex = conn.execute("SELECT * FROM citizens WHERE id = 'bex'").fetchone()
            assert float(tool["condition"]) == 98.5
            assert int(tool["use_count"]) == 1
            assert float(bex["battery_health"]) < 100
            assert float(bex["joint_wear"]) > 0

        # Degraded equipment has a smaller physical effect, but still functions above critical.
        with connect() as conn:
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = 'bex'")
            conn.execute("UPDATE equipment SET condition = 50 WHERE id = ?", (tool_id,))
            conn.execute("UPDATE citizens SET energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'bex'")
            set_time(conn, 1000)

            degraded_multiplier = extraction_speed_multiplier(conn, "bex", "rocky_basin")
            assert 1.0 < degraded_multiplier < 1.35

        extract = next(a for a in possible_actions("bex") if a["action"] == "extract")
        ok, _ = start_action(
            "bex",
            {
                "action": "extract",
                "target": extract["target"],
                "material": extract["material"],
                "reason": "Continue with the worn extraction tool.",
            },
        )
        assert ok
        degraded_job = active_job("bex")
        assert int(degraded_job["end_minute"]) - int(degraded_job["start_minute"]) > (
            int(first_extract["end_minute"]) - int(first_extract["start_minute"])
        )
        finish("bex")

        # A critical tool becomes unavailable for capability but remains visible/repairable.
        with connect() as conn:
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = 'bex'")
            conn.execute("UPDATE equipment SET condition = 15 WHERE id = ?", (tool_id,))
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            set_time(conn, 1300)
            assert extraction_speed_multiplier(conn, "bex", "seed_site") == 1.0

        state = snapshot()
        exposed_tool = next(e for e in state["equipment"] if e["id"] == tool_id)
        assert exposed_tool["operational"] is False
        assert exposed_tool["condition_state"] == "critical"
        assert exposed_tool["effective_extraction_speed_multiplier"] == 1.0

        service = next(
            a for a in possible_actions("bex")
            if a["action"] == "service_equipment" and a["target"] == str(tool_id)
        )
        with connect() as conn:
            fasteners_before = float(conn.execute("SELECT amount FROM resources WHERE name = 'Fasteners'").fetchone()["amount"])
            lubricant_before = float(conn.execute("SELECT amount FROM resources WHERE name = 'Lubricant'").fetchone()["amount"])

        ok, _ = start_action(
            "bex",
            {
                "action": "service_equipment",
                "target": service["target"],
                "reason": "Restore the critical extraction tool before further use.",
            },
        )
        assert ok
        service_job = active_job("bex")

        with connect() as conn:
            assert float(conn.execute("SELECT amount FROM resources WHERE name = 'Fasteners'").fetchone()["amount"]) < fasteners_before
            assert float(conn.execute("SELECT amount FROM resources WHERE name = 'Lubricant'").fetchone()["amount"]) < lubricant_before

        finish("bex")
        with connect() as conn:
            repaired = conn.execute("SELECT * FROM equipment WHERE id = ?", (tool_id,)).fetchone()
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (service_job["id"],)).fetchone()
            event = conn.execute(
                "SELECT * FROM maintenance_events WHERE job_id = ?",
                (service_job["id"],),
            ).fetchone()
            assert float(repaired["condition"]) == 100
            assert repaired["last_service_minute"] is not None
            assert event is not None
            assert int(job["maintenance_event_id"]) == int(event["id"])
            assert event["event_type"] == "equipment_service"

        # Structure condition degrades from simulated time, not wall-clock downtime.
        with connect() as conn:
            workbench = conn.execute("SELECT * FROM structures WHERE name = 'Basic Workbench'").fetchone()
            workbench_id = int(workbench["id"])
            conn.execute("UPDATE structures SET condition = 100 WHERE id = ?", (workbench_id,))
            db.set_meta(conn, "maintenance_wear_minute", "2000")
            conn.commit()
        apply_passive_wear(2000 + 1440 * 10)
        with connect() as conn:
            workbench = conn.execute("SELECT * FROM structures WHERE id = ?", (workbench_id,)).fetchone()
            assert 99.0 < float(workbench["condition"]) < 100.0

        # A degraded workbench makes supported work take longer.
        with connect() as conn:
            conn.execute("UPDATE structures SET condition = 50 WHERE id = ?", (workbench_id,))
            conn.execute(
                """
                INSERT INTO resources(name, amount) VALUES ('Plant Fiber', 20)
                ON CONFLICT(name) DO UPDATE SET amount = MAX(amount, 20)
                """
            )
            conn.execute(
                """
                UPDATE citizens
                SET energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            set_time(conn, 17000)

        pack = next(a for a in possible_actions("bex") if a["action"] == "fabricate" and a["target"] == "field_pack")
        ok, _ = start_action(
            "bex",
            {
                "action": "fabricate",
                "target": pack["target"],
                "reason": "Fabricate cargo gear using the degraded but operational workbench.",
            },
        )
        assert ok
        fab_job = active_job("bex")
        assert int(fab_job["end_minute"]) - int(fab_job["start_minute"]) >= 180
        finish("bex")

        # A critical workbench is unavailable but can be serviced.
        with connect() as conn:
            conn.execute("UPDATE structures SET condition = 15 WHERE id = ?", (workbench_id,))
            conn.execute(
                "UPDATE citizens SET energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'iri'"
            )
            set_time(conn, 18000)
        iri_actions = possible_actions("iri")
        assert not any(a["action"] in {"fabricate", "experiment"} for a in iri_actions)
        structure_service = next(
            a for a in iri_actions
            if a["action"] == "service_structure" and a["target"] == str(workbench_id)
        )
        ok, _ = start_action(
            "iri",
            {
                "action": "service_structure",
                "target": structure_service["target"],
                "reason": "Restore the non-operational Basic Workbench.",
            },
        )
        assert ok
        structure_job = active_job("iri")
        finish("iri")
        with connect() as conn:
            workbench = conn.execute("SELECT * FROM structures WHERE id = ?", (workbench_id,)).fetchone()
            event = conn.execute("SELECT * FROM maintenance_events WHERE job_id = ?", (structure_job["id"],)).fetchone()
            assert float(workbench["condition"]) == 100
            assert event["event_type"] == "structure_service"

        # Battery health is distinct from current charge and caps usable charging.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET battery_health = 70, energy = 60, active_job_id = NULL,
                    current_activity = 'Available', location_id = 'seed_site', location = 'Seed Site'
                WHERE id = 'cato'
                """
            )
            set_time(conn, 19000)

        charge = next(a for a in possible_actions("cato") if a["action"] == "charge")
        ok, _ = start_action(
            "cato",
            {"action": "charge", "target": charge["target"], "reason": "Recharge within the pack's remaining healthy capacity."},
        )
        assert ok
        finish("cato")
        with connect() as conn:
            cato = conn.execute("SELECT * FROM citizens WHERE id = 'cato'").fetchone()
            assert float(cato["energy"]) == 70
            assert float(cato["battery_health"]) == 70

        # Replacing a degraded pack consumes real parts and restores health, not charge.
        replacement = next(a for a in possible_actions("cato") if a["action"] == "replace_battery")
        with connect() as conn:
            cells_before = float(conn.execute("SELECT amount FROM resources WHERE name = 'Battery cells'").fetchone()["amount"])
        ok, _ = start_action(
            "cato",
            {
                "action": "replace_battery",
                "target": replacement["target"],
                "reason": "Replace the aged battery pack before field range becomes too constrained.",
            },
        )
        assert ok
        replacement_job = active_job("cato")
        finish("cato")
        with connect() as conn:
            cato = conn.execute("SELECT * FROM citizens WHERE id = 'cato'").fetchone()
            cells_after = float(conn.execute("SELECT amount FROM resources WHERE name = 'Battery cells'").fetchone()["amount"])
            event = conn.execute("SELECT * FROM maintenance_events WHERE job_id = ?", (replacement_job["id"],)).fetchone()
            assert float(cato["battery_health"]) == 100
            assert float(cato["energy"]) == 70  # replacement is not a free recharge
            assert cells_after == cells_before - 4
            assert event["event_type"] == "battery_replacement"

        # Chassis lubrication is preventative maintenance driven by accumulated wear.
        with connect() as conn:
            conn.execute("UPDATE citizens SET joint_wear = 15, active_job_id = NULL, current_activity = 'Available' WHERE id = 'vale'")
            set_time(conn, 20000)
        chassis = next(a for a in possible_actions("vale") if a["action"] == "service_chassis")
        ok, _ = start_action(
            "vale",
            {
                "action": "service_chassis",
                "target": chassis["target"],
                "reason": "Service accumulated joint wear before it becomes a larger problem.",
            },
        )
        assert ok
        chassis_job = active_job("vale")
        finish("vale")
        with connect() as conn:
            vale = conn.execute("SELECT * FROM citizens WHERE id = 'vale'").fetchone()
            event = conn.execute("SELECT * FROM maintenance_events WHERE job_id = ?", (chassis_job["id"],)).fetchone()
            assert float(vale["joint_wear"]) == 0
            assert event["event_type"] == "chassis_service"

        # Public condition fields are authoritative and UI-ready.
        state = snapshot()
        assert all("battery_health" in c for c in state["citizens"])
        assert all("battery_state" in c for c in state["citizens"])
        assert all("condition_state" in s for s in state["structures"])
        assert all("operational" in s for s in state["structures"])
        assert all("condition_state" in e for e in state["equipment"])
        assert state["maintenance_events"]

        print("Agent City v0.7 maintenance smoke test passed.")


if __name__ == "__main__":
    main()
