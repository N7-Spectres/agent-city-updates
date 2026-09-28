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


def finish(minute: int) -> None:
    from agent_city.simulation import complete_due_jobs
    complete_due_jobs(minute)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, snapshot
        from agent_city.simulation import (
            BASE_CARRY_CAPACITY,
            cargo_capacity,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema
        from agent_city.memory import ensure_memory_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Re-running migrations must be safe.
        init_db()

        state = snapshot()
        assert "equipment" in state
        assert "projects" in state
        assert "project_materials" in state
        seed = next(loc for loc in state["locations"] if loc["id"] == "seed_site")
        assert seed["x_km"] == 0.0 and seed["y_km"] == 0.0
        charger = next(s for s in state["structures"] if s["name"] == "Charging Station")
        assert charger["location_id"] == "seed_site"
        assert charger["provides_charging"] == 1

        # Fabrication consumes real stock and only creates equipment when the job completes.
        with connect() as conn:
            before = {
                row["name"]: float(row["amount"])
                for row in conn.execute(
                    "SELECT name, amount FROM resources WHERE name IN ('Mechanical components', 'Basic electronics', 'Fasteners')"
                )
            }
            set_time(conn, 400)

        ok, _ = start_action(
            "bex",
            {"action": "fabricate", "target": "extraction_tool", "reason": "Make extraction work more efficient."},
        )
        assert ok

        with connect() as conn:
            assert conn.execute("SELECT COUNT(*) AS n FROM equipment").fetchone()["n"] == 0
            after_start = {
                row["name"]: float(row["amount"])
                for row in conn.execute(
                    "SELECT name, amount FROM resources WHERE name IN ('Mechanical components', 'Basic electronics', 'Fasteners')"
                )
            }
            assert after_start["Mechanical components"] == before["Mechanical components"] - 6
            assert after_start["Basic electronics"] == before["Basic electronics"] - 3
            assert after_start["Fasteners"] == before["Fasteners"] - 4

        finish(1000)
        with connect() as conn:
            tool = conn.execute("SELECT * FROM equipment WHERE template_id = 'extraction_tool'").fetchone()
            assert tool is not None
            assert tool["owner_citizen_id"] == "bex"
            assert float(tool["extraction_speed_multiplier"]) > 1.0

            # Put Bex at a real discovered deposit to verify the owned tool affects job time.
            conn.execute(
                "UPDATE citizens SET location_id = 'rocky_basin', location = 'Rocky Basin', energy = 100 WHERE id = 'bex'"
            )
            conn.execute("UPDATE deposits SET discovered = 1 WHERE id = 'dep_silicate'")
            set_time(conn, 1100)

        extraction = next(
            a for a in possible_actions("bex")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        ok, _ = start_action(
            "bex",
            {
                "action": "extract",
                "target": extraction["target"],
                "material": extraction["material"],
                "reason": "Use the new extraction tool.",
            },
        )
        assert ok
        with connect() as conn:
            job = conn.execute("SELECT * FROM jobs WHERE id = (SELECT active_job_id FROM citizens WHERE id = 'bex')").fetchone()
            assert int(job["end_minute"]) - int(job["start_minute"]) < 90
        finish(1400)

        # A fabricated cargo pack raises capacity through persisted owned equipment.
        with connect() as conn:
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = 'bex'")
            conn.execute(
                """
                INSERT INTO resources(name, amount) VALUES ('Plant Fiber', 20)
                ON CONFLICT(name) DO UPDATE SET amount = MAX(amount, 20)
                """
            )
            conn.execute(
                "UPDATE citizens SET location_id = 'seed_site', location = 'Seed Site', energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'bex'"
            )
            set_time(conn, 1500)

        ok, _ = start_action(
            "bex",
            {"action": "fabricate", "target": "field_pack", "reason": "Carry more material per trip."},
        )
        assert ok
        finish(1800)
        with connect() as conn:
            assert cargo_capacity(conn, "bex", "seed_site") > BASE_CARRY_CAPACITY

        # Remote work is blocked before start if it would consume the return-energy reserve.
        with connect() as conn:
            conn.execute(
                "UPDATE citizens SET location_id = 'resin_grove', location = 'Resin Grove', energy = 12, active_job_id = NULL, current_activity = 'Available' WHERE id = 'aris'"
            )
            conn.execute("UPDATE locations SET surveyed = 0 WHERE id = 'resin_grove'")
            conn.execute("UPDATE deposits SET discovered = 1 WHERE id = 'dep_fiber'")
            conn.commit()
        aris_actions = possible_actions("aris")
        assert not any(a["action"] == "survey" for a in aris_actions)
        assert not any(a["action"] == "extract" for a in aris_actions)
        assert any(a["action"] == "travel" and a["target"] == "seed_site" for a in aris_actions)

        # Construction follows planned -> reserved -> underway -> complete.
        with connect() as conn:
            conn.execute(
                "UPDATE citizens SET location_id = 'seed_site', location = 'Seed Site', energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'iri'"
            )
            set_time(conn, 2000)

        ok, _ = start_action(
            "iri",
            {"action": "plan_project", "target": "field_shelter", "reason": "Add useful physical shelter at the settlement."},
        )
        assert ok
        finish(2050)

        with connect() as conn:
            project = conn.execute("SELECT * FROM projects ORDER BY id DESC LIMIT 1").fetchone()
            project_id = int(project["id"])
            assert project["status"] == "planned"
            set_time(conn, 2100)

        ok, _ = start_action(
            "iri",
            {"action": "reserve_project", "target": str(project_id), "reason": "Stage the required materials."},
        )
        assert ok
        with connect() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            assert project["status"] == "reserved"
            assert all(
                float(row["reserved_amount"]) == float(row["required_amount"])
                for row in conn.execute("SELECT * FROM project_materials WHERE project_id = ?", (project_id,))
            )
        finish(2150)

        with connect() as conn:
            set_time(conn, 2200)

        ok, _ = start_action(
            "iri",
            {"action": "construct", "target": str(project_id), "reason": "Build the reserved project."},
        )
        assert ok
        with connect() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            assert project["status"] == "underway"
        finish(2500)

        with connect() as conn:
            project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            assert project["status"] == "complete"
            structure = conn.execute("SELECT * FROM structures WHERE project_id = ?", (project_id,)).fetchone()
            assert structure is not None
            assert structure["location_id"] == "seed_site"
            assert project["resulting_structure_id"] == structure["id"]

            minimum = conn.execute("SELECT MIN(amount) AS minimum FROM resources").fetchone()["minimum"]
            assert float(minimum) >= 0.0

            # Stable completed jobs remain available as authoritative physical event references.
            completed = conn.execute(
                "SELECT id, citizen_id, action, target, end_minute, status, outcome, project_id FROM jobs WHERE status = 'complete' ORDER BY id"
            ).fetchall()
            assert completed
            assert all(int(row["id"]) > 0 for row in completed)
            assert all(row["outcome"] is not None for row in completed)

        print("Agent City v0.5 simulation smoke test passed.")


if __name__ == "__main__":
    main()
