from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


CONTEXT_KEY = "location:seed_site|phase:active|open_choice"
PATTERN_KEY = f"habit:talk|{CONTEXT_KEY}"


def add_completed_talk_job(conn, job_id: int, citizen_id: str, target_id: str, minute: int):
    conn.execute(
        """
        INSERT INTO jobs(
            id, citizen_id, action, target,
            start_minute, end_minute, status, outcome, intent_reason
        )
        VALUES (?, ?, 'talk', ?, ?, ?, 'complete', 'success', ?)
        """,
        (
            job_id,
            citizen_id,
            target_id,
            minute - 20,
            minute,
            f"Chose to talk with {target_id} while several ordinary options were available.",
        ),
    )


def seed_talk_pattern(citizen_id: str, target_id: str, job_base: int):
    from agent_city.db import connect
    from agent_city.pattern_memory import record_voluntary_choice_evidence

    minutes = (600, 2040, 3480)
    with connect() as conn:
        for offset, minute in enumerate(minutes):
            add_completed_talk_job(
                conn,
                job_base + offset,
                citizen_id,
                target_id,
                minute,
            )
        conn.commit()

    for offset in range(3):
        evidence_id = record_voluntary_choice_evidence(
            citizen_id,
            job_base + offset,
            action_key="talk",
            context_key=CONTEXT_KEY,
            location_id="seed_site",
        )
        assert evidence_id is not None


def claim(speaker: str, text: str, pattern_key: str = PATTERN_KEY):
    return {
        "speaker": speaker,
        "subject_type": "social_pattern",
        "subject_id": None,
        "topic": "recurring_talk_pattern",
        "value": text,
        "pattern_key": pattern_key,
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.comms import _citizen_private_context, record_dialogue
        from agent_city.continuity_language import (
            pattern_continuity_context,
            transmittable_pattern_catalog,
        )
        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.pattern_memory import custom_candidates_for
        from agent_city.provenance import ensure_information_schema
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()

        # Cato and Noma each independently developed the same source-backed
        # recurring talk pattern. Bex has no such evidence yet.
        seed_talk_pattern("cato", "aris", 8100)
        seed_talk_pattern("noma", "vale", 8200)

        cato_catalog = transmittable_pattern_catalog("cato")
        noma_catalog = transmittable_pattern_catalog("noma")
        assert any(row["pattern_key"] == PATTERN_KEY for row in cato_catalog)
        assert any(row["pattern_key"] == PATTERN_KEY for row in noma_catalog)
        assert transmittable_pattern_catalog("bex") == []

        cato_context = pattern_continuity_context(
            "cato",
            location_id="seed_site",
        )
        assert "RECURRING HISTORY / PLACE CONTINUITY / SOCIAL PATTERN EVIDENCE" in cato_context
        assert "talk in location:seed_site|phase:active|open_choice" in cato_context
        assert "evidence trails, not personality traits, preferences" in cato_context
        assert "Do not automatically call it a tradition" in cato_context

        # First grounded transmission: real stored sentence, real face-to-face
        # conversation, exact catalog key. One report is not a custom.
        text1 = "I seem to keep choosing to talk when I have open options here."
        convo1 = record_dialogue(
            4 * 1440 + 600,
            "seed_site",
            "cato",
            "bex",
            text1,
            "I have noticed you doing that.",
            "Cato described a recurring personal talk pattern to Bex.",
            claims=[claim("initiator", text1)],
        )
        assert convo1 is not None
        assert custom_candidates_for("bex") == []

        with connect() as conn:
            rows = conn.execute(
                """
                SELECT mpe.*, me.event_kind, me.status
                FROM memory_pattern_evidence mpe
                JOIN memory_events me ON me.id = mpe.source_id
                WHERE mpe.owner_id='bex'
                  AND mpe.evidence_kind='social_transmission'
                  AND mpe.action_key=?
                """,
                (PATTERN_KEY,),
            ).fetchall()
            assert len(rows) == 1
            assert rows[0]["actor_id"] == "cato"
            assert rows[0]["transmission_mode"] == "heard"
            assert rows[0]["verification_state"] == "unverified"
            assert rows[0]["event_kind"] == "reported_social_pattern"
            assert rows[0]["status"] == "remembered"

        # An invented key is still allowed to exist as an ordinary unverified
        # claim receipt, but it must not become Stage 3 pattern evidence.
        bad_text = "I always polish the solar array at dawn."
        bad = record_dialogue(
            4 * 1440 + 900,
            "seed_site",
            "cato",
            "bex",
            bad_text,
            "I did not know that.",
            "Cato made a claim about a supposed routine.",
            claims=[claim("initiator", bad_text, "habit:polish_solar|invented_context")],
        )
        assert bad is not None
        with connect() as conn:
            bad_evidence = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_pattern_evidence
                WHERE owner_id='bex'
                  AND evidence_kind='social_transmission'
                  AND action_key='habit:polish_solar|invented_context'
                """
            ).fetchone()["n"]
            assert int(bad_evidence) == 0
            bad_receipts = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM information_receipts
                WHERE recipient_id='bex'
                  AND source_conversation_id=?
                  AND verification='unverified'
                """,
                (bad,),
            ).fetchone()["n"]
            assert int(bad_receipts) == 1

        # Second actor on a later day still does not meet the 3-source threshold.
        text2 = "I also seem to keep choosing to talk when I have open options here."
        convo2 = record_dialogue(
            5 * 1440 + 600,
            "seed_site",
            "noma",
            "bex",
            text2,
            "That sounds similar to what Cato told me.",
            "Noma described a similar recurring talk pattern to Bex.",
            claims=[claim("initiator", text2)],
        )
        assert convo2 is not None
        assert custom_candidates_for("bex") == []

        # Third source event, two distinct speakers, two days. Bex can now have
        # an owner-perspective social-pattern candidate. This is still not an
        # authoritative tradition.
        text3 = "That talk pattern keeps showing up for me when choices are open here."
        convo3 = record_dialogue(
            6 * 1440 + 600,
            "seed_site",
            "cato",
            "bex",
            text3,
            "Now I have heard this from more than one person.",
            "Cato again reported the recurring talk pattern to Bex.",
            claims=[claim("initiator", text3)],
        )
        assert convo3 is not None

        customs = custom_candidates_for("bex")
        social = next(row for row in customs if row["pattern_key"] == PATTERN_KEY)
        assert social["evidence_count"] == 3
        assert social["distinct_actors"] == ["cato", "noma"]
        assert social["transmission_modes"] == ["heard"]
        assert social["verification_states"] == ["unverified"]

        bex_context = pattern_continuity_context("bex", location_id="seed_site")
        assert PATTERN_KEY in bex_context
        assert "perspective-specific" in bex_context
        assert "Repeated unverified reports remain unverified" in bex_context
        assert "everyone does" in bex_context.lower()

        private = _citizen_private_context("bex", "cato")
        assert PATTERN_KEY in private
        assert "not personality traits, preferences, roles" in private

        # The transmission belongs only to the recipient. No global culture
        # object or automatic inheritance appears for another citizen.
        assert custom_candidates_for("aris") == []
        assert custom_candidates_for("vale") == []

        with connect() as conn:
            global_tables = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table'
                  AND name IN ('culture', 'traditions', 'global_reputation')
                """
            ).fetchall()
            assert global_tables == []

        print("Agent City v0.9 Stage 3 Communication pattern-transmission smoke passed.")


if __name__ == "__main__":
    main()
