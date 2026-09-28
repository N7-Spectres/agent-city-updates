from __future__ import annotations

import inspect
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from fastapi import HTTPException

        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import ensure_memory_schema, knowledge_snapshot_for
        from agent_city.exploration_memory import (
            shared_exploration_context_for,
            shared_exploration_snapshot_for,
            sync_shared_exploration,
        )
        from agent_city.planner import citizen_context
        from agent_city.spatial_memory import (
            MAX_SPATIAL_CONTEXT_CHARS,
            nearby_spatial_context_for,
            spatial_snapshot_for,
            sync_spatial_observations,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        with connect() as conn:
            conn.execute(
                "UPDATE citizens SET position_x_m = 110, position_y_m = 55 WHERE id = 'noma'"
            )
            conn.execute(
                "UPDATE citizens SET position_x_m = 110, position_y_m = 55 WHERE id = 'aris'"
            )

            # First meaningful encounter.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 9001, 'field_observation', 'seed_site_local',
                    100.4, 50.2, 5, 1200, 'broken',
                    8.1, 'ferric', 'gdep_return', 'Ferrite Stone',
                    'Contact with Ferrite Stone body gdep_return'
                )
                """
            )

            # Many repeated observations of the same body/method/precision must
            # not turn planning context into a movement/scan diary.
            for i in range(15):
                conn.execute(
                    """
                    INSERT INTO spatial_observations(
                        observer_id, source_job_id, observation_kind, frame_id,
                        x_m, y_m, radius_m, observed_minute, terrain_class,
                        elevation_m, geology_class, deposit_id, material, summary
                    )
                    VALUES (
                        'noma', ?, 'field_observation', 'seed_site_local',
                        ?, ?, 5, ?, 'broken',
                        8.1, 'ferric', 'gdep_return', 'Ferrite Stone',
                        'Repeated contact with Ferrite Stone body gdep_return'
                    )
                    """,
                    (9100 + i, 101.0 + i * 0.1, 50.5, 1210 + i),
                )

            # A materially improved scan should survive as another meaningful
            # observation of the SAME stable subject.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 9200, 'instrument_scan', 'seed_site_local',
                    102.34, 50.84, 0.5, 1300, 'broken',
                    8.1, 'ferric', 'gdep_return', 'Ferrite Stone',
                    'Instrument scan refined contact with Ferrite Stone body gdep_return'
                )
                """
            )
            improved_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )

            # Salient but distant personal observation should not enter nearby
            # context around Noma's current position.
            conn.execute(
                """
                INSERT INTO spatial_observations(
                    observer_id, source_job_id, observation_kind, frame_id,
                    x_m, y_m, radius_m, observed_minute, terrain_class,
                    elevation_m, geology_class, deposit_id, material, summary
                )
                VALUES (
                    'noma', 9300, 'field_observation', 'seed_site_local',
                    1400, 800, 4, 1400, 'ridge',
                    20.0, 'veyra', 'gdep_far', 'Veyra Ore',
                    'Contact with Veyra Ore body gdep_far'
                )
                """
            )
            # Simulation Stage 2 shared-activity ledger shape.
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS shared_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visitor TEXT NOT NULL,
                    citizen_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    frame_id TEXT NOT NULL,
                    start_x_m REAL NOT NULL,
                    start_y_m REAL NOT NULL,
                    target_x_m REAL NOT NULL,
                    target_y_m REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'proposed',
                    proposed_minute INTEGER NOT NULL,
                    accepted_minute INTEGER,
                    started_minute INTEGER,
                    completed_minute INTEGER,
                    source_visit_id INTEGER,
                    source_exchange_id INTEGER,
                    tool_equipment_id INTEGER,
                    citizen_job_id INTEGER,
                    observation_id INTEGER,
                    outcome TEXT,
                    failure_reason TEXT
                );
                """
            )

            # Proposal only: must NOT become a physical shared-exploration memory.
            conn.execute(
                """
                INSERT INTO shared_activities(
                    visitor, citizen_id, activity_type, objective, frame_id,
                    start_x_m, start_y_m, target_x_m, target_y_m,
                    status, proposed_minute, source_visit_id, source_exchange_id
                )
                VALUES (
                    'N7', 'noma', 'walk_inspect', 'Maybe inspect the ridge together',
                    'seed_site_local', 110, 55, 130, 70,
                    'proposed', 1450, 21, 301
                )
                """
            )

            # Active but unfinished: also must NOT become completed memory.
            conn.execute(
                """
                INSERT INTO shared_activities(
                    visitor, citizen_id, activity_type, objective, frame_id,
                    start_x_m, start_y_m, target_x_m, target_y_m,
                    status, proposed_minute, accepted_minute, started_minute,
                    source_visit_id, source_exchange_id, citizen_job_id
                )
                VALUES (
                    'N7', 'noma', 'walk_inspect', 'Walk to the ferrite contact',
                    'seed_site_local', 110, 55, 120, 60,
                    'active', 1460, 1462, 1462, 21, 302, 9400
                )
                """
            )

            # Physically completed Simulation-owned activity with a real linked
            # observation. This one is eligible for durable shared continuity.
            conn.execute(
                """
                INSERT INTO shared_activities(
                    visitor, citizen_id, activity_type, objective, frame_id,
                    start_x_m, start_y_m, target_x_m, target_y_m,
                    status, proposed_minute, accepted_minute, started_minute,
                    completed_minute, source_visit_id, source_exchange_id,
                    citizen_job_id, observation_id, outcome
                )
                VALUES (
                    'N7', 'noma', 'walk_inspect', 'Return to the ferrite contact together',
                    'seed_site_local', 110, 55, 102, 51,
                    'complete', 1470, 1471, 1471, 1490,
                    21, 303, 9500, ?, 'success'
                )
                """,
                (improved_id,),
            )
            conn.commit()

        sync_spatial_observations()
        sync_shared_exploration()

        same_body = spatial_snapshot_for("noma", subject_id="gdep_return")
        assert len(same_body) == 2
        assert all(m["metadata"]["subject_id"] == "gdep_return" for m in same_body)

        nearby = nearby_spatial_context_for(
            "noma",
            x_m=110,
            y_m=55,
            radius_m=250,
            limit=4,
        )
        assert "gdep_return" in nearby
        assert "gdep_far" not in nearby
        assert "±5" in nearby or "±0.5" in nearby
        assert len(nearby) <= MAX_SPATIAL_CONTEXT_CHARS

        # Same physical coordinates do not imply shared memory.
        aris_nearby = nearby_spatial_context_for(
            "aris",
            x_m=110,
            y_m=55,
            radius_m=250,
            limit=4,
        )
        assert "gdep_return" not in aris_nearby

        state = snapshot()
        noma = next(c for c in state["citizens"] if c["id"] == "noma")
        aris = next(c for c in state["citizens"] if c["id"] == "aris")

        actions = [{"action": "wait", "target": None, "material": None, "label": "Observe surroundings."}]
        noma_prompt = citizen_context(noma, state, actions)
        aris_prompt = citizen_context(aris, state, actions)

        assert "RETAINED PERSONAL EXPLORATION MEMORY NEAR YOUR CURRENT POSITION:" in noma_prompt
        assert "gdep_return" in noma_prompt
        assert "historical personal evidence" in noma_prompt
        assert "observation radius" in noma_prompt
        assert "gdep_return" not in aris_prompt

        import main as app_module

        payload = app_module.get_spatial_memory(
            "noma",
            subject_id="gdep_return",
            center_x_m=110,
            center_y_m=55,
            radius_m=250,
            limit=10,
        )
        assert payload["citizen"]["id"] == "noma"
        assert len(payload["events"]) == 2
        assert "gdep_return" in payload["summary"]

        try:
            app_module.get_spatial_memory("noma", center_x_m=110)
        except HTTPException as exc:
            assert exc.status_code == 400
        else:
            raise AssertionError("Partial center coordinate should be rejected")

        # Visitor dialogue is wired to retained exploration memory while current
        # authoritative grounding remains a separate Communication-owned layer.
        talk_src = inspect.getsource(app_module.talk)
        assert "retained_exploration_memory = nearby_spatial_context_for" in talk_src
        assert "RETAINED PERSONAL EXPLORATION MEMORY NEAR YOUR CURRENT POSITION" in talk_src
        assert "spatial_context = spatial_grounding_context" in talk_src

        print("Agent City v0.8 Stage 2 exploration Memory smoke test passed.")


if __name__ == "__main__":
    main()
