from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


RAW_STOCK = {
    "Ferrite Stone": 40.0,
    "Silicate": 40.0,
    "Copper-like Ore": 40.0,
    "Carbonaceous Rock": 40.0,
    "Native Resin": 40.0,
}

STARTER_OUTPUTS = {
    "Processed structural material",
    "Conductive wire",
    "Mechanical components",
    "Lubricant",
    "Fasteners",
    "Battery cells",
    "Basic electronics",
}


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
    from agent_city.db import connect
    from agent_city.simulation import complete_due_jobs

    job = active_job(citizen_id)
    complete_due_jobs(int(job["end_minute"]))
    with connect() as conn:
        set_time(conn, int(job["end_minute"]))
        conn.execute(
            """
            UPDATE citizens
            SET energy = 100, active_job_id = NULL, current_activity = 'Available'
            WHERE id = ?
            """,
            (citizen_id,),
        )
        conn.commit()
    return job


def run_experiment(citizen_id: str, method: str, material: str) -> dict:
    from agent_city.simulation import possible_actions, start_action

    action = next(
        row for row in possible_actions(citizen_id)
        if row["action"] == "experiment"
        and row["experiment_method"] == method
        and row["material"] == material
    )
    ok, message = start_action(
        citizen_id,
        {
            "action": "experiment",
            "target": action["target"],
            "material": material,
            "reason": f"Test stored {material} without assuming the result.",
        },
    )
    assert ok, message
    return finish(citizen_id)


