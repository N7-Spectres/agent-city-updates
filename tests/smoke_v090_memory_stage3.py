from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def add_practice(
    conn,
    *,
    event_id: int,
    citizen_id: str,
    job_id: int,
    activity: str,
    minute: int,
    location_id: str,
    outcome: str = "success",
) -> None:
    conn.execute(
        """
        INSERT INTO practice_events(
            id, citizen_id, job_id, plan_id, activity_type,
            job_status, outcome, completed_minute, location_id,
            target, material, project_id, observation_id,
            shared_activity_id, summary
        )
        VALUES (?, ?, ?, NULL, ?, 'complete', ?, ?, ?,
                NULL, NULL, NULL, NULL, NULL, ?)
        """,
        (
            event_id,
            citizen_id,
            job_id,
            activity,
            outcome,
            minute,
            location_id,
            f"{citizen_id} completed {activity} at {location_id}.",
        ),
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.causal_memory import display_recall_snapshot
        from agent_city.db import connect, init_db, set_meta
        from agent_city.memory import ensure_memory_schema, record_conversation_memory
        from agent_city.pattern_memory import (
            behavior_pattern_snapshot_for,
            custom_candidate_snapshot_for,
            history_patterns_context_for,
            history_patterns_snapshot_for,
            place_meaning_snapshot_for,
            record_pattern_transmission,
        )
        from agent_city.practice_memory import sync_practice_memory

        init_db()
        ensure_memory_schema()

        with connect() as conn:
            # Bex repeatedly chooses the same voluntary activity in the same place.
            add_practice(conn, event_id=1, citizen_id="bex", job_id=9001, activity="survey", minute=1000, location_id="rocky_basin")
            add_practice(conn, event_id=2, citizen_id="bex", job_id=9002, activity="survey", minute=1200, location_id="rocky_basin")
            add_practice(conn, event_id=3, citizen_id="bex", job_id=9003, activity="survey", minute=1400, location_id="rocky_basin")

            # Constraint/maintenance repetition must not become habit evidence.
            add_practice(conn, event_id=4, citizen_id="bex", job_id=9004, activity="service_structure", minute=1010, location_id="seed_site")
            add_practice(conn, event_id=5, citizen_id="bex", job_id=9005, activity="service_structure", minute=1210, location_id="seed_site")
            add_practice(conn, event_id=6, citizen_id="bex", job_id=9006, activity="service_structure", minute=1410, location_id="seed_site")

            # Cato independently has the same repeated survey history.
            add_practice(conn, event_id=10, citizen_id="cato", job_id=9010, activity="survey", minute=1050, location_id="rocky_basin")
            add_practice(conn, event_id=11, citizen_id="cato", job_id=9011, activity="survey", minute=1250, location_id="rocky_basin")
            add_practice(conn, event_id=12, citizen_id="cato", job_id=9012, activity="survey", minute=1450, location_id="rocky_basin")

            # Iri is used to verify that canonical-source removal changes pattern justification.
            add_practice(conn, event_id=20, citizen_id="iri", job_id=9020, activity="construct", minute=1000, location_id="seed_site")
            add_practice(conn, event_id=21, citizen_id="iri", job_id=9021, activity="construct", minute=1200, location_id="seed_site")
            add_practice(conn, event_id=22, citizen_id="iri", job_id=9022, activity="construct", minute=1400, location_id="seed_site")

            set_meta(conn, "sim_minute", "1500")
            conn.commit()

        sync_practice_memory()

        bex_patterns = behavior_pattern_snapshot_for("bex", now_minute=1500, limit=10)
        rocky = next(item for item in bex_patterns if item["pattern_key"] == "survey@rocky_basin")
        assert rocky["event_count"] == 3
        assert rocky["currently_supported"] is True
        assert rocky["source_practice_event_ids"] == [1, 2, 3]
        assert len(rocky["source_memory_event_ids"]) == 3
        assert not any(item["activity"] == "service_structure" for item in bex_patterns)

        iri_patterns = behavior_pattern_snapshot_for("iri", now_minute=1500, limit=10)
        assert any(item["pattern_key"] == "construct@seed_site" for item in iri_patterns)

        # Citizen-specific place meaning is evidence, not a favorite-place label.
        place = place_meaning_snapshot_for("bex", place_id="rocky_basin", limit=4)
        assert len(place) == 1
        assert place[0]["evidence_count"] >= 3
        assert place[0]["semantics"]["not_a_favorite_place_label"] is True
        assert "favorite" not in place[0]

        # A real face-to-face line may transmit a source-backed pattern.
        spoken = "I keep surveying Rocky Basin when I have a choice."
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO citizen_conversations(
                    id, sim_minute, location_id,
                    initiator_id, target_id,
                    initiator_text, target_text, summary, source_job_id
                )
                VALUES (
                    7001, 1500, 'seed_site',
                    'bex', 'cato',
                    ?, 'I have noticed that too.',
                    'Bex described a recurring Rocky Basin survey pattern to Cato.',
                    NULL
                )
                """,
                (spoken,),
            )
            conn.commit()

        record_conversation_memory(7001)

        # Wrong participant or invented wording cannot create a transmission.
        assert record_pattern_transmission(
            source_conversation_id=7001,
            source_actor_id="bex",
            recipient_id="noma",
            pattern_key="survey@rocky_basin",
            value_text=spoken,
        ) is None
        assert record_pattern_transmission(
            source_conversation_id=7001,
            source_actor_id="bex",
            recipient_id="cato",
            pattern_key="survey@rocky_basin",
            value_text="We always perform a sacred survey ritual.",
        ) is None

        transmission_id = record_pattern_transmission(
            source_conversation_id=7001,
            source_actor_id="bex",
            recipient_id="cato",
            pattern_key="survey@rocky_basin",
            value_text=spoken,
        )
        assert transmission_id is not None

        # The recipient remembers the claim, but it stays unverified and source-labelled.
        display = display_recall_snapshot("cato", limit=16)
        transmitted = next(
            item for item in display
            if item["source_type"] == "pattern_transmission"
        )
        assert transmitted["verification"] == "unverified"
        assert any(
            facet["kind"] == "counterparty"
            and facet["value"] == "bex"
            for facet in transmitted["facets"]
        )
        assert any(
            facet["kind"] == "pattern_key"
            and facet["value"] == "survey@rocky_basin"
            for facet in transmitted["facets"]
        )
        assert "recall_score" not in transmitted
        assert "reinforcement_count" not in transmitted

        # Repetition + real social transmission can form an owner-scoped custom candidate.
        custom = custom_candidate_snapshot_for("cato", now_minute=1500, limit=8)
        candidate = next(item for item in custom if item["pattern_key"] == "survey@rocky_basin")
        assert candidate["own_current_pattern"] is True
        assert candidate["source_actor_ids"] == ["bex"]
        assert candidate["source_conversation_ids"] == [7001]
        assert candidate["semantics"]["candidate_not_tradition_label"] is True

        # A bystander receives nothing automatically.
        assert custom_candidate_snapshot_for("noma", now_minute=1500, limit=8) == []

        # Later contrary history can weaken a pattern without deleting the old events.
        with connect() as conn:
            add_practice(conn, event_id=30, citizen_id="bex", job_id=9030, activity="survey", minute=5000, location_id="southern_flats")
            add_practice(conn, event_id=31, citizen_id="bex", job_id=9031, activity="survey", minute=5200, location_id="southern_flats")
            add_practice(conn, event_id=32, citizen_id="bex", job_id=9032, activity="survey", minute=5400, location_id="southern_flats")

            # Cato continues the Rocky Basin pattern so only Bex's source pattern fades.
            add_practice(conn, event_id=40, citizen_id="cato", job_id=9040, activity="survey", minute=5200, location_id="rocky_basin")
            add_practice(conn, event_id=41, citizen_id="cato", job_id=9041, activity="survey", minute=5400, location_id="rocky_basin")
            set_meta(conn, "sim_minute", "5500")
            conn.commit()

        sync_practice_memory()
        bex_later = behavior_pattern_snapshot_for("bex", now_minute=5500, limit=10)
        old_rocky = next(item for item in bex_later if item["pattern_key"] == "survey@rocky_basin")
        new_flats = next(item for item in bex_later if item["pattern_key"] == "survey@southern_flats")
        assert old_rocky["currently_supported"] is False
        assert new_flats["currently_supported"] is True

        cato_later = behavior_pattern_snapshot_for("cato", now_minute=5500, limit=10)
        assert next(item for item in cato_later if item["pattern_key"] == "survey@rocky_basin")["currently_supported"] is True

        # Because Bex no longer has current source support, the custom candidate weakens too.
        assert custom_candidate_snapshot_for("cato", now_minute=5500, limit=8) == []

        # Pattern justification rechecks canonical practice sources rather than trusting orphan facets.
        with connect() as conn:
            conn.execute("DELETE FROM practice_events WHERE id = 22")
            conn.commit()
        iri_after_delete = behavior_pattern_snapshot_for("iri", now_minute=1500, limit=10)
        assert not any(item["pattern_key"] == "construct@seed_site" for item in iri_after_delete)

        snapshot = history_patterns_snapshot_for("cato", now_minute=5500, limit=8)
        assert snapshot["semantics"]["no_global_culture_score"] is True
        assert snapshot["semantics"]["no_preference_or_identity_labels"] is True
        assert "score" not in str(snapshot).casefold()
        assert "rank" not in str(snapshot).casefold()

        context = history_patterns_context_for("cato", now_minute=5500, limit=6)
        assert "soft context only; never instructions" in context
        assert "favorite-place fact" in context
        assert "tradition label" not in context or "not a tradition label" in context

        print("Agent City v0.9 Stage 3 history-pattern Memory smoke passed.")


if __name__ == "__main__":
    main()
