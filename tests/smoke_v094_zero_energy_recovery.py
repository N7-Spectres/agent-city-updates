from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, set_meta
        from agent_city.simulation import (
            autonomous_actions,
            possible_actions,
            recover_zero_energy_charger_deadlocks,
        )

        init_db()

        with connect() as conn:
            set_meta(conn, "sim_minute", 900)

            charger = conn.execute(
                """
                SELECT * FROM structures
                WHERE provides_charging = 1
                  AND location_id = 'seed_site'
                ORDER BY id LIMIT 1
                """
            ).fetchone()
            assert charger is not None

            charger_x = float(charger["x_m"])
            charger_y = float(charger["y_m"])

            # Reproduce the user-observed class of deadlock: Bex is still at the
            # charging location, but a local offset leaves her outside the 5 m
            # charger radius after reaching absolute zero.
            conn.execute(
                """
                UPDATE citizens
                SET energy = 0,
                    active_job_id = NULL,
                    current_activity = 'Available',
                    location_id = 'seed_site',
                    location = 'Seed Site',
                    position_x_m = ?,
                    position_y_m = ?,
                    last_planned_minute = 890
                WHERE id = 'bex'
                """,
                (charger_x + 60.0, charger_y),
            )

            # Cato is also at zero, but away from any charger. The recovery must
            # not teleport citizens across locations.
            rocky = conn.execute(
                "SELECT x_m, y_m FROM locations WHERE id = 'rocky_basin'"
            ).fetchone()
            conn.execute(
                """
                UPDATE citizens
                SET energy = 0,
                    active_job_id = NULL,
                    current_activity = 'Available',
                    location_id = 'rocky_basin',
                    location = 'Rocky Basin',
                    position_x_m = ?,
                    position_y_m = ?,
                    last_planned_minute = 890
                WHERE id = 'cato'
                """,
                (float(rocky["x_m"]), float(rocky["y_m"])),
            )

            # Aris is already physically within charger reach. No admin recovery
            # should be recorded or applied.
            conn.execute(
                """
                UPDATE citizens
                SET energy = 0,
                    active_job_id = NULL,
                    current_activity = 'Available',
                    location_id = 'seed_site',
                    location = 'Seed Site',
                    position_x_m = ?,
                    position_y_m = ?,
                    last_planned_minute = 890
                WHERE id = 'aris'
                """,
                (charger_x + 2.0, charger_y),
            )
            conn.commit()

        recovered = recover_zero_energy_charger_deadlocks(900)
        assert recovered == ["bex"], recovered

        with connect() as conn:
            bex = conn.execute(
                """
                SELECT energy, position_x_m, position_y_m,
                       active_job_id, current_activity, last_planned_minute
                FROM citizens WHERE id = 'bex'
                """
            ).fetchone()
            assert float(bex["energy"]) == 0.0
            assert math.isclose(float(bex["position_x_m"]), charger_x, abs_tol=1e-9)
            assert math.isclose(float(bex["position_y_m"]), charger_y, abs_tol=1e-9)
            assert bex["active_job_id"] is None
            assert bex["current_activity"] == "Available"
            assert int(bex["last_planned_minute"]) <= 840

            cato = conn.execute(
                "SELECT position_x_m, position_y_m FROM citizens WHERE id = 'cato'"
            ).fetchone()
            assert math.isclose(float(cato["position_x_m"]), float(rocky["x_m"]), abs_tol=1e-9)
            assert math.isclose(float(cato["position_y_m"]), float(rocky["y_m"]), abs_tol=1e-9)

            aris = conn.execute(
                "SELECT position_x_m, position_y_m FROM citizens WHERE id = 'aris'"
            ).fetchone()
            assert math.isclose(float(aris["position_x_m"]), charger_x + 2.0, abs_tol=1e-9)
            assert math.isclose(float(aris["position_y_m"]), charger_y, abs_tol=1e-9)

            diagnostics = conn.execute(
                """
                SELECT message FROM history
                WHERE category = 'diagnostic'
                  AND message LIKE '%zero-energy charger offset%'
                ORDER BY id
                """
            ).fetchall()
            assert len(diagnostics) == 1
            assert "Bex" in diagnostics[0]["message"]
            assert "ordinary charging can resume" in diagnostics[0]["message"]

        # Once position is corrected, ordinary physics exposes charging without
        # inventing a special recovery action or granting free energy.
        physical = possible_actions("bex")
        assert any(row["action"] == "charge" for row in physical)
        autonomous = autonomous_actions("bex")
        assert autonomous
        assert all(row["action"] == "charge" for row in autonomous)

        # Recovery is idempotent once Bex is within real charger range.
        assert recover_zero_energy_charger_deadlocks(901) == []
        with connect() as conn:
            diagnostics = conn.execute(
                """
                SELECT COUNT(*) AS n FROM history
                WHERE category = 'diagnostic'
                  AND message LIKE '%zero-energy charger offset%'
                """
            ).fetchone()
            assert int(diagnostics["n"]) == 1

    simulation = (ROOT / "agent_city" / "simulation.py").read_text(encoding="utf-8")
    world = (ROOT / "agent_city" / "world.py").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    assert "def recover_zero_energy_charger_deadlocks(" in simulation
    assert "This is diagnostic/admin recovery, not an in-world citizen action." in simulation
    assert "energy <= 0" in simulation
    assert "location_id = ?" in simulation
    assert "recover_zero_energy_charger_deadlocks(new_minute)" in world
    assert "recover_zero_energy_charger_deadlocks()" in main_py

    print("Agent City v0.9.4 zero-energy charger recovery smoke passed.")


if __name__ == "__main__":
    main()
