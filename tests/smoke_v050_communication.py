from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def active_job_id(citizen_id: str) -> int:
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute(
            "SELECT active_job_id FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
        assert row and row["active_job_id"] is not None
        return int(row["active_job_id"])


def job_row(job_id: int):
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        assert row
        return dict(row)


def conversation_rows_for_job(job_id: int) -> list[dict]:
    from agent_city.db import connect

    with connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM citizen_conversations WHERE source_job_id = ? ORDER BY id",
                (job_id,),
            ).fetchall()
        ]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.comms import record_dialogue
        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import ensure_memory_schema, relationship_snapshot
        from agent_city.simulation import complete_due_jobs, start_action

        init_db()
        ensure_memory_schema()

        # A real physical talk job is the source event for one durable exchange.
        ok, _ = start_action(
            "bex",
            {
                "action": "talk",
                "target": "aris",
                "reason": "Ask what Aris has directly observed nearby.",
            },
        )
        assert ok
        talk_job_id = active_job_id("bex")
        assert active_job_id("aris") == talk_job_id

        conversation_id = record_dialogue(
            9999,  # source-linked records use the authoritative talk start minute instead.
            "wrong_location_is_ignored",
            "bex",
            "aris",
            "What have you directly observed nearby?",
            "Only what I can see here at Seed Site so far.",
            "Bex asked Aris what Aris had directly observed; Aris reported only local observation.",
            source_job_id=talk_job_id,
        )
        assert conversation_id is not None

        rows = conversation_rows_for_job(talk_job_id)
        assert len(rows) == 1
        row = rows[0]
        job = job_row(talk_job_id)
        assert row["id"] == conversation_id
        assert row["sim_minute"] == job["start_minute"]
        assert row["location_id"] == "seed_site"
        assert row["initiator_id"] == "bex"
        assert row["target_id"] == "aris"
        assert row["initiator_text"] == "What have you directly observed nearby?"
        assert row["target_text"] == "Only what I can see here at Seed Site so far."
        assert "directly observed" in row["summary"]

        # Retrying persistence for the same physical talk is idempotent.
        same_id = record_dialogue(
            9999,
            "seed_site",
            "bex",
            "aris",
            "duplicate retry should not replace original text",
            "duplicate retry should not replace original text",
            "duplicate retry should not create a second conversation",
            source_job_id=talk_job_id,
        )
        assert same_id == conversation_id
        assert len(conversation_rows_for_job(talk_job_id)) == 1

        # Completing a source-linked talk succeeds and releases both citizens.
        complete_due_jobs(int(job["end_minute"]))
        assert job_row(talk_job_id)["status"] == "complete"
        with connect() as conn:
            bex = conn.execute("SELECT active_job_id FROM citizens WHERE id = 'bex'").fetchone()
            aris = conn.execute("SELECT active_job_id FROM citizens WHERE id = 'aris'").fetchone()
            assert bex["active_job_id"] is None
            assert aris["active_job_id"] is None

        # The public state shape exposes stable source identity for History/UI.
        state = snapshot()
        exposed = next(c for c in state["citizen_conversations"] if c["id"] == conversation_id)
        assert exposed["source_type"] == "citizen_conversation"
        assert exposed["source_id"] == conversation_id
        assert exposed["transfer_event_id"] == conversation_id
        assert exposed["source_job_id"] == talk_job_id
        assert exposed["summary"] == row["summary"]

        # The derived relationship memory remains tied to the one stored exchange.
        bex_rel = relationship_snapshot("bex")
        assert bex_rel and bex_rel[0]["other_id"] == "aris"
        assert bex_rel[0]["conversation_count"] == 1

        # A physical talk job with no successfully persisted exchange must fail,
        # not create a false transfer record or a "finished talking" success.
        ok, _ = start_action(
            "cato",
            {
                "action": "talk",
                "target": "iri",
                "reason": "Test failure integrity.",
            },
        )
        assert ok
        failed_job_id = active_job_id("cato")
        failed_job = job_row(failed_job_id)
        complete_due_jobs(int(failed_job["end_minute"]))

        assert job_row(failed_job_id)["status"] == "failed"
        assert conversation_rows_for_job(failed_job_id) == []

        # Once the physical talk has failed, stale generated text cannot be
        # committed later as if information had transferred.
        stale = record_dialogue(
            int(failed_job["start_minute"]),
            "seed_site",
            "cato",
            "iri",
            "This should never become a transfer.",
            "Nor should this.",
            "Stale generated dialogue must be rejected.",
            source_job_id=failed_job_id,
        )
        assert stale is None
        assert conversation_rows_for_job(failed_job_id) == []

        with connect() as conn:
            history = [
                row["message"]
                for row in conn.execute(
                    "SELECT message FROM history ORDER BY id"
                ).fetchall()
            ]
        assert any(f"conversation #{conversation_id}" in message for message in history)
        assert any(
            "conversation attempt" in message and "ended without a recorded exchange" in message
            for message in history
        )

        print("Agent City v0.5 communication integrity smoke test passed.")


if __name__ == "__main__":
    main()
