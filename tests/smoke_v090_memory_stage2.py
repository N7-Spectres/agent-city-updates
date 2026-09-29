from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def add_column_if_missing(conn, table: str, column_def: str, name: str) -> None:
    names = {str(row["name"]) for row in conn.execute(f"PRAGMA table_info({table})")}
    if name not in names:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.causal_memory import display_recall_snapshot
        from agent_city.db import connect, init_db
        from agent_city.guided_practice_memory import (
            guided_practice_recall_context_for,
            guided_practice_recall_snapshot_for,
            sync_guided_practice_memory,
        )
        from agent_city.memory import ensure_memory_schema
        from agent_city.practice_memory import (
            practice_recall_snapshot_for,
            sync_practice_memory,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        with connect() as conn:
            add_column_if_missing(conn, "jobs", "competence_family TEXT", "competence_family")
            add_column_if_missing(conn, "jobs", "guidance_session_id INTEGER", "guidance_session_id")

            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS guided_practice_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER UNIQUE,
                    teacher_id TEXT NOT NULL,
                    learner_id TEXT NOT NULL,
                    activity_family TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    started_minute INTEGER NOT NULL,
                    completed_minute INTEGER,
                    source_conversation_id INTEGER,
                    teacher_practice_count INTEGER NOT NULL DEFAULT 0,
                    learner_practice_count INTEGER NOT NULL DEFAULT 0,
                    consumed_by_job_id INTEGER,
                    summary TEXT NOT NULL
                );
                """
            )

            conn.execute(
                """
                INSERT INTO jobs(
                    id, citizen_id, action, target, start_minute, end_minute,
                    status, outcome
                )
                VALUES (8101, 'bex', 'guided_practice', 'cato', 1000, 1020, 'complete', 'success')
                """
            )
            conn.execute(
                """
                INSERT INTO guided_practice_sessions(
                    id, job_id, teacher_id, learner_id, activity_family,
                    status, started_minute, completed_minute,
                    source_conversation_id, teacher_practice_count,
                    learner_practice_count, consumed_by_job_id, summary
                )
                VALUES (
                    1, 8101, 'bex', 'cato', 'extraction',
                    'complete', 1000, 1020,
                    501, 7, 1, NULL,
                    'Bex guided Cato through extraction practice.'
                )
                """
            )

            # Active sessions are not durable completed teaching/learning memories.
            conn.execute(
                """
                INSERT INTO guided_practice_sessions(
                    id, job_id, teacher_id, learner_id, activity_family,
                    status, started_minute, completed_minute,
                    source_conversation_id, teacher_practice_count,
                    learner_practice_count, consumed_by_job_id, summary
                )
                VALUES (
                    2, NULL, 'iri', 'noma', 'surveying',
                    'active', 1030, NULL,
                    NULL, 3, 1, NULL,
                    'Iri is guiding Noma through surveying practice.'
                )
                """
            )

            # Future-safe terminal failure semantics remain event history, not competence.
            conn.execute(
                """
                INSERT INTO jobs(
                    id, citizen_id, action, target, start_minute, end_minute,
                    status, outcome
                )
                VALUES (8102, 'bex', 'guided_practice', 'cato', 1040, 1060, 'failed', 'failed')
                """
            )
            conn.execute(
                """
                INSERT INTO guided_practice_sessions(
                    id, job_id, teacher_id, learner_id, activity_family,
                    status, started_minute, completed_minute,
                    source_conversation_id, teacher_practice_count,
                    learner_practice_count, consumed_by_job_id, summary
                )
                VALUES (
                    3, 8102, 'bex', 'cato', 'construction',
                    'failed', 1040, 1060,
                    NULL, 4, 1, NULL,
                    'Bex and Cato attempted guided construction practice.'
                )
                """
            )
            conn.commit()

        sync_guided_practice_memory()

        with connect() as conn:
            guided = conn.execute(
                """
                SELECT id, owner_id, event_kind, counterparty_id,
                       source_id, source_role, metadata_json
                FROM memory_events
                WHERE source_type = 'simulation_guided_practice_session'
                ORDER BY source_id, source_role
                """
            ).fetchall()
            assert len(guided) == 4

            complete = [row for row in guided if int(row["source_id"]) == 1]
            assert {row["owner_id"] for row in complete} == {"bex", "cato"}
            assert {row["source_role"] for row in complete} == {"teacher", "learner"}
            assert all(row["event_kind"] == "guided_practice_complete" for row in complete)

            cato_complete = next(row for row in complete if row["owner_id"] == "cato")
            assert cato_complete["counterparty_id"] == "bex"
            metadata = json.loads(cato_complete["metadata_json"])
            assert metadata["guided_role"] == "learner"
            assert metadata["activity_family"] == "extraction"
            assert "teacher_practice_count" not in metadata
            assert "learner_practice_count" not in metadata
            assert "weighted_evidence" not in metadata
            assert "duration_multiplier" not in metadata

            # Guided-session memory is deliberately not learner practice evidence.
            practice_facet = conn.execute(
                """
                SELECT 1
                FROM memory_event_facets
                WHERE memory_event_id = ?
                  AND facet_kind = 'practice_event'
                """,
                (int(cato_complete["id"]),),
            ).fetchone()
            assert practice_facet is None

            # Active session #2 created no durable guided memory.
            assert conn.execute(
                """
                SELECT 1 FROM memory_events
                WHERE source_type = 'simulation_guided_practice_session'
                  AND source_id = 2
                """
            ).fetchone() is None

        learner_recall = guided_practice_recall_snapshot_for(
            "cato",
            family="extraction",
            role="learner",
            limit=4,
        )
        assert len(learner_recall) == 1
        assert learner_recall[0]["source_id"] == 1
        assert learner_recall[0]["counterparty_id"] == "bex"
        assert "recall_score" not in learner_recall[0]
        assert "reinforcement_count" not in learner_recall[0]

        teacher_recall = guided_practice_recall_snapshot_for(
            "bex",
            family="extraction",
            counterpart_id="cato",
            role="teacher",
            limit=4,
        )
        assert len(teacher_recall) == 1
        assert teacher_recall[0]["source_id"] == 1

        # Another citizen cannot infer or inherit Bex/Cato's teaching event.
        assert guided_practice_recall_snapshot_for(
            "noma",
            family="extraction",
            limit=4,
        ) == []

        context = guided_practice_recall_context_for(
            "cato",
            family="extraction",
            counterpart_id="bex",
            role="learner",
        )
        assert "simulation_guided_practice_session #1" in context
        assert "Completed guided extraction practice with Bex as the learner." in context
        assert "practice_count" not in context
        assert "weighted_evidence" not in context

        # The learner later performs a real matching physical task.
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(
                    id, citizen_id, action, target, material,
                    start_minute, end_minute, status, outcome,
                    competence_family, guidance_session_id
                )
                VALUES (
                    8200, 'cato', 'extract', 'dep_silicate', 'Silicate Rock',
                    1100, 1140, 'complete', 'success',
                    'extraction', 1
                )
                """
            )
            conn.execute(
                """
                INSERT INTO practice_events(
                    id, citizen_id, job_id, plan_id, activity_type,
                    job_status, outcome, completed_minute, location_id,
                    target, material, project_id, observation_id,
                    shared_activity_id, summary
                )
                VALUES (
                    20, 'cato', 8200, NULL, 'extract',
                    'complete', 'success', 1140, 'rocky_basin',
                    'dep_silicate', 'Silicate Rock', NULL, NULL, NULL,
                    'Completed extract job #8200 with outcome success.'
                )
                """
            )
            conn.execute(
                "UPDATE guided_practice_sessions SET consumed_by_job_id = 8200 WHERE id = 1"
            )
            conn.commit()

        sync_practice_memory()
        sync_guided_practice_memory()

        family_practice = practice_recall_snapshot_for(
            "cato",
            family="extraction",
            limit=4,
        )
        assert len(family_practice) == 1
        assert family_practice[0]["event_kind"] == "practice_extract"
        assert family_practice[0]["source_type"] == "simulation_practice_event"
        assert all(
            any(f["kind"] == "practice_event" for f in item["facets"])
            for item in family_practice
        )
        assert any(
            f["kind"] == "competence_family" and f["value"] == "extraction"
            for f in family_practice[0]["facets"]
        )
        assert any(
            f["kind"] == "guided_practice_session" and f["value"] == "1"
            for f in family_practice[0]["facets"]
        )

        with connect() as conn:
            cato_guided_id = int(cato_complete["id"])
            applied = conn.execute(
                """
                SELECT facet_value
                FROM memory_event_facets
                WHERE owner_id = 'cato'
                  AND memory_event_id = ?
                  AND facet_kind = 'applied_job'
                """,
                (cato_guided_id,),
            ).fetchone()
            assert applied is not None
            assert applied["facet_value"] == "8200"

            # The teaching session's physical job still never became practice.
            assert conn.execute(
                "SELECT 1 FROM practice_events WHERE job_id = 8101"
            ).fetchone() is None

        # Citizen-facing continuity projection refreshes guided/practice memories
        # without exposing internal recall math.
        display = display_recall_snapshot("cato", limit=12)
        assert any(item["source_type"] == "simulation_guided_practice_session" for item in display)
        assert any(item["source_type"] == "simulation_practice_event" for item in display)
        assert all("recall_score" not in item for item in display)
        assert all("reinforcement_count" not in item for item in display)

        # Repeated sync is idempotent.
        sync_guided_practice_memory()
        sync_practice_memory()
        with connect() as conn:
            count = int(conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_events
                WHERE source_type = 'simulation_guided_practice_session'
                """
            ).fetchone()["n"])
            assert count == 4

        print("Agent City v0.9 Stage 2 guided-practice Memory smoke passed.")


if __name__ == "__main__":
    main()
