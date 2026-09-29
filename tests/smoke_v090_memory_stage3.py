from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def add_job(conn, job_id: int, citizen_id: str, action: str, minute: int, *, outcome: str = "success") -> None:
    conn.execute(
        """
        INSERT INTO jobs(
            id, citizen_id, action, target,
            start_minute, end_minute, status, outcome, intent_reason
        )
        VALUES (?, ?, ?, 'stage3-seed', ?, ?, 'complete', ?, ?)
        """,
        (
            job_id,
            citizen_id,
            action,
            minute - 10,
            minute,
            outcome,
            f"Chose {action} for a non-emergency Stage 3 continuity fixture.",
        ),
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.causal_memory import link_memory_event
        from agent_city.db import connect, init_db, set_meta
        from agent_city.memory import ensure_memory_schema, record_knowledge_event
        from agent_city.pattern_memory import (
            continuity_pattern_snapshot,
            custom_candidates_for,
            habit_candidates_for,
            place_continuity_for,
            record_social_pattern_evidence,
            record_voluntary_choice_evidence,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        with connect() as conn:
            set_meta(conn, "sim_minute", 12_000)

            # Three matching voluntary choices across multiple days.
            add_job(conn, 9001, "bex", "extract", 1_000)
            add_job(conn, 9002, "bex", "extract", 2_500)
            add_job(conn, 9003, "bex", "extract", 4_000)

            # Known forced/survival repetitions must never qualify.
            add_job(conn, 9010, "bex", "recharge", 4_100)
            add_job(conn, 9011, "bex", "service_chassis", 4_200)

            conn.commit()

        for job_id in (9001, 9002, 9003):
            evidence_id = record_voluntary_choice_evidence(
                "bex",
                job_id,
                action_key="extract",
                context_key="seed_site:open_choice",
                location_id="seed_site",
            )
            assert evidence_id is not None

        assert record_voluntary_choice_evidence(
            "bex",
            9010,
            action_key="recharge",
            context_key="seed_site:open_choice",
            location_id="seed_site",
        ) is None
        assert record_voluntary_choice_evidence(
            "bex",
            9011,
            action_key="service_chassis",
            context_key="seed_site:open_choice",
            location_id="seed_site",
        ) is None

        initial_habits = habit_candidates_for("bex", now_minute=12_000)
        extract = next(
            item for item in initial_habits
            if item["action_key"] == "extract"
            and item["context_key"] == "seed_site:open_choice"
        )
        assert extract["support_count"] == 3
        assert extract["distinct_days"] >= 2
        assert extract["state"] == "current"
        assert "score" not in extract
        assert "preference" not in extract

        # Later voluntary history diverges in the SAME context.
        with connect() as conn:
            for job_id, minute in (
                (9020, 5_000),
                (9021, 6_500),
                (9022, 8_000),
                (9023, 9_500),
            ):
                add_job(conn, job_id, "bex", "experiment", minute)
            conn.commit()

        for job_id in (9020, 9021, 9022, 9023):
            assert record_voluntary_choice_evidence(
                "bex",
                job_id,
                action_key="experiment",
                context_key="seed_site:open_choice",
                location_id="seed_site",
            ) is not None

        changed = habit_candidates_for("bex", now_minute=12_000)
        extract_after = next(item for item in changed if item["action_key"] == "extract")
        experiment_after = next(item for item in changed if item["action_key"] == "experiment")
        assert extract_after["state"] == "fading"
        assert experiment_after["state"] == "current"
        assert extract_after["recent_contrary_sources"]

        # Removing a canonical source removes part of the justification. With
        # only two extraction supports left, the old habit candidate disappears.
        with connect() as conn:
            conn.execute("DELETE FROM jobs WHERE id = 9001")
            conn.commit()
        after_delete = habit_candidates_for("bex", now_minute=12_000)
        assert not any(item["action_key"] == "extract" for item in after_delete)

        # Place meaning is personal experience continuity, not a favorite field.
        bex_place_1 = record_knowledge_event(
            "bex",
            sim_minute=3_000,
            event_kind="shared_experience",
            source_type="simulation_shared_activity",
            source_id=701,
            summary="Bex completed a meaningful shared inspection at Resin Grove.",
            metadata={"verification": "verified", "location_id": "resin_grove"},
            status="verified",
            importance=0.65,
        )
        bex_place_2 = record_knowledge_event(
            "bex",
            sim_minute=5_200,
            event_kind="practice_survey",
            source_type="simulation_practice_event",
            source_id=702,
            summary="Bex completed a careful survey at Resin Grove.",
            metadata={"verification": "verified", "location_id": "resin_grove"},
            status="verified",
            importance=0.60,
        )
        assert bex_place_1 is not None and bex_place_2 is not None
        assert link_memory_event(bex_place_1, "location", "resin_grove")
        assert link_memory_event(bex_place_2, "location", "resin_grove")

        cato_place = record_knowledge_event(
            "cato",
            sim_minute=5_300,
            event_kind="practice_survey",
            source_type="simulation_practice_event",
            source_id=703,
            summary="Cato completed one survey at Resin Grove.",
            metadata={"verification": "verified", "location_id": "resin_grove"},
            status="verified",
            importance=0.60,
        )
        assert cato_place is not None
        assert link_memory_event(cato_place, "location", "resin_grove")

        bex_places = place_continuity_for("bex", location_id="resin_grove")
        assert len(bex_places) == 1
        assert bex_places[0]["location_id"] == "resin_grove"
        assert bex_places[0]["evidence_count"] == 2
        assert len(bex_places[0]["event_kinds"]) == 2
        assert "favorite" not in bex_places[0]

        # Same physical place, different personal history.
        assert place_continuity_for("cato", location_id="resin_grove") == []

        # Social custom candidate requires legitimate owner-scoped transmission
        # from multiple actors over time.
        custom_memories = []
        for idx, (minute, actor, status) in enumerate(
            (
                (2_000, "cato", "verified"),
                (4_000, "noma", "remembered"),
                (6_000, "cato", "verified"),
            ),
            start=1,
        ):
            memory_id = record_knowledge_event(
                "bex",
                sim_minute=minute,
                event_kind="reported_custom_evidence",
                source_type="information_receipt",
                source_id=800 + idx,
                summary=f"Source-backed evidence involving {actor} and a shared greeting pattern.",
                metadata={
                    "verification": "verified" if status == "verified" else "unverified",
                },
                status=status,
                importance=0.50,
            )
            assert memory_id is not None
            custom_memories.append(memory_id)
            assert record_social_pattern_evidence(
                memory_id,
                pattern_key="greeting:tap-rail",
                actor_id=actor,
                transmission_mode="observed" if idx != 2 else "heard",
                context_key="seed_site:arrival",
            ) is not None

        customs = custom_candidates_for("bex")
        assert len(customs) == 1
        custom = customs[0]
        assert custom["pattern_key"] == "greeting:tap-rail"
        assert custom["distinct_actors"] == ["cato", "noma"]
        assert set(custom["transmission_modes"]) == {"heard", "observed"}
        assert set(custom["verification_states"]) == {"unverified", "verified"}
        assert "score" not in custom
        assert "culture" not in custom

        # One person's private repetition does NOT become a custom.
        private_ids = []
        for idx, minute in enumerate((2_100, 4_100, 6_100), start=1):
            memory_id = record_knowledge_event(
                "cato",
                sim_minute=minute,
                event_kind="private_repeat",
                source_type="information_receipt",
                source_id=900 + idx,
                summary="Repeated private action by one actor.",
                metadata={"verification": "verified"},
                status="verified",
                importance=0.40,
            )
            assert memory_id is not None
            private_ids.append(memory_id)
            assert record_social_pattern_evidence(
                memory_id,
                pattern_key="private:stone-stack",
                actor_id="cato",
                transmission_mode="participated",
                context_key="seed_site",
            ) is not None
        assert custom_candidates_for("cato") == []

        # Delete one source Memory event. The custom candidate must disappear
        # instead of surviving as a fabricated global tradition.
        with connect() as conn:
            conn.execute("DELETE FROM memory_events WHERE id = ?", (custom_memories[1],))
            conn.commit()
        assert custom_candidates_for("bex") == []

        payload = continuity_pattern_snapshot("bex", location_id="resin_grove")
        assert payload["citizen_id"] == "bex"
        assert payload["semantics"]["habit_candidates_not_identity"] is True
        assert payload["semantics"]["place_evidence_not_favorite"] is True
        assert payload["semantics"]["customs_are_owner_perspective"] is True
        assert payload["semantics"]["no_global_score"] is True
        assert not any(
            key in payload
            for key in ("habit_score", "culture_score", "preference_score", "favorite_place")
        )

        import main as app_module

        api_payload = app_module.get_continuity_patterns(
            "bex",
            location_id="resin_grove",
        )
        assert api_payload["citizen"]["id"] == "bex"
        assert api_payload["location"]["id"] == "resin_grove"
        assert api_payload["semantics"]["source_events_remain_authoritative"] is True

        print("Agent City v0.9 Stage 3 Memory pattern-evidence smoke passed.")


if __name__ == "__main__":
    main()
