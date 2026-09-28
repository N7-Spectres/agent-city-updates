from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, get_meta, init_db, snapshot
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import (
            complete_due_jobs,
            possible_actions,
            query_spatial_truth,
            record_local_spatial_observation,
            start_action,
        )
        from agent_city.spatial import query_hidden_world
        from agent_city.visitors import (
            complete_due_visitor_travel,
            ensure_visitor,
            start_visitor_travel,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        with connect() as conn:
            seed_first = get_meta(conn, "planet_seed")
            assert seed_first and len(seed_first) >= 16

            # Legacy landmarks retain identity and gain meter coordinates.
            seed_site = conn.execute(
                "SELECT * FROM locations WHERE id = 'seed_site'"
            ).fetchone()
            north = conn.execute(
                "SELECT * FROM locations WHERE id = 'northern_ridge'"
            ).fetchone()
            rocky = conn.execute(
                "SELECT * FROM locations WHERE id = 'rocky_basin'"
            ).fetchone()
            resin = conn.execute(
                "SELECT * FROM locations WHERE id = 'resin_grove'"
            ).fetchone()

            assert float(seed_site["x_m"]) == 0.0
            assert float(seed_site["y_m"]) == 0.0
            assert float(north["x_m"]) == 0.0
            assert float(north["y_m"]) == 1800.0
            assert float(rocky["x_m"]) == 1400.0
            assert float(rocky["y_m"]) == 0.0
            assert float(resin["x_m"]) == -1200.0
            assert float(resin["y_m"]) == 0.0

            citizens = conn.execute(
                "SELECT position_x_m, position_y_m FROM citizens"
            ).fetchall()
            assert citizens
            assert all(float(row["position_x_m"]) == 0.0 for row in citizens)
            assert all(float(row["position_y_m"]) == 0.0 for row in citizens)

            legacy = conn.execute(
                """
                SELECT * FROM generated_deposits
                WHERE source_kind = 'legacy'
                ORDER BY id
                """
            ).fetchall()
            assert {row["id"] for row in legacy} >= {
                "dep_ferrite",
                "dep_veyra",
                "dep_silicate",
                "dep_copper",
                "dep_carbon",
                "dep_clay",
                "dep_fiber",
                "dep_resin",
            }

        # Re-running migrations does not replace the planet.
        init_db()
        with connect() as conn:
            seed_second = get_meta(conn, "planet_seed")
            assert seed_second == seed_first

        # Same point is deterministic.
        first = query_spatial_truth(13.25, -8.75)
        second = query_spatial_truth(13.25, -8.75)
        assert first == second

        # Nearby terrain is continuous rather than one random roll per scan.
        one_meter = query_spatial_truth(14.25, -8.75)
        assert abs(float(first["elevation_m"]) - float(one_meter["elevation_m"])) < 2.0
        assert abs(float(first["roughness"]) - float(one_meter["roughness"])) < 0.1

        # Find a materialized procedural body, then prove nearby coordinates see
        # the same physical body ID instead of minting a new deposit.
        chosen = None
        with connect() as conn:
            for qx, qy in ((0.0, 0.0), (500.0, 500.0), (-500.0, 300.0)):
                query_hidden_world(conn, qx, qy)
                chosen = conn.execute(
                    """
                    SELECT * FROM generated_deposits
                    WHERE source_kind = 'procedural'
                    ORDER BY id
                    LIMIT 1
                    """
                ).fetchone()
                if chosen:
                    break
            assert chosen is not None
            center_x = float(chosen["center_x_m"])
            center_y = float(chosen["center_y_m"])
            stable_id = str(chosen["id"])

            at_center = query_hidden_world(conn, center_x, center_y)
            one_meter_inside = query_hidden_world(conn, center_x + 1.0, center_y)
            ids_center = {body["id"] for body in at_center["deposit_bodies"]}
            ids_meter = {body["id"] for body in one_meter_inside["deposit_bodies"]}
            assert stable_id in ids_center
            assert stable_id in ids_meter

            # Re-querying never changes persisted geometry.
            before = dict(
                conn.execute(
                    "SELECT * FROM generated_deposits WHERE id = ?",
                    (stable_id,),
                ).fetchone()
            )
            query_hidden_world(conn, center_x, center_y)
            after = dict(
                conn.execute(
                    "SELECT * FROM generated_deposits WHERE id = ?",
                    (stable_id,),
                ).fetchone()
            )
            assert before == after
            conn.commit()

        # Raw seed, generated hidden bodies, richness, and hidden geometry never
        # appear in the ordinary civilization-facing snapshot.
        state = snapshot()
        serialized = json.dumps(state, sort_keys=True)
        assert seed_first not in serialized
        assert "generated_deposits" not in state
        assert "world_properties" not in state
        assert "richness" not in serialized
        assert "long_axis_m" not in serialized
        assert "short_axis_m" not in serialized
        assert state["spatial_frame"] == {
            "id": "seed_site_local",
            "units": "meters",
            "origin_location_id": "seed_site",
        }
        assert state["spatial_observations"] == []

        # The minimal observation contract enforces real observer position/range.
        ok, observation_id, message = record_local_spatial_observation(
            "aris",
            50.0,
            0.0,
            max_range_m=2.0,
        )
        assert not ok
        assert observation_id is None
        assert "outside" in message.lower()

        ok, observation_id, _ = record_local_spatial_observation(
            "aris",
            1.0,
            0.0,
            max_range_m=2.0,
            observation_kind="stage1_test_observation",
        )
        assert ok
        assert observation_id is not None

        state = snapshot()
        observation = next(
            row for row in state["spatial_observations"]
            if row["id"] == observation_id
        )
        assert observation["observer_id"] == "aris"
        assert observation["frame_id"] == "seed_site_local"
        assert observation["x_m"] == 1.0
        assert "terrain_class" in observation
        assert "geology_class" in observation
        assert "richness" not in observation
        assert "long_axis_m" not in observation

        # Existing route travel keeps meter position aligned with landmark truth.
        ok, _ = start_action(
            "bex",
            {
                "action": "travel",
                "target": "rocky_basin",
                "reason": "Verify route travel preserves the new spatial anchor.",
            },
        )
        assert ok
        with connect() as conn:
            job = conn.execute(
                """
                SELECT j.*
                FROM citizens c
                JOIN jobs j ON j.id = c.active_job_id
                WHERE c.id = 'bex'
                """
            ).fetchone()
            assert job is not None
            end_minute = int(job["end_minute"])
        complete_due_jobs(end_minute)

        with connect() as conn:
            bex = conn.execute(
                "SELECT * FROM citizens WHERE id = 'bex'"
            ).fetchone()
            assert bex["location_id"] == "rocky_basin"
            assert float(bex["position_x_m"]) == 1400.0
            assert float(bex["position_y_m"]) == 0.0

        # Visitor landmark travel uses the same meter frame.
        visitor = ensure_visitor("Spatial Test Visitor")
        assert float(visitor["x_m"]) == 0.0
        assert float(visitor["y_m"]) == 0.0

        ok, _ = start_visitor_travel("Spatial Test Visitor", "resin_grove")
        assert ok
        with connect() as conn:
            row = conn.execute(
                "SELECT * FROM visitor_presence WHERE visitor = 'Spatial Test Visitor'"
            ).fetchone()
            travel_end = int(row["travel_end_minute"])
        complete_due_visitor_travel(travel_end)

        with connect() as conn:
            row = conn.execute(
                "SELECT * FROM visitor_presence WHERE visitor = 'Spatial Test Visitor'"
            ).fetchone()
            assert row["location_id"] == "resin_grove"
            assert float(row["x_m"]) == -1200.0
            assert float(row["y_m"]) == 0.0

        # Stage 1 intentionally does not expose arbitrary continuous-move actions.
        actions = possible_actions("aris")
        assert not any(a["action"] in {"move_meter", "free_roam", "scan"} for a in actions)

        print("Agent City v0.8 seeded-world Stage 1 smoke test passed.")


if __name__ == "__main__":
    main()
