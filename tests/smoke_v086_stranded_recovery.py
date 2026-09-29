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


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import autonomous_actions, complete_due_jobs, start_action
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # Reproduce Iri's observed trap: Resin Grove, 6% energy, Seed Site charger 1.2 km away.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'resin_grove', location = 'Resin Grove',
                    position_x_m = -1200, position_y_m = 0,
                    energy = 6, battery_health = 100,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'iri'
                """
            )
            set_time(conn, 6 * 60 + 45)

        choices = autonomous_actions("iri")
        home = next(
            a for a in choices
            if a["action"] == "travel" and a["target"] == "seed_site"
        )

        ok, message = start_action(
            "iri",
            {
                "action": "travel",
                "target": home["target"],
                "reason": "Energy is critically low; return to the Charging Station.",
            },
        )
        assert ok, message

        with connect() as conn:
            job = conn.execute(
                """
                SELECT j.* FROM citizens c
                JOIN jobs j ON j.id = c.active_job_id
                WHERE c.id = 'iri'
                """
            ).fetchone()
            assert job is not None
            end = int(job["end_minute"])
            energy_after_departure = float(
                conn.execute("SELECT energy FROM citizens WHERE id = 'iri'").fetchone()["energy"]
            )
            assert 2.3 < energy_after_departure < 2.5
            set_time(conn, end)

        complete_due_jobs(end)

        with connect() as conn:
            iri = conn.execute("SELECT * FROM citizens WHERE id = 'iri'").fetchone()
            assert iri["location_id"] == "seed_site"
            assert float(iri["energy"]) > 0
            assert iri["active_job_id"] is None

        # Once home, critical-energy autonomy should immediately prioritize charging.
        home_choices = autonomous_actions("iri")
        assert home_choices
        assert {a["action"] for a in home_choices} == {"charge"}

        print("Agent City v0.8.6 stranded-citizen recovery smoke passed.")


if __name__ == "__main__":
    main()
