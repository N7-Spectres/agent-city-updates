from __future__ import annotations

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
            CRITICAL_RECHARGE_ENERGY,
            autonomous_actions,
            possible_actions,
            start_action,
        )

        init_db()

        with connect() as conn:
            set_meta(conn, "sim_minute", 600)  # active cycle
            conn.execute(
                """
                UPDATE citizens
                SET location_id='seed_site',
                    location='Seed Site',
                    position_x_m=0,
                    position_y_m=0,
                    active_job_id=NULL,
                    current_activity='Available'
                WHERE id IN ('aris', 'bex')
                """
            )
            conn.execute(
                "UPDATE citizens SET energy=100, last_planned_minute=100 WHERE id='aris'"
            )
            conn.execute(
                "UPDATE citizens SET energy=?, last_planned_minute=5 WHERE id='bex'",
                (CRITICAL_RECHARGE_ENERGY - 1,),
            )
            conn.commit()

        # Physical talk remains possible: this is not a new physics prohibition.
        physical = possible_actions("aris")
        assert any(
            row["action"] == "talk" and row["target"] == "bex"
            for row in physical
        )

        # Autonomous planning must not select a critically low citizen as a
        # social target while that citizen needs a chance to recharge.
        autonomous = autonomous_actions("aris")
        assert not any(
            row["action"] == "talk" and row["target"] == "bex"
            for row in autonomous
        )
        assert not any(
            row["action"] == "guided_practice"
            and row.get("learner_id") == "bex"
            for row in autonomous
        )

        # At Seed Site, Bex's own autonomy must prioritize real charging.
        bex_choices = autonomous_actions("bex")
        assert bex_choices
        assert all(row["action"] == "charge" for row in bex_choices)

        # Start-time recheck closes a race where Bex becomes critical after the
        # initiator saw a stale/earlier legal action list.
        with connect() as conn:
            before_aris = float(
                conn.execute("SELECT energy FROM citizens WHERE id='aris'").fetchone()["energy"]
            )
            before_bex = float(
                conn.execute("SELECT energy FROM citizens WHERE id='bex'").fetchone()["energy"]
            )

        ok, message = start_action(
            "aris",
            {
                "action": "talk",
                "target": "bex",
                "reason": "Check in with Bex.",
            },
            autonomous_choice=True,
            autonomous_action_count=max(2, len(physical)),
        )
        assert not ok
        assert "critically low energy" in message.lower()

        with connect() as conn:
            after_aris = float(
                conn.execute("SELECT energy FROM citizens WHERE id='aris'").fetchone()["energy"]
            )
            after_bex = float(
                conn.execute("SELECT energy FROM citizens WHERE id='bex'").fetchone()["energy"]
            )
        assert after_aris == before_aris
        assert after_bex == before_bex

        # Once Bex is no longer critical, an autonomous talk may start, but
        # being somebody else's listener must not reset Bex's planner clock.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET energy=50,
                    active_job_id=NULL,
                    current_activity='Available',
                    last_planned_minute=123
                WHERE id='bex'
                """
            )
            conn.execute(
                """
                UPDATE citizens
                SET energy=100,
                    active_job_id=NULL,
                    current_activity='Available'
                WHERE id='aris'
                """
            )
            conn.commit()

        aris_choices = autonomous_actions("aris")
        talk = next(
            row for row in aris_choices
            if row["action"] == "talk" and row["target"] == "bex"
        )
        ok, _ = start_action(
            "aris",
            {
                "action": "talk",
                "target": "bex",
                "reason": "Talk with Bex while both have enough energy.",
            },
            autonomous_choice=True,
            autonomous_action_count=max(2, len(aris_choices)),
        )
        assert ok, talk

        with connect() as conn:
            bex = conn.execute(
                "SELECT energy, last_planned_minute, active_job_id FROM citizens WHERE id='bex'"
            ).fetchone()
            assert float(bex["energy"]) == 49.0
            assert int(bex["last_planned_minute"]) == 123
            assert bex["active_job_id"] is not None

    print("Agent City v0.9.2 social-energy protection smoke passed.")


if __name__ == "__main__":
    main()
