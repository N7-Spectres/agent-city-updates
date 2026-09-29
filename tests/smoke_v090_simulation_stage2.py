from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def set_time(conn, minute: int) -> None:
    from agent_city.db import set_meta
    set_meta(conn, "sim_minute", minute)
    conn.commit()


def seed_practice(
    conn,
    citizen_id: str,
    action: str,
    *,
    count: int,
    start_minute: int,
    status: str = "complete",
    outcome: str = "success",
) -> list[int]:
    ids: list[int] = []
    for i in range(count):
        minute = start_minute + i * 10
        cur = conn.execute(
            """
            INSERT INTO jobs(
                citizen_id, action, target, start_minute, end_minute,
                status, outcome
            )
            VALUES (?, ?, 'practice-seed', ?, ?, ?, ?)
            """,
            (citizen_id, action, minute, minute + 5, status, outcome),
        )
        job_id = int(cur.lastrowid)
        cur = conn.execute(
            """
            INSERT INTO practice_events(
                citizen_id, job_id, plan_id, activity_type, job_status, outcome,
                completed_minute, location_id, target, summary
            )
            VALUES (?, ?, NULL, ?, ?, ?, ?, 'seed_site', 'practice-seed', ?)
            """,
            (
                citizen_id,
                job_id,
                action,
                status,
                outcome,
                minute + 5,
                f"Seeded real {action} practice job #{job_id}.",
            ),
        )
        ids.append(int(cur.lastrowid))
    conn.commit()
    return ids


