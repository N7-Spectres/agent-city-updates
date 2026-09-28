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

        from agent_city.db import connect, init_db, snapshot
        from agent_city.exploration import (
            accept_shared_activity,
            propose_shared_activity,
            shared_activity_payload,
            start_local_inspection,
            start_local_move,
            start_shared_activity,
        )
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import complete_due_jobs, possible_actions, start_action
        from agent_city.spatial import query_hidden_world
        from agent_city.visitors import (
            ensure_visitor,
            presence_payload,
            start_visitor_travel,
            visit_access_payload,
        )
        from agent_city.visits import ensure_visit_schema, get_or_create_active_visit

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # ----- Citizen local movement -----
        with connect() as conn:
            set_time(conn, 500)
            ok, job_id, message = start_local_move(
                conn, "aris", 80.0, 0.0, now=500, reason="Explore east of Seed Site."
            )
            assert ok, message
            conn.commit()
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            assert job["action"] == "local_move"
            assert float(job["start_x_m"]) == 0.0
            assert float(job["target_x_m"]) == 80.0
            assert float(job["path_distance_m"]) == 80.0
            assert float(job["terrain_multiplier"]) > 0
            assert float(conn.execute("SELECT position_x_m FROM citizens WHERE id = 'aris'").fetchone()["position_x_m"]) == 0.0
            mid = int(job["start_minute"]) + max(1, (int(job["end_minute"]) - int(job["start_minute"])) // 2)
            set_time(conn, mid)

        state = snapshot()
        aris = next(c for c in state["citizens"] if c["id"] == "aris")
        assert aris["local_movement"] is not None
        assert 0.0 < float(aris["position_x_m"]) < 80.0
        assert 0.0 < float(aris["local_movement"]["progress"]) < 1.0

        # Reopening/migrating while the job is active preserves derived position.
        before_reopen = float(aris["position_x_m"])
        init_db()
        after = snapshot()
        aris_after = next(c for c in after["citizens"] if c["id"] == "aris")
        assert float(aris_after["position_x_m"]) == before_reopen

        with connect() as conn:
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            end = int(job["end_minute"])
        complete_due_jobs(end)
        with connect() as conn:
            aris_row = conn.execute("SELECT * FROM citizens WHERE id = 'aris'").fetchone()
            assert float(aris_row["position_x_m"]) == 80.0
            assert aris_row["active_job_id"] is None

        # A citizen away from the landmark cannot use the legacy route network.
        aris_actions = possible_actions("aris")
        assert not any(a["action"] == "travel" for a in aris_actions)
        assert any(
            a["action"] == "local_move" and abs(float(a["target_x_m"])) < 0.01
            for a in aris_actions
        )

        # Face-to-face is meter-aware inside the same named region.
        ensure_visitor("Distance Visitor")
        access = visit_access_payload("Distance Visitor", "aris")
        assert access["accessible"] is False
        assert access["status"] == "remote"
        assert float(access["distance_m"]) > 70.0

        # ----- Baseline direct inspection -----
        with connect() as conn:
            set_time(conn, end + 10)
            ok, inspect_job_id, message = start_local_inspection(
                conn, "aris", now=end + 10
            )
            assert ok, message
            conn.commit()
            inspect_job = conn.execute("SELECT * FROM jobs WHERE id = ?", (inspect_job_id,)).fetchone()
        complete_due_jobs(int(inspect_job["end_minute"]))
        with connect() as conn:
            obs = conn.execute(
                "SELECT * FROM spatial_observations WHERE source_job_id = ?",
                (inspect_job_id,),
            ).fetchone()
            assert obs is not None
            assert obs["detail_level"] == "baseline"
            assert obs["geology_class"] == "unclassified"
            assert obs["material"] is None
            assert float(obs["radius_m"]) == 1.5

        # Find a seeded body and prove nearby baseline encounters keep one subject ID.
        with connect() as conn:
            for qx, qy in ((0.0, 0.0), (300.0, 300.0), (-300.0, 200.0), (600.0, -200.0)):
                query_hidden_world(conn, qx, qy)
                body = conn.execute(
                    """
                    SELECT * FROM generated_deposits
                    WHERE source_kind = 'procedural'
                    ORDER BY id LIMIT 1
                    """
                ).fetchone()
                if body:
                    break
            assert body is not None
            body_id = str(body["id"])
            bx = float(body["center_x_m"])
            by = float(body["center_y_m"])
            conn.execute(
                """
                UPDATE citizens
                SET position_x_m = ?, position_y_m = ?, energy = 100,
                    active_job_id = NULL, current_activity = 'Available',
                    location_id = 'seed_site', location = 'Seed Site'
                WHERE id = 'noma'
                """,
                (bx, by),
            )
            set_time(conn, 1000)
            ok, obs_job_1, _ = start_local_inspection(conn, "noma", now=1000)
            assert ok
            conn.commit()
            job1 = conn.execute("SELECT * FROM jobs WHERE id = ?", (obs_job_1,)).fetchone()
        complete_due_jobs(int(job1["end_minute"]))
        with connect() as conn:
            first_obs = conn.execute(
                "SELECT * FROM spatial_observations WHERE source_job_id = ?",
                (obs_job_1,),
            ).fetchone()
            assert first_obs["deposit_id"] == body_id
            assert first_obs["material"] is None
            now = int(job1["end_minute"]) + 5
            set_time(conn, now)
            ok, move_one_id, _ = start_local_move(conn, "noma", bx + 1.0, by, now=now)
            assert ok
            conn.commit()
            move_one = conn.execute("SELECT * FROM jobs WHERE id = ?", (move_one_id,)).fetchone()
        complete_due_jobs(int(move_one["end_minute"]))
        with connect() as conn:
            now = int(move_one["end_minute"]) + 5
            set_time(conn, now)
            ok, obs_job_2, _ = start_local_inspection(conn, "noma", now=now)
            assert ok
            conn.commit()
            job2 = conn.execute("SELECT * FROM jobs WHERE id = ?", (obs_job_2,)).fetchone()
        complete_due_jobs(int(job2["end_minute"]))
        with connect() as conn:
            second_obs = conn.execute(
                "SELECT * FROM spatial_observations WHERE source_job_id = ?",
                (obs_job_2,),
            ).fetchone()
            assert second_obs["deposit_id"] == body_id
            assert second_obs["material"] is None

        # Low energy prevents local movement that would violate charger reserve.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET position_x_m = 0, position_y_m = 0, location_id = 'seed_site',
                    location = 'Seed Site', energy = 5.1, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            set_time(conn, 1500)
            ok, _, message = start_local_move(conn, "bex", 120.0, 0.0, now=1500)
            assert not ok
            assert "reserve" in message.lower()

        # ----- Shared proposal / accept / physical start -----
        visitor = "Shared Visitor"
        ensure_visitor(visitor)
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET position_x_m = 0, position_y_m = 0, location_id = 'seed_site',
                    location = 'Seed Site', energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'vale'
                """
            )
            conn.execute(
                "UPDATE visitor_presence SET location_id = 'seed_site', x_m = 0, y_m = 0 WHERE visitor = ?",
                (visitor,),
            )
            set_time(conn, 2000)
            visit = get_or_create_active_visit(conn, visitor, "vale", 2000)
            visit_id = int(visit["id"])
            exchange_cur = conn.execute(
                """
                INSERT INTO conversations
                (sim_minute, visitor, citizen_id, visitor_text, citizen_text, visit_id)
                VALUES (?, ?, 'vale', ?, ?, ?)
                """,
                (
                    2000,
                    visitor,
                    "Want to walk east and take a look together?",
                    "I can agree to that as a proposal, if the physical action is validated.",
                    visit_id,
                ),
            )
            exchange_id = int(exchange_cur.lastrowid)

            # Bad provenance is rejected.
            ok, _, message = propose_shared_activity(
                conn,
                visitor=visitor,
                citizen_id="vale",
                target_x_m=40.0,
                target_y_m=0.0,
                objective="Walk east together and inspect the destination.",
                source_visit_id=visit_id,
                source_exchange_id=exchange_id + 999,
                now=2000,
            )
            assert not ok
            assert "source exchange" in message.lower()

            ok, activity_id, message = propose_shared_activity(
                conn,
                visitor=visitor,
                citizen_id="vale",
                target_x_m=40.0,
                target_y_m=0.0,
                objective="Walk east together and inspect the destination.",
                source_visit_id=visit_id,
                source_exchange_id=exchange_id,
                now=2000,
            )
            assert ok, message
            conn.commit()
            proposal = shared_activity_payload(conn, activity_id, 2000)
            assert proposal["status"] == "proposed"
            assert proposal["citizen_job_id"] is None
            assert proposal.get("movement") is None
            assert float(conn.execute("SELECT position_x_m FROM citizens WHERE id = 'vale'").fetchone()["position_x_m"]) == 0.0
            assert float(conn.execute("SELECT x_m FROM visitor_presence WHERE visitor = ?", (visitor,)).fetchone()["x_m"]) == 0.0

            # Wrong visitor cannot accept.
            ok, _, _ = accept_shared_activity(conn, activity_id, "Other Visitor", now=2001)
            assert not ok

            ok, no_job, message = accept_shared_activity(conn, activity_id, visitor, now=2001)
            assert ok, message
            assert no_job is None
            conn.commit()
            accepted = shared_activity_payload(conn, activity_id, 2001)
            assert accepted["status"] == "accepted"
            assert accepted["started_minute"] is None
            assert accepted.get("movement") is None

            # Acceptance alone did not change physical position.
            assert float(conn.execute("SELECT position_x_m FROM citizens WHERE id = 'vale'").fetchone()["position_x_m"]) == 0.0

            ok, shared_job_id, message = start_shared_activity(conn, activity_id, visitor, now=2002)
            assert ok, message
            assert shared_job_id is not None
            conn.commit()
            active = shared_activity_payload(conn, activity_id, 2002)
            assert active["status"] == "active"
            assert active["citizen_job_id"] == shared_job_id
            shared_job = conn.execute("SELECT * FROM jobs WHERE id = ?", (shared_job_id,)).fetchone()
            assert shared_job["action"] == "shared_local_activity"

            # Legacy visitor route travel is blocked during shared movement.
            route_ok, route_message = start_visitor_travel(visitor, "resin_grove")
            assert not route_ok
            assert "shared physical activity" in route_message.lower()

            mid = int(shared_job["start_minute"]) + max(
                1, (int(shared_job["end_minute"]) - int(shared_job["start_minute"])) // 2
            )
            set_time(conn, mid)

        mid_state = snapshot()
        vale = next(c for c in mid_state["citizens"] if c["id"] == "vale")
        assert vale["local_movement"] is not None
        assert 0.0 < float(vale["position_x_m"]) < 40.0
        presence = presence_payload(visitor)
        assert presence["shared_activity_id"] == activity_id
        assert abs(float(presence["x_m"]) - float(vale["position_x_m"])) < 0.001

        access = visit_access_payload(visitor, "vale")
        assert access["accessible"] is False
        assert access["status"] == "shared_activity_active"

        complete_due_jobs(int(shared_job["end_minute"]))
        with connect() as conn:
            completed = conn.execute(
                "SELECT * FROM shared_activities WHERE id = ?",
                (activity_id,),
            ).fetchone()
            assert completed["status"] == "complete"
            assert completed["outcome"] == "success"
            assert completed["observation_id"] is not None
            obs = conn.execute(
                "SELECT * FROM spatial_observations WHERE id = ?",
                (completed["observation_id"],),
            ).fetchone()
            assert obs["detail_level"] == "baseline"
            assert obs["observer_id"] == "vale"
            assert obs["source_job_id"] == shared_job_id
            assert obs["material"] is None

            vale_row = conn.execute("SELECT * FROM citizens WHERE id = 'vale'").fetchone()
            visitor_row = conn.execute(
                "SELECT * FROM visitor_presence WHERE visitor = ?",
                (visitor,),
            ).fetchone()
            assert float(vale_row["position_x_m"]) == 40.0
            assert float(visitor_row["x_m"]) == 40.0

        # After leaving the landmark by shared walk, legacy route departure remains blocked.
        route_ok, route_message = start_visitor_travel(visitor, "resin_grove")
        assert not route_ok
        assert "landmark" in route_message.lower()

        # ----- Legacy route travel still works when physically at the landmark -----
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET position_x_m = 0, position_y_m = 0, location_id = 'seed_site',
                    location = 'Seed Site', energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            set_time(conn, 3000)
        travel = next(
            a for a in possible_actions("cato")
            if a["action"] == "travel" and a["target"] == "resin_grove"
        )
        ok, _ = start_action(
            "cato",
            {
                "action": "travel",
                "target": travel["target"],
                "reason": "Use the existing landmark route.",
            },
        )
        assert ok
        with connect() as conn:
            job = conn.execute(
                """
                SELECT j.* FROM citizens c
                JOIN jobs j ON j.id = c.active_job_id
                WHERE c.id = 'cato'
                """
            ).fetchone()
        complete_due_jobs(int(job["end_minute"]))
        with connect() as conn:
            cato = conn.execute("SELECT * FROM citizens WHERE id = 'cato'").fetchone()
            assert cato["location_id"] == "resin_grove"
            assert float(cato["position_x_m"]) == -1200.0
            assert float(cato["position_y_m"]) == 0.0

        # Hidden seeded-world truth remains hidden from ordinary state.
        state = snapshot()
        assert "generated_deposits" not in state
        assert "planet_seed" not in state
        assert "shared_activities" in state
        assert any(row["id"] == activity_id for row in state["shared_activities"])

        print("Agent City v0.8 Stage 2 exploration/shared-activity smoke test passed.")


if __name__ == "__main__":
    main()
