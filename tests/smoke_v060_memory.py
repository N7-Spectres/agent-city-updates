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
        from agent_city.memory import (
            ensure_memory_schema,
            knowledge_context_for,
            knowledge_snapshot_for,
            location_knowledge_snapshot,
            record_knowledge_event,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Create one authoritative personal survey discovery for Noma.
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(
                    citizen_id, action, target, material, amount,
                    start_minute, end_minute, status, detail, intent_reason,
                    project_id, outcome
                )
                VALUES (
                    'noma', 'survey', 'resin_grove', NULL, NULL,
                    500, 620, 'complete', 'survey:resin_grove',
                    'Inspect the grove directly.', NULL, 'success'
                )
                """
            )
            survey_job_id = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])
            conn.execute(
                """
                UPDATE deposits
                SET discovered = 1,
                    discoverer_id = 'noma',
                    discovered_minute = 620
                WHERE id = 'dep_resin'
                """
            )
            conn.commit()

        noma = knowledge_snapshot_for("noma", location_id="resin_grove")
        assert noma
        resin = next(
            fact for fact in noma
            if fact["metadata"].get("subject_id") == "dep_resin"
        )
        assert resin["verification"] == "verified"
        assert resin["source_type"] == "job"
        assert int(resin["source_id"]) == survey_job_id
        assert resin["metadata"]["material"] == "Native Resin"
        assert resin["metadata"]["channel"] == "personal_experience"

        # Knowledge remains per-citizen. Vale must not inherit Noma's discovery.
        vale = knowledge_snapshot_for("vale", location_id="resin_grove")
        assert vale == []

        # Repeated retrieval/backfill is idempotent.
        again = knowledge_snapshot_for("noma", location_id="resin_grove")
        assert len(again) == len(noma)
        with connect() as conn:
            count = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_events
                WHERE owner_id = 'noma'
                  AND event_kind = 'location_discovery'
                  AND source_type = 'job'
                  AND source_id = ?
                """,
                (survey_job_id,),
            ).fetchone()["n"]
            assert int(count) == 1

        # A communicated claim can be retained without becoming verified truth.
        claim_id = record_knowledge_event(
            "vale",
            sim_minute=700,
            event_kind="location_claim",
            source_type="citizen_conversation",
            source_id=77,
            source_role="listener",
            summary="Noma said Native Resin can be found at Resin Grove.",
            status="remembered",
            metadata={
                "verification": "unverified",
                "channel": "face_to_face_claim",
                "source_actor_id": "noma",
                "location_id": "resin_grove",
                "material": "Native Resin",
            },
        )
        assert claim_id is not None

        vale_claims = knowledge_snapshot_for(
            "vale",
            location_id="resin_grove",
            material="Native Resin",
        )
        assert len(vale_claims) == 1
        assert vale_claims[0]["verification"] == "unverified"
        assert vale_claims[0]["source_type"] == "citizen_conversation"

        context = knowledge_context_for("vale", location_id="resin_grove")
        assert "Unverified" in context
        assert "Verified" not in context

        # Location UI model partitions knowledge by citizen instead of unioning it.
        notebook = location_knowledge_snapshot("resin_grove")
        by_id = {entry["citizen_id"]: entry for entry in notebook["citizens"]}
        assert by_id["noma"]["facts"]
        assert by_id["vale"]["facts"]
        assert by_id["aris"]["facts"] == []
        assert notebook["location"]["id"] == "resin_grove"

        # API module imports with the new knowledge endpoints.
        import main as app_module
        citizen_payload = app_module.get_citizen_knowledge(
            "noma",
            location_id="resin_grove",
        )
        assert citizen_payload["facts"]

        location_payload = app_module.get_location_knowledge(
            "resin_grove",
            citizen_id="noma",
        )
        assert len(location_payload["citizens"]) == 1
        assert location_payload["citizens"][0]["citizen_id"] == "noma"

        print("Agent City v0.6 Memory knowledge smoke test passed.")


if __name__ == "__main__":
    main()
