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
    from agent_city.simulation import daily_phase

    assert daily_phase(5 * 60 + 59) == "quiet"
    assert daily_phase(6 * 60) == "active"
    assert daily_phase(19 * 60 + 59) == "active"
    assert daily_phase(20 * 60) == "wind_down"
    assert daily_phase(21 * 60 + 59) == "wind_down"
    assert daily_phase(22 * 60) == "quiet"

    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import complete_due_jobs, possible_actions, start_action
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # Critically low energy at a reachable charger is a hard recharge priority,
        # even during the daytime active cycle.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET energy = 20, battery_health = 100,
                    location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'aris'
                """
            )
            set_time(conn, 10 * 60)

        active_low = possible_actions("aris")
        assert active_low
        assert {a["action"] for a in active_low} == {"charge"}

        # Overnight docking repeats real +25 charge cycles until usable capacity,
        # instead of releasing the citizen after one partial cycle.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET energy = 30, battery_health = 100,
                    location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            set_time(conn, 23 * 60)

        for expected in (55.0, 80.0, 100.0):
            choices = possible_actions("cato")
            assert {a["action"] for a in choices} == {"charge"}
            charge = choices[0]
            ok, message = start_action(
                "cato",
                {
                    "action": "charge",
                    "target": charge["target"],
                    "reason": "Overnight recharge cycle.",
                },
            )
            assert ok, message
            with connect() as conn:
                job = conn.execute(
                    """
                    SELECT j.* FROM citizens c
                    JOIN jobs j ON j.id = c.active_job_id
                    WHERE c.id = 'cato'
                    """
                ).fetchone()
                assert job is not None
                end = int(job["end_minute"])
                set_time(conn, end)
            complete_due_jobs(end)
            with connect() as conn:
                row = conn.execute("SELECT energy FROM citizens WHERE id = 'cato'").fetchone()
                assert float(row["energy"]) == expected

        full_night = possible_actions("cato")
        assert not any(a["action"] == "charge" for a in full_night)
        assert not any(
            a["action"] in {
                "survey",
                "extract",
                "experiment",
                "fabricate",
                "construct",
                "plan_project",
                "reserve_project",
            }
            for a in full_night
        )
        assert not any(
            a["action"] == "travel" and a.get("target") != "seed_site"
            for a in full_night
        )

        # Battery health is the true full-charge ceiling. Do not offer a useless
        # charging cycle when current Energy already equals degraded capacity.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET energy = 82, battery_health = 82,
                    location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            set_time(conn, 23 * 60 + 15)

        capped = possible_actions("bex")
        assert not any(a["action"] == "charge" for a in capped)

        # Wind-down allows closure/social/maintenance actions but blocks starting
        # a fresh expedition or heavy production task.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET energy = 100, battery_health = 100,
                    location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'vale'
                """
            )
            set_time(conn, 20 * 60 + 30)

        wind_down = possible_actions("vale")
        assert wind_down
        assert not any(a["action"] == "local_move" and "Return locally" not in a["label"] for a in wind_down)
        assert not any(a["action"] == "travel" and a.get("target") != "seed_site" for a in wind_down)
        assert not any(
            a["action"] in {
                "survey",
                "extract",
                "experiment",
                "fabricate",
                "construct",
                "plan_project",
                "reserve_project",
            }
            for a in wind_down
        )

    js = (Path(__file__).resolve().parents[1] / "static" / "app.js").read_text(encoding="utf-8")
    css = (Path(__file__).resolve().parents[1] / "static" / "styles.css").read_text(encoding="utf-8")
    assert "function visualDayPhase" in js
    assert "document.body.dataset.dayPhase = dayPhase" in js
    assert 'body[data-day-phase="dawn"] .world-stage' in css
    assert 'body[data-day-phase="day"] .world-stage' in css
    assert 'body[data-day-phase="dusk"] .world-stage' in css
    assert 'body[data-day-phase="night"] .world-stage' in css

    print("Agent City v0.8.5 daily rhythm/recharge smoke passed.")


if __name__ == "__main__":
    main()
