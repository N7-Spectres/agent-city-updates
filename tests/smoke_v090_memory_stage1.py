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
