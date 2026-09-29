from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.causal_memory import (
            causal_recall_context_for,
            causal_recall_snapshot,
            link_memory_event,
        )
        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema, record_knowledge_event
        from agent_city.practice_memory import sync_practice_memory

        init_db()
        ensure_memory_schema()

        now = 200_000

        # Old low-value event should remain durable but naturally lose active priority.
        old_low = record_knowledge_event(
            "bex",
            sim_minute=1_000,
            event_kind="minor_observation",
            source_type="job",
            source_id=7001,
            summary="Noted an ordinary patch of ground during routine travel.",
            metadata={"action": "observe", "location_id": "seed_site"},
            status="verified",
            importance=0.15,
        )
        assert old_low is not None

        # Repeated source-backed extraction experiences share causal facets.
        repeated_ids: list[int] = []
        for i, minute in enumerate((185_000, 188_000, 191_000, 194_000), start=1):
            memory_id = record_knowledge_event(
                "bex",
                sim_minute=minute,
                event_kind="work_outcome",
                source_type="job",
                source_id=7100 + i,
                summary=f"Completed ferrite extraction run {i}.",
                metadata={
                    "action": "extract",
                    "subject_type": "deposit",
                    "subject_id": "dep_ferrite",
                    "material": "Ferrite Stone",
                    "verification": "verified",
                },
                status="verified",
                importance=0.58,
            )
            assert memory_id is not None
            repeated_ids.append(memory_id)

        # Repeated claims stay claims even when their social/topic facet repeats.
        claim_ids: list[int] = []
        for i, minute in enumerate((192_000, 193_000, 194_500), start=1):
            memory_id = record_knowledge_event(
                "bex",
                sim_minute=minute,
                event_kind="reported_claim",
                source_type="information_receipt",
                source_id=7200 + i,
                summary="Cato said the western ridge may contain useful stone.",
                metadata={
                    "visitor": None,
                    "subject_type": "place",
                    "subject_id": "western_ridge",
                    "verification": "unverified",
                },
                status="remembered",
                importance=0.45,
            )
            assert memory_id is not None
            claim_ids.append(memory_id)

        # Old initiating reason for a future persistent plan.
        plan_reason = record_knowledge_event(
            "bex",
            sim_minute=20_000,
            event_kind="personal_experience",
            source_type="job",
            source_id=7301,
            summary="A Resin Grove survey was left incomplete after energy ran low.",
            metadata={
                "action": "survey",
                "location_id": "resin_grove",
                "verification": "verified",
            },
            status="verified",
            importance=0.42,
        )
        assert plan_reason is not None
        assert link_memory_event(plan_reason, "plan", "plan-resin-followup")

        # Another citizen has unrelated personal history only.
        cato_event = record_knowledge_event(
            "cato",
            sim_minute=198_000,
            event_kind="work_outcome",
            source_type="job",
            source_id=7401,
            summary="Completed a hauling run.",
            metadata={"action": "haul", "verification": "verified"},
            status="verified",
            importance=0.55,
        )
        assert cato_event is not None

        # Canonical Simulation practice evidence is retained without duplicating
        # an already remembered physical job.
        existing_job_memory = record_knowledge_event(
            "bex",
            sim_minute=196_000,
            event_kind="maintenance_service",
            source_type="job",
            source_id=7501,
            summary="Serviced field equipment after wear was noticed.",
            metadata={
                "action": "service_equipment",
                "job_id": 7501,
                "target_type": "equipment",
                "target_id": "12",
                "verification": "verified",
            },
            status="verified",
            importance=0.62,
        )
        assert existing_job_memory is not None

        with connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS practice_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    citizen_id TEXT NOT NULL,
                    job_id INTEGER NOT NULL UNIQUE,
                    plan_id INTEGER,
                    activity_type TEXT NOT NULL,
                    job_status TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    completed_minute INTEGER NOT NULL,
                    location_id TEXT,
                    target TEXT,
                    material TEXT,
                    project_id INTEGER,
                    observation_id INTEGER,
                    shared_activity_id INTEGER,
                    summary TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                INSERT INTO practice_events(
                    citizen_id, job_id, plan_id, activity_type,
                    job_status, outcome, completed_minute,
                    location_id, target, material, project_id,
                    observation_id, shared_activity_id, summary
                )
                VALUES (
                    'bex', 7501, NULL, 'service_equipment',
                    'complete', 'success', 196000,
                    'seed_site', '12', NULL, NULL,
                    NULL, NULL, 'Completed service_equipment job #7501 with outcome success.'
                )
                """
            )
            existing_practice_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )

            conn.execute(
                """
                INSERT INTO practice_events(
                    citizen_id, job_id, plan_id, activity_type,
                    job_status, outcome, completed_minute,
                    location_id, target, material, project_id,
                    observation_id, shared_activity_id, summary
                )
                VALUES (
                    'bex', 7601, 44, 'fabricate',
                    'complete', 'success', 197000,
                    'seed_site', 'field_pack', 'Processed structural material', NULL,
                    NULL, NULL, 'Completed fabricate job #7601 with outcome success.'
                )
                """
            )
            fabricate_practice_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )

            conn.execute(
                """
                INSERT INTO practice_events(
                    citizen_id, job_id, plan_id, activity_type,
                    job_status, outcome, completed_minute,
                    location_id, target, material, project_id,
                    observation_id, shared_activity_id, summary
                )
                VALUES (
                    'bex', 7602, 44, 'construct',
                    'failed', 'failed', 197500,
                    'seed_site', 'field_shelter', NULL, 91,
                    NULL, NULL, 'Ended construct job #7602 with outcome failed.'
                )
                """
            )
            construct_practice_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )
            conn.commit()

        sync_practice_memory()

        with connect() as conn:
            # Existing job memory was reused: no duplicate practice Memory row.
            dup = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_events
                WHERE owner_id = 'bex'
                  AND source_type = 'simulation_practice_event'
                  AND source_id = ?
                """,
                (existing_practice_id,),
            ).fetchone()
            assert int(dup["n"]) == 0

            linked = conn.execute(
                """
                SELECT facet_value
                FROM memory_event_facets
                WHERE owner_id = 'bex'
                  AND memory_event_id = ?
                  AND facet_kind = 'practice_event'
                """,
                (existing_job_memory,),
            ).fetchone()
            assert linked is not None
            assert linked["facet_value"] == str(existing_practice_id)

            new_rows = conn.execute(
                """
                SELECT source_id, event_kind, importance, metadata_json
                FROM memory_events
                WHERE owner_id = 'bex'
                  AND source_type = 'simulation_practice_event'
                ORDER BY source_id
                """
            ).fetchall()
            assert len(new_rows) == 2
            assert int(new_rows[0]["source_id"]) == fabricate_practice_id
            assert new_rows[0]["event_kind"] == "practice_fabricate"
            assert int(new_rows[1]["source_id"]) == construct_practice_id
            assert new_rows[1]["event_kind"] == "practice_construct"
            assert float(new_rows[1]["importance"]) > float(new_rows[0]["importance"])

        practice_recall = causal_recall_snapshot(
            "bex",
            now_minute=now,
            facet_filters={"plan": "44"},
            limit=4,
        )
        assert {item["event_kind"] for item in practice_recall} >= {
            "practice_fabricate",
            "practice_construct",
        }
        assert all(item["verification"] == "verified" for item in practice_recall)

        # Repeated sync remains idempotent.
        sync_practice_memory()
        with connect() as conn:
            count = int(conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_events
                WHERE owner_id = 'bex'
                  AND source_type = 'simulation_practice_event'
                """
            ).fetchone()["n"])
            assert count == 2

        # Reinforcement: repeated related practice is easy to retrieve without
        # copying an unbounded transcript into context.
        extraction = causal_recall_snapshot(
            "bex",
            now_minute=now,
            facet_filters={"activity": "extract"},
            limit=3,
        )
        assert len(extraction) == 3
        assert all(item["reinforcement_count"] >= 4 for item in extraction)
        assert all(item["verification"] == "verified" for item in extraction)
        assert all(item["source_type"] == "job" for item in extraction)

        # Aging: newer equal-family experiences outrank older ones.
        assert extraction[0]["sim_minute"] > extraction[-1]["sim_minute"]

        # Repetition does not upgrade truth status.
        claims = causal_recall_snapshot(
            "bex",
            now_minute=now,
            facet_filters={"subject": "place:western_ridge"},
            limit=3,
        )
        assert len(claims) == 3
        assert all(item["reinforcement_count"] >= 3 for item in claims)
        assert all(item["verification"] == "unverified" for item in claims)
        assert all(item["status"] == "remembered" for item in claims)

        # Persistent-plan continuity: an old initiating reason can be pinned and
        # remain in the active packet after lots of unrelated time passes.
        pinned = causal_recall_snapshot(
            "bex",
            now_minute=now,
            facet_filters={"activity": "extract"},
            pinned_event_ids=[plan_reason],
            limit=2,
        )
        assert pinned[0]["memory_event_id"] == plan_reason
        assert pinned[0]["pinned"] is True
        assert pinned[0]["age_minutes"] > 100_000
        assert any(f["kind"] == "plan" and f["value"] == "plan-resin-followup" for f in pinned[0]["facets"])

        context = causal_recall_context_for(
            "bex",
            now_minute=now,
            pinned_event_ids=[plan_reason],
            limit=2,
        )
        assert "pinned by unfinished continuity" in context
        assert "job #7301" in context
        assert len(context) <= 2400

        # Citizen-scoped ownership: Cato cannot inherit Bex's plan or practice.
        assert causal_recall_snapshot(
            "cato",
            now_minute=now,
            facet_filters={"plan": "plan-resin-followup"},
            limit=4,
        ) == []
        assert causal_recall_snapshot(
            "cato",
            now_minute=now,
            facet_filters={"subject": "deposit:dep_ferrite"},
            limit=4,
        ) == []

        # Active recall never rewrites the durable archive.
        with connect() as conn:
            row = conn.execute(
                """
                SELECT source_type, source_id, summary, status
                FROM memory_events
                WHERE id = ?
                """,
                (old_low,),
            ).fetchone()
            assert row is not None
            assert row["source_type"] == "job"
            assert int(row["source_id"]) == 7001
            assert row["summary"] == "Noted an ordinary patch of ground during routine travel."
            assert row["status"] == "verified"

            # The low-value old event still exists even if it is not in the top recall packet.
            total = int(conn.execute(
                "SELECT COUNT(*) AS n FROM memory_events WHERE owner_id = 'bex'"
            ).fetchone()["n"])
            assert total >= 9

        unfiltered = causal_recall_snapshot("bex", now_minute=now, limit=4)
        assert all(item["memory_event_id"] != old_low for item in unfiltered)

        print("Agent City v0.9 Stage 1 causal Memory smoke test passed.")


if __name__ == "__main__":
    main()
