from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def section(prompt: str, header: str) -> str:
    return prompt.split(header, 1)[1].split("\n\n", 1)[0]


def cato_prompt() -> str:
    from agent_city.db import snapshot
    from agent_city.planner import citizen_context
    from agent_city.simulation import possible_actions

    state = snapshot()
    cato = next(c for c in state["citizens"] if c["id"] == "cato")
    return citizen_context(cato, state, possible_actions("cato"))


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, set_meta
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import (
            apply_passive_wear,
            complete_due_jobs,
            local_resource_sustainability_attention,
            material_testing_attention,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        materials_header = "RAW MATERIALS YOU HAVE PERSONALLY ENCOUNTERED AND YOUR OWN TEST HISTORY:"
        supply_header = "CURRENT LOCALLY OBSERVABLE RESOURCE SUSTAINABILITY:"

        # A fresh citizen has handled nothing, so no material is named.
        assert material_testing_attention("cato") == []
        prompt = cato_prompt()
        assert "you have not personally handled or confirmed any raw material yet" in section(prompt, materials_header)
        assert "MATERIAL TESTING:" in prompt
        assert "finite does not mean urgent" not in prompt
        assert "Do not invent a source, conversion, fabrication recipe" in prompt

        # Without at least one earlier daily reading there is no trend line.
        rows = {row["material"]: row for row in local_resource_sustainability_attention("cato")}
        assert rows["Fasteners"]["recent_change"] is None
        assert "Fasteners: 100 units stored; no validated" in section(prompt, supply_header)

        # The passive-wear clock logs one stock reading per simulation day.
        with connect() as conn:
            set_meta(conn, "maintenance_wear_minute", 0)
            conn.commit()
        apply_passive_wear(360)
        with connect() as conn:
            conn.execute("UPDATE resources SET amount = 62 WHERE name = 'Fasteners'")
            set_meta(conn, "sim_minute", 3 * 1440 + 600)
            conn.commit()
        apply_passive_wear(3 * 1440 + 600)
        with connect() as conn:
            logged_days = conn.execute(
                "SELECT COUNT(DISTINCT sim_day) AS n FROM resource_stock_log"
            ).fetchone()["n"]
        assert logged_days == 2, logged_days

        rows = {row["material"]: row for row in local_resource_sustainability_attention("cato")}
        assert rows["Fasteners"]["recent_change"] == {"days": 3.0, "change": -38.0}
        supply = section(cato_prompt(), supply_header)
        assert "Fasteners: 62 units stored; 38 used over the last 3 day(s)" in supply, supply
        assert "Lubricant: 40 units stored; unchanged over the last 3 day(s)" in supply, supply

        # Readings older than the window are ignored.
        with connect() as conn:
            set_meta(conn, "sim_minute", 30 * 1440 + 600)
            conn.commit()
        rows = {row["material"]: row for row in local_resource_sustainability_attention("cato")}
        assert rows["Fasteners"]["recent_change"] is None

        # A real survey confirms a deposit; the citizen now knows the material exists
        # but nothing says whether it holds any property.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'northern_ridge', location = 'Northern Ridge',
                    position_x_m = 0, position_y_m = 1800,
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            conn.commit()
        survey = next(
            a for a in possible_actions("cato")
            if a["action"] == "survey" and a["target"] == "northern_ridge"
        )
        ok, message = start_action("cato", {"action": "survey", "target": survey["target"], "reason": "Look around."})
        assert ok, message
        with connect() as conn:
            end = conn.execute(
                "SELECT j.end_minute FROM citizens c JOIN jobs j ON j.id = c.active_job_id WHERE c.id = 'cato'"
            ).fetchone()["end_minute"]
        complete_due_jobs(int(end))

        rows = {row["material"]: row for row in material_testing_attention("cato")}
        assert "Ferrite Stone" in rows, rows
        assert rows["Ferrite Stone"]["tried"] == {}
        assert rows["Ferrite Stone"]["untried"] == ["thermal_assay", "electrical_assay", "mechanical_assay"]
        assert rows["Ferrite Stone"]["sample_in_storage_here"] is False
        materials = section(cato_prompt(), materials_header)
        assert "Ferrite Stone (confirmed a deposit at Northern Ridge)" in materials, materials
        assert "never tried by you: thermal-response assay" in materials
        assert "smelt" not in materials.lower()
        assert "field_response" not in materials

        # Back at Seed Site with a stored sample, Cato's own test history is recorded.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            conn.execute("INSERT OR REPLACE INTO resources(name, amount) VALUES ('Ferrite Stone', 10)")
            conn.commit()
        assay = next(
            a for a in possible_actions("cato")
            if a["action"] == "experiment" and a["target"] == "thermal_assay:Ferrite Stone"
        )
        ok, message = start_action(
            "cato",
            {"action": "experiment", "target": assay["target"], "material": "Ferrite Stone", "reason": "Untested."},
        )
        assert ok, message
        with connect() as conn:
            end = conn.execute(
                "SELECT j.end_minute FROM citizens c JOIN jobs j ON j.id = c.active_job_id WHERE c.id = 'cato'"
            ).fetchone()["end_minute"]
        complete_due_jobs(int(end))

        rows = {row["material"]: row for row in material_testing_attention("cato")}
        ferrite = rows["Ferrite Stone"]
        assert ferrite["tried"] == {"thermal_assay": {"runs": 1, "last_outcome": "discovery"}}, ferrite
        assert ferrite["untried"] == ["electrical_assay", "mechanical_assay"]
        assert ferrite["sample_in_storage_here"] is True
        materials = section(cato_prompt(), materials_header)
        assert "thermal-response assay run 1x, last run revealed a new property" in materials, materials
        assert "never tried by you: electrical-response assay, mechanical-response assay" in materials

        # Another citizen's tests never appear in Cato's history.
        assert all(row["material"] != "Ferrite Stone" or row["tried"] == {} for row in material_testing_attention("bex"))

    print("v1.1.12 curiosity and stock trend smoke passed")


if __name__ == "__main__":
    main()
