from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema, knowledge_snapshot_for
        from agent_city.spatial_memory import (
            spatial_context_for,
            spatial_snapshot_for,
            sync_spatial_observations,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Compatibility with shipped v0.7 before Simulation's spatial schema merges.
        assert spatial_snapshot_for("noma") == []

        with connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS spatial_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observer_id TEXT NOT NULL,
                    source_job_id INTEGER,
                    observation_kind TEXT NOT NULL,
                    frame_id TEXT NOT NULL,
                    x_m REAL NOT NULL,
                    y_m REAL NOT NULL,
                    radius_m REAL NOT NULL DEFAULT 1,
                    observed_minute INTEGER NOT NULL,
                    terrain_class TEXT NOT NULL,
                    elevation_m REAL NOT NULL,
                    geology_class TEXT NOT NULL,
                    deposit_id TEXT,
                    material TEXT,
                    summary TEXT NOT NULL
                );
                """
            )

            # Routine meter-scale observation with no stable subject should not
            # become durable Memory.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', NULL, 'field_observation', 'seed_site_local',
                    101.27, -18.41, 1, 1000, 'open_ground',
                    2.3, 'silicate', NULL, NULL,
                    'Terrain open_ground; elevation 2.3 m; geology silicate'
                )
                """
            )

            # First contact with a stable generated deposit is salient.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 8101, 'field_observation', 'seed_site_local',
                    123.4567, -45.9876, 5, 1010, 'broken',
                    8.24, 'ferric', 'gdep_same_body', 'Ferrite Stone',
                    'Contact with Ferrite Stone body gdep_same_body'
                )
                """
            )
            first_id = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

            # Same body, same method, same precision. This is continuity, not a
            # second durable discovery.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 8102, 'field_observation', 'seed_site_local',
                    125.9, -43.2, 5, 1020, 'broken',
                    8.1, 'ferric', 'gdep_same_body', 'Ferrite Stone',
                    'Repeated contact with Ferrite Stone body gdep_same_body'
                )
                """
            )

            # Better instrument precision for the same stable body is meaningful.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 8103, 'instrument_scan', 'seed_site_local',
                    124.34, -44.76, 0.4, 1030, 'broken',
                    8.18, 'ferric', 'gdep_same_body', 'Ferrite Stone',
                    'Instrument scan refined contact with Ferrite Stone body gdep_same_body'
                )
                """
            )
            improved_id = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

            # Another citizen can independently encounter the same physical body.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'aris', 8104, 'field_observation', 'seed_site_local',
                    127.2, -42.9, 3, 1040, 'broken',
                    8.0, 'ferric', 'gdep_same_body', 'Ferrite Stone',
                    'Aris contacted Ferrite Stone body gdep_same_body'
                )
                """
            )

            # Explicit survey milestone without a deposit is allowed.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 8105, 'field_survey', 'seed_site_local',
                    600.2, 410.7, 20, 1050, 'ridge',
                    25.6, 'veyra', NULL, NULL,
                    'Field survey established a ridge observation'
                )
                """
            )
            conn.commit()

        sync_spatial_observations()

        noma = spatial_snapshot_for("noma")
        aris = spatial_snapshot_for("aris")

        # Noma keeps first deposit contact, improved scan, and explicit survey.
        assert len(noma) == 3
        same_body = [m for m in noma if m["metadata"].get("subject_id") == "gdep_same_body"]
        assert len(same_body) == 2
        assert {int(m["source_id"]) for m in same_body} == {first_id, improved_id}

        # Stable subject identity survives repeated encounters.
        assert all(m["metadata"]["subject_type"] == "generated_deposit" for m in same_body)
        assert all(m["metadata"]["subject_id"] == "gdep_same_body" for m in same_body)

        # Precision bounds coordinate detail instead of preserving hidden/excess
        # decimal precision.
        first = next(m for m in same_body if int(m["source_id"]) == first_id)
        improved = next(m for m in same_body if int(m["source_id"]) == improved_id)
        assert first["metadata"]["observed_x_m"] == 123.0
        assert first["metadata"]["observed_y_m"] == -46.0
        assert first["metadata"]["precision_radius_m"] == 5.0
        assert improved["metadata"]["observed_x_m"] == 124.3
        assert improved["metadata"]["observed_y_m"] == -44.8
        assert improved["metadata"]["precision_radius_m"] == 0.4

        # Hidden seeded-world fields are never copied into Memory metadata.
        for memory in noma + aris:
            metadata = memory["metadata"]
            assert "planet_seed" not in metadata
            assert "richness" not in metadata
            assert "center_x_m" not in metadata
            assert "center_y_m" not in metadata
            assert "long_axis_m" not in metadata
            assert "short_axis_m" not in metadata

        # Per-citizen isolation: Aris has only Aris's own encounter.
        assert len(aris) == 1
        assert aris[0]["metadata"]["subject_id"] == "gdep_same_body"

        # Repeated synchronization is idempotent.
        sync_spatial_observations()
        sync_spatial_observations()
        assert len(spatial_snapshot_for("noma")) == 3
        assert len(spatial_snapshot_for("aris")) == 1

        # Stable-subject and nearby retrieval both work.
        by_subject = spatial_snapshot_for("noma", subject_id="gdep_same_body")
        assert len(by_subject) == 2
        nearby = spatial_snapshot_for(
            "noma",
            center_x_m=124,
            center_y_m=-45,
            radius_m=10,
        )
        assert len(nearby) == 2

        context = spatial_context_for("noma", subject_id="gdep_same_body")
        assert "gdep_same_body" in context
        assert "planet_seed" not in context

        # Spatial evidence is its own stream, not generic v0.6 knowledge facts.
        assert all(
            item["source_type"] != "simulation_spatial_observation"
            for item in knowledge_snapshot_for("noma")
        )

        print("Agent City v0.8 Stage 1 spatial Memory smoke test passed.")


if __name__ == "__main__":
    main()