def run_process(citizen_id: str, process_key: str) -> dict:
    from agent_city.simulation import possible_actions, start_action

    action = next(
        row for row in possible_actions(citizen_id)
        if row["action"] == "process_material"
        and row["target"] == process_key
    )
    ok, message = start_action(
        citizen_id,
        {
            "action": "process_material",
            "target": process_key,
            "reason": "Use the validated production process with physically available inputs.",
        },
    )
    assert ok, message
    return finish(citizen_id)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import STARTING_RESOURCES, connect, init_db, snapshot
        from agent_city.material_independence import (
            PRODUCTION_PROCESSES,
            citizen_knows_production_process,
        )
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import (
            local_resource_sustainability_attention,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # Simulate the long-term case v1.0 exists to solve: the manufactured
        # starter crate is exhausted, while raw locally extractable materials
        # have reached Seed Site storage through prior physical work.
        with connect() as conn:
            for material in STARTING_RESOURCES:
                conn.execute(
                    "UPDATE resources SET amount = 0 WHERE name = ?",
                    (material,),
                )
            for material, amount in RAW_STOCK.items():
                conn.execute(
                    """
                    INSERT INTO resources(name, amount) VALUES (?, ?)
                    ON CONFLICT(name) DO UPDATE SET amount = excluded.amount
                    """,
                    (material, amount),
                )
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            set_time(conn, 20_000)

        initial = snapshot()
        assert "world_properties" not in initial
        assert "generated_deposits" not in initial
        assert "planet_seed" not in initial
        assert initial["production_events"] == []

        # No production recipe exists merely because raw stock is sitting there.
        assert not any(
            row["action"] == "process_material"
            for row in possible_actions("cato")
        )
        with connect() as conn:
            assert not any(
                citizen_knows_production_process(conn, "cato", key)
                for key in PRODUCTION_PROCESSES
            )

        # Ferrite -> discovered smelting response -> crude metal.
        run_experiment("cato", "thermal_assay", "Ferrite Stone")
        with connect() as conn:
            assert citizen_knows_production_process(conn, "cato", "smelt_crude_metal")
            assert not citizen_knows_production_process(conn, "bex", "smelt_crude_metal")

        run_process("cato", "smelt_crude_metal")

        # Crude metal itself must be physically tested before parts-forming exists.
        assert not any(
            row["action"] == "process_material"
            and row["target"] == "form_fasteners"
            for row in possible_actions("cato")
        )
        run_experiment("cato", "mechanical_assay", "Crude Metal Stock")
        with connect() as conn:
            assert citizen_knows_production_process(conn, "cato", "form_fasteners")
            assert citizen_knows_production_process(conn, "cato", "form_mechanical_components")

        run_process("cato", "form_fasteners")
        run_process("cato", "smelt_crude_metal")
        run_process("cato", "smelt_crude_metal")
        run_process("cato", "form_mechanical_components")

        # Silicate -> locally reproducible structural stock.
        run_experiment("cato", "thermal_assay", "Silicate")
        run_process("cato", "cast_structural_material")

        # Resin requires two distinct thermal discoveries before lubricant is learned.
        run_experiment("cato", "thermal_assay", "Native Resin")
        with connect() as conn:
            assert not citizen_knows_production_process(conn, "cato", "refine_lubricant")
        run_experiment("cato", "thermal_assay", "Native Resin")
        run_process("cato", "refine_lubricant")

        # Copper conductivity alone is not wire-making knowledge.
        run_experiment("cato", "electrical_assay", "Copper-like Ore")
        with connect() as conn:
            assert not citizen_knows_production_process(conn, "cato", "draw_conductive_wire")
        run_experiment("cato", "mechanical_assay", "Copper-like Ore")
        run_process("cato", "draw_conductive_wire")
        run_process("cato", "draw_conductive_wire")

        # Carbon and resin electrical behavior complete the local cell/electronics
        # evidence chain. Nothing is unlocked from a single plausible material.
        run_experiment("cato", "electrical_assay", "Carbonaceous Rock")
        run_experiment("cato", "electrical_assay", "Native Resin")

        with connect() as conn:
            assert citizen_knows_production_process(conn, "cato", "assemble_battery_cells")
            assert not citizen_knows_production_process(conn, "cato", "assemble_basic_electronics")

        # The second carbon electrical property supports electronics assembly.
        run_experiment("cato", "electrical_assay", "Carbonaceous Rock")
        with connect() as conn:
            assert citizen_knows_production_process(conn, "cato", "assemble_basic_electronics")

        run_process("cato", "assemble_battery_cells")
        run_process("cato", "assemble_battery_cells")
        run_process("cato", "assemble_basic_electronics")

        # Every manufactured starter category can now be physically replenished
        # from non-starter stock through learned, source-backed processes.
        with connect() as conn:
            amounts = {
                row["name"]: float(row["amount"])
                for row in conn.execute("SELECT name, amount FROM resources")
            }
            for material in STARTER_OUTPUTS:
                assert amounts.get(material, 0.0) > 0.0, material

            learned = {
                row["process_key"]
                for row in conn.execute(
                    """
                    SELECT process_key FROM learned_processes
                    WHERE citizen_id = 'cato' AND process_kind = 'production'
                    """
                )
            }
            assert learned == set(PRODUCTION_PROCESSES)

            production_count = int(
                conn.execute("SELECT COUNT(*) AS n FROM production_events").fetchone()["n"]
            )
            assert production_count >= 12

        # Sustainability context flips from "no process" to the real learned
        # replenishment processes rather than staying hard-coded.
        attention = {
            row["material"]: row
            for row in local_resource_sustainability_attention("cato")
        }
        for material in STARTER_OUTPUTS:
            assert (
                attention[material]["replenishment_status"]
                == "validated_production_process_available"
            )
            assert attention[material]["validated_processes"]

        # Locally produced maintenance parts can service real infrastructure after
        # the starter stock has been exhausted.
        with connect() as conn:
            charger = conn.execute(
                "SELECT id FROM structures WHERE name = 'Charging Station'"
            ).fetchone()
            charger_id = int(charger["id"])
            conn.execute(
                "UPDATE structures SET condition = 89 WHERE id = ?",
                (charger_id,),
            )
            conn.commit()

        service = next(
            row for row in possible_actions("cato")
            if row["action"] == "service_structure"
            and row["target"] == str(charger_id)
        )
        ok, message = start_action(
            "cato",
            {
                "action": "service_structure",
                "target": service["target"],
                "reason": "Use locally reproduced maintenance stock to service the due charger.",
            },
        )
        assert ok, message
        finish("cato")

        with connect() as conn:
            charger = conn.execute(
                "SELECT condition FROM structures WHERE id = ?",
                (charger_id,),
            ).fetchone()
            assert float(charger["condition"]) == 100.0
            event = conn.execute(
                """
                SELECT * FROM maintenance_events
                WHERE target_type = 'structure' AND target_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (str(charger_id),),
            ).fetchone()
            assert event is not None
            assert event["outcome"] == "success"

        print("Agent City v1.0 material-independence smoke passed")


if __name__ == "__main__":
    main()
