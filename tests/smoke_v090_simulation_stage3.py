from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def add_completed_choice_job(
    conn,
    job_id: int,
    citizen_id: str,
    action: str,
    minute: int,
    *,
    location_id: str = "seed_site",
) -> None:
    conn.execute(
        """
        INSERT INTO jobs(
            id, citizen_id, action, target,
            start_minute, end_minute, status, outcome, intent_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, 'complete', 'success', ?)
        """,
        (
            job_id,
            citizen_id,
            action,
            "cato" if action == "talk" else location_id,
            minute - 20,
            minute,
            f"Chose {action} while several ordinary options were available.",
        ),
    )


def action_signature(rows):
    return [
        (
            str(row.get("action") or ""),
            str(row.get("target")),
            str(row.get("material")),
        )
        for row in rows
    ]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.causal_memory import link_memory_event
        from agent_city.db import connect, init_db, set_meta, snapshot
        from agent_city.memory import ensure_memory_schema, record_knowledge_event
        from agent_city.pattern_memory import (
            habit_candidates_for,
            record_voluntary_choice_evidence,
        )
        from agent_city.planner import citizen_context
        from agent_city.simulation import (
            _voluntary_choice_provenance,
            autonomous_actions,
            complete_due_jobs,
            possible_actions,
            start_action,
            voluntary_choice_context_key,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Put Bex and Cato together at Seed Site during the active cycle.
        now = 3 * 1440 + 600  # Day 3, 10:00.
        with connect() as conn:
            set_meta(conn, "sim_minute", str(now))
            conn.execute(
                """
                UPDATE citizens
                SET location_id='seed_site', location='Seed Site',
                    position_x_m=0, position_y_m=0,
                    active_job_id=NULL, current_activity='Available',
                    energy=100
                WHERE id IN ('bex', 'cato')
                """
            )
            conn.commit()

        with connect() as conn:
            bex_row = conn.execute("SELECT * FROM citizens WHERE id='bex'").fetchone()
            bex = dict(bex_row)
        context_key = voluntary_choice_context_key(bex, now)
        assert context_key == "location:seed_site|phase:active|open_choice"

        # Pattern evidence must never alter physical legality.
        legal_before = possible_actions("bex")
        signature_before = action_signature(legal_before)
        assert any(row["action"] == "talk" and row["target"] == "cato" for row in legal_before)

        # Seed three legitimate voluntary choices in the same deterministic
        # context across three simulation days.
        prior_minutes = (600, 2040, 3480)
        with connect() as conn:
            for job_id, minute in zip((9801, 9802, 9803), prior_minutes):
                add_completed_choice_job(conn, job_id, "bex", "talk", minute)
            conn.commit()

        for job_id in (9801, 9802, 9803):
            assert record_voluntary_choice_evidence(
                "bex",
                job_id,
                action_key="talk",
                context_key=context_key,
                location_id="seed_site",
            ) is not None

        habits = habit_candidates_for("bex", now_minute=now)
        talk_pattern = next(
            row for row in habits
            if row["action_key"] == "talk" and row["context_key"] == context_key
        )
        assert talk_pattern["state"] == "current"
        assert talk_pattern["support_count"] == 3

        legal_after = possible_actions("bex")
        assert action_signature(legal_after) == signature_before

        # Give Seed Site one unusually important source-backed personal memory
        # so place continuity can enter reasoning without becoming a favorite.
        place_memory = record_knowledge_event(
            "bex",
            sim_minute=3200,
            event_kind="meaningful_shared_experience",
            source_type="simulation_shared_activity",
            source_id=9901,
            summary="Bex completed a difficult shared inspection at Seed Site.",
            metadata={"verification": "verified", "location_id": "seed_site"},
            status="verified",
            importance=0.80,
        )
        assert place_memory is not None
        assert link_memory_event(place_memory, "location", "seed_site")

        state = snapshot()
        bex_state = next(row for row in state["citizens"] if row["id"] == "bex")
        autonomous = autonomous_actions("bex")
        context_text = citizen_context(bex_state, state, autonomous)
        assert "SOURCE-BACKED RECURRING VOLUNTARY CHOICE EVIDENCE" in context_text
        assert "action=talk" in context_text
        assert "evidence state=current" in context_text
        assert "PERSONAL PLACE-CONTINUITY EVIDENCE" in context_text
        assert "not personality traits, roles, preferences, commands" in context_text
        assert "You remain free to choose a different legal action" in context_text

        # Simulation classifies ordinary autonomous choice provenance
        # conservatively. Forced/maintenance/travel actions never qualify.
        with connect() as conn:
            bex_row = conn.execute("SELECT * FROM citizens WHERE id='bex'").fetchone()
            bex = dict(bex_row)
        for forced_action in ("charge", "travel", "service_chassis"):
            eligible, key, location = _voluntary_choice_provenance(
                bex,
                action=forced_action,
                sim_minute=now,
                intent_reason="Fixture reason.",
                plan_id=None,
                autonomous_choice=True,
                autonomous_action_count=5,
            )
            assert eligible == 0
            assert key is None and location is None

        eligible, key, location = _voluntary_choice_provenance(
            bex,
            action="talk",
            sim_minute=now,
            intent_reason="Check in with Cato while several options are open.",
            plan_id=None,
            autonomous_choice=True,
            autonomous_action_count=max(2, len(autonomous)),
        )
        assert eligible == 1
        assert key == context_key
        assert location == "seed_site"

        one_option = _voluntary_choice_provenance(
            bex,
            action="talk",
            sim_minute=now,
            intent_reason="Only one option.",
            plan_id=None,
            autonomous_choice=True,
            autonomous_action_count=1,
        )
        assert one_option == (0, None, None)

        # Start one real autonomous face-to-face talk. The job is tagged at
        # start, but Memory evidence does not exist until the physical job
        # reaches a successful terminal state.
        decision = {
            "action": "talk",
            "target": "cato",
            "material": None,
            "reason": "I want to check in with Cato while I have several reasonable choices.",
        }
        current_actions = autonomous_actions("bex")
        ok, _ = start_action(
            "bex",
            decision,
            autonomous_choice=True,
            autonomous_action_count=len(current_actions),
        )
        assert ok

        with connect() as conn:
            active = conn.execute(
                "SELECT active_job_id FROM citizens WHERE id='bex'"
            ).fetchone()
            job_id = int(active["active_job_id"])
            job = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            assert int(job["voluntary_choice_eligible"]) == 1
            assert job["voluntary_choice_context"] == context_key
            assert job["voluntary_choice_location_id"] == "seed_site"
            before_evidence = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM memory_pattern_evidence
                WHERE owner_id='bex'
                  AND evidence_kind='voluntary_choice'
                  AND source_type='job'
                  AND source_id=?
                """,
                (job_id,),
            ).fetchone()["n"]
            assert int(before_evidence) == 0

            conn.execute(
                """
                INSERT INTO citizen_conversations(
                    sim_minute, location_id, initiator_id, target_id,
                    initiator_text, target_text, summary, source_job_id
                )
                VALUES (?, 'seed_site', 'bex', 'cato',
                        'How is your work going?',
                        'Steady. I have been checking the stores.',
                        'Bex and Cato checked in face to face.', ?)
                """,
                (now, job_id),
            )
            conn.commit()

        complete_due_jobs(now + 20)

        with connect() as conn:
            completed = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            assert completed["status"] == "complete"
            retained = conn.execute(
                """
                SELECT *
                FROM memory_pattern_evidence
                WHERE owner_id='bex'
                  AND evidence_kind='voluntary_choice'
                  AND source_type='job'
                  AND source_id=?
                """,
                (job_id,),
            ).fetchall()
            assert len(retained) == 1
            assert retained[0]["context_key"] == context_key

        # A plan-attached action is still a real action, but it is not tagged
        # as a free recurring-choice source for Stage 3.
        later = now + 60
        with connect() as conn:
            set_meta(conn, "sim_minute", str(later))
            cur = conn.execute(
                """
                INSERT INTO citizen_plans(
                    owner_id, created_minute, updated_minute, status,
                    current_intent, next_step, unresolved_question
                )
                VALUES (
                    'bex', ?, ?, 'active',
                    'Maintain a deliberate communication check-in',
                    'Talk with Cato', NULL
                )
                """,
                (later, later),
            )
            plan_id = int(cur.lastrowid)
            conn.commit()

        planned_decision = {
            "action": "talk",
            "target": "cato",
            "material": None,
            "reason": "Continue the active check-in plan.",
            "plan_id": plan_id,
        }
        planned_actions = autonomous_actions("bex")
        ok, _ = start_action(
            "bex",
            planned_decision,
            autonomous_choice=True,
            autonomous_action_count=max(2, len(planned_actions)),
        )
        assert ok
        with connect() as conn:
            planned_job_id = int(
                conn.execute(
                    "SELECT active_job_id FROM citizens WHERE id='bex'"
                ).fetchone()["active_job_id"]
            )
            planned_job = conn.execute(
                "SELECT * FROM jobs WHERE id=?", (planned_job_id,)
            ).fetchone()
            assert int(planned_job["voluntary_choice_eligible"]) == 0
            assert planned_job["voluntary_choice_context"] is None

        print("Agent City v0.9 Stage 3 Simulation habit-context smoke passed.")


if __name__ == "__main__":
    main()