def active_job(citizen_id: str) -> dict:
    from agent_city.db import connect
    with connect() as conn:
        row = conn.execute(
            """
            SELECT j.*
            FROM citizens c
            JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()
        assert row is not None
        return dict(row)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.competence import (
            best_guided_practice_option,
            competence_evidence,
            competence_snapshot,
            guided_practice_snapshot,
        )
        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import complete_due_jobs, possible_actions, start_action
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        with connect() as conn:
            # Seven successful extraction jobs produce a 6% duration benefit.
            bex_practice_ids = seed_practice(
                conn,
                "bex",
                "extract",
                count=7,
                start_minute=1_000,
            )
            # Fabrication practice must not bleed into extraction.
            seed_practice(
                conn,
                "cato",
                "fabricate",
                count=8,
                start_minute=2_000,
            )
            # A failed attempt is partial experience, not a permanent penalty.
            noma_failed_ids = seed_practice(
                conn,
                "noma",
                "extract",
                count=1,
                start_minute=3_000,
                status="failed",
                outcome="failed",
            )

            bex_extraction = competence_evidence(conn, "bex", "extraction")
            cato_extraction = competence_evidence(conn, "cato", "extraction")
            cato_fabrication = competence_evidence(conn, "cato", "fabrication")
            noma_extraction = competence_evidence(conn, "noma", "extraction")

            assert bex_extraction["practice_count"] == 7
            assert bex_extraction["source_practice_event_ids"] == bex_practice_ids
            assert 0.939 <= float(bex_extraction["duration_multiplier"]) <= 0.941

            assert cato_extraction["practice_count"] == 0
            assert float(cato_extraction["duration_multiplier"]) == 1.0
            assert cato_fabrication["practice_count"] == 8
            assert float(cato_fabrication["duration_multiplier"]) < 1.0

            assert noma_extraction["source_practice_event_ids"] == noma_failed_ids
            assert 0.98 < float(noma_extraction["duration_multiplier"]) < 1.0

            # No family exposes levels, titles, or an expert threshold.
            for family in competence_snapshot(conn, "bex"):
                assert "level" not in family
                assert "rank" not in family
                assert "title" not in family
                assert "expert" not in family

            # Prepare equal physical extraction conditions.
            conn.execute("UPDATE deposits SET discovered = 1, amount = 200 WHERE id = 'dep_silicate'")
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id IN ('bex', 'cato')")
            for citizen_id in ("bex", "cato"):
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = 'rocky_basin', location = 'Rocky Basin',
                        position_x_m = 1400, position_y_m = 0,
                        energy = 100, active_job_id = NULL,
                        current_activity = 'Available'
                    WHERE id = ?
                    """,
                    (citizen_id,),
                )
            set_time(conn, 4_000)

        bex_action = next(
            a for a in possible_actions("bex")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        cato_action = next(
            a for a in possible_actions("cato")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        ok, message = start_action(
            "bex",
            {
                "action": "extract",
                "target": bex_action["target"],
                "material": bex_action["material"],
                "reason": "Compare repeated practice under equal physical conditions.",
            },
        )
        assert ok, message
        ok, message = start_action(
            "cato",
            {
                "action": "extract",
                "target": cato_action["target"],
                "material": cato_action["material"],
                "reason": "Attempt unfamiliar extraction under equal physical conditions.",
            },
        )
        assert ok, message

        bex_job = active_job("bex")
        cato_job = active_job("cato")
        bex_duration = int(bex_job["end_minute"]) - int(bex_job["start_minute"])
        cato_duration = int(cato_job["end_minute"]) - int(cato_job["start_minute"])
        assert bex_duration < cato_duration
        assert bex_job["competence_family"] == "extraction"
        assert 0.939 <= float(bex_job["competence_duration_multiplier"]) <= 0.941
        assert float(cato_job["competence_duration_multiplier"]) == 1.0
        assert bex_duration >= int(cato_duration * 0.90)

        complete_due_jobs(max(int(bex_job["end_minute"]), int(cato_job["end_minute"])))

        # Both citizens remain able to attempt the work; Cato simply gained first real practice.
        with connect() as conn:
            cato_after = competence_evidence(conn, "cato", "extraction")
            assert cato_after["practice_count"] == 1
            assert float(cato_after["duration_multiplier"]) < 1.0

            # Reset both to the same physical point for guided practice.
            for citizen_id in ("bex", "cato"):
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = 'seed_site', location = 'Seed Site',
                        position_x_m = 0, position_y_m = 0,
                        energy = 100, active_job_id = NULL,
                        current_activity = 'Available'
                    WHERE id = ?
                    """,
                    (citizen_id,),
                )
            set_time(conn, 5_000)

            option = best_guided_practice_option(conn, "bex", "cato")
            assert option is not None
            assert option["family"] == "extraction"
            assert float(option["teacher_weighted_evidence"]) > float(option["learner_weighted_evidence"])

        guide_action = next(
            a for a in possible_actions("bex")
            if a["action"] == "guided_practice"
            and a["learner_id"] == "cato"
            and a["activity_family"] == "extraction"
        )
        ok, message = start_action(
            "bex",
            {
                "action": "guided_practice",
                "target": guide_action["target"],
                "reason": "Guide Cato through extraction practice preparation.",
            },
        )
        assert ok, message

        guided_job = active_job("bex")
        cato_guided_job = active_job("cato")
        assert guided_job["id"] == cato_guided_job["id"]
        assert guided_job["action"] == "guided_practice"

        complete_due_jobs(int(guided_job["end_minute"]))

        with connect() as conn:
            sessions = guided_practice_snapshot(conn, "cato")
            session = next(row for row in sessions if int(row["job_id"]) == int(guided_job["id"]))
            session_id = int(session["id"])
            assert session["status"] == "complete"
            assert session["consumed_by_job_id"] is None

            # The guided session itself is not competence/practice evidence.
            assert conn.execute(
                "SELECT 1 FROM practice_events WHERE job_id = ?",
                (guided_job["id"],),
            ).fetchone() is None

            cato_before_guided_task = competence_evidence(conn, "cato", "extraction")
            assert cato_before_guided_task["practice_count"] == 1

            # Move learner to the existing extraction site. Travel is not extraction practice.
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'rocky_basin', location = 'Rocky Basin',
                    position_x_m = 1400, position_y_m = 0,
                    energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = 'cato'")
            set_time(conn, 6_000)

        guided_extract = next(
            a for a in possible_actions("cato")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        ok, message = start_action(
            "cato",
            {
                "action": "extract",
                "target": guided_extract["target"],
                "material": guided_extract["material"],
                "reason": "Apply the completed guided-practice preparation on a real extraction task.",
            },
        )
        assert ok, message
        guided_extract_job = active_job("cato")
        guided_duration = int(guided_extract_job["end_minute"]) - int(guided_extract_job["start_minute"])
        assert guided_extract_job["guidance_session_id"] == session_id
        assert float(guided_extract_job["competence_duration_multiplier"]) >= 0.90
        assert float(guided_extract_job["competence_duration_multiplier"]) < float(
            cato_before_guided_task["duration_multiplier"]
        )

        with connect() as conn:
            consumed = conn.execute(
                "SELECT consumed_by_job_id FROM guided_practice_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            assert int(consumed["consumed_by_job_id"]) == int(guided_extract_job["id"])

        complete_due_jobs(int(guided_extract_job["end_minute"]))

        # The learner's actual matching task, not the teaching session, creates new practice evidence.
        with connect() as conn:
            cato_after_guided_task = competence_evidence(conn, "cato", "extraction")
            assert cato_after_guided_task["practice_count"] == 2

            # Guidance is one-use. The next matching task uses only practice-derived competence.
            conn.execute("DELETE FROM citizen_inventory WHERE citizen_id = 'cato'")
            conn.execute(
                "UPDATE citizens SET energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'cato'"
            )
            set_time(conn, 7_000)

        next_extract = next(
            a for a in possible_actions("cato")
            if a["action"] == "extract" and a["target"] == "dep_silicate"
        )
        ok, message = start_action(
            "cato",
            {
                "action": "extract",
                "target": next_extract["target"],
                "material": next_extract["material"],
                "reason": "Repeat extraction after guidance has already been consumed.",
            },
        )
        assert ok, message
        next_job = active_job("cato")
        next_duration = int(next_job["end_minute"]) - int(next_job["start_minute"])
        assert next_job["guidance_session_id"] is None
        assert next_duration > guided_duration

        # Removing the canonical practice evidence removes the objective competence justification.
        with connect() as conn:
            conn.execute("DELETE FROM practice_events WHERE citizen_id = 'bex' AND activity_type = 'extract'")
            stripped = competence_evidence(conn, "bex", "extraction")
            assert stripped["practice_count"] == 0
            assert float(stripped["duration_multiplier"]) == 1.0

        print("Agent City v0.9 Simulation competence/guided-practice Stage 2 smoke passed.")


if __name__ == "__main__":
    main()
