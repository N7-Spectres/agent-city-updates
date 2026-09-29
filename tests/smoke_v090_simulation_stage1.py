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


def finish(citizen_id: str) -> dict:
    from agent_city.simulation import complete_due_jobs
    job = active_job(citizen_id)
    complete_due_jobs(int(job["end_minute"]))
    return job


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.continuity import (
            causal_candidates_for_new_plan,
            create_plan,
            plan_context_for_planner,
            plan_snapshot_for,
            practice_snapshot_for,
            transition_plan,
        )
        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import ensure_memory_schema, record_knowledge_event
        from agent_city.simulation import possible_actions, start_action
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # The standalone Simulation branch intentionally does not duplicate
        # Memory's causal-ranking module.
        assert causal_candidates_for_new_plan("bex", now=10_000) == []

        reason_id = record_knowledge_event(
            "bex",
            sim_minute=1_000,
            event_kind="personal_experience",
            source_type="job",
            source_id=9001,
            summary="Bex previously left Resin Grove without completing the survey.",
            metadata={
                "action": "survey",
                "location_id": "resin_grove",
                "verification": "verified",
            },
            status="verified",
            importance=0.65,
        )
        assert reason_id is not None

        foreign_id = record_knowledge_event(
            "cato",
            sim_minute=1_100,
            event_kind="personal_experience",
            source_type="job",
            source_id=9002,
            summary="Cato completed unrelated logistics work.",
            metadata={"action": "travel", "verification": "verified"},
            status="verified",
            importance=0.5,
        )
        assert foreign_id is not None

        # Foreign or missing Memory cannot justify Bex's plan.
        ok, plan_id, message = create_plan(
            "bex",
            intent="Return to Resin Grove and complete the unfinished survey.",
            next_step="Travel to Resin Grove.",
            unresolved_question="Whether the earlier survey left useful work unfinished.",
            memory_event_ids=[foreign_id],
            now=2_000,
        )
        assert not ok and plan_id is None
        assert "source Memory" in message

        ok, plan_id, message = create_plan(
            "bex",
            intent="Return to Resin Grove and complete the unfinished survey.",
            next_step="Travel to Resin Grove.",
            unresolved_question="Whether the earlier survey left useful work unfinished.",
            memory_event_ids=[reason_id],
            now=2_000,
        )
        assert ok, message
        assert plan_id is not None

        plans = plan_snapshot_for("bex", include_closed=False)
        assert len(plans) == 1
        assert plans[0]["id"] == plan_id
        assert plans[0]["status"] == "active"
        assert plans[0]["memory_event_ids"] == [reason_id]

        context = plan_context_for_planner("bex", now=2_000)
        assert f"Plan #{plan_id}" in context
        assert f"Memory #{reason_id}" in context
        assert "unfinished survey" in context.lower()

        # Unrelated time/action does not erase the unfinished plan.
        with connect() as conn:
            set_time(conn, 2_200)
        ok, _ = start_action(
            "cato",
            {"action": "wait", "target": "seed_site", "reason": "Observe for a while."},
        )
        assert ok
        finish("cato")
        assert plan_snapshot_for("bex", include_closed=False)[0]["id"] == plan_id

        # Real physical plan step.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'bex'
                """
            )
            set_time(conn, 3_000)

        travel = next(
            a for a in possible_actions("bex")
            if a["action"] == "travel" and a["target"] == "resin_grove"
        )
        ok, message = start_action(
            "bex",
            {
                "action": "travel",
                "target": travel["target"],
                "reason": "Continue the unfinished Resin Grove plan.",
                "plan_id": plan_id,
            },
        )
        assert ok, message
        travel_job = active_job("bex")
        assert travel_job["plan_id"] == plan_id
        finish("bex")

        practice = practice_snapshot_for("bex")
        travel_practice = next(p for p in practice if p["job_id"] == travel_job["id"])
        assert travel_practice["activity_type"] == "travel"
        assert travel_practice["plan_id"] == plan_id
        assert travel_practice["job_status"] == "complete"
        assert travel_practice["outcome"] == "success"

        with connect() as conn:
            transitions = conn.execute(
                """
                SELECT transition_type, source_job_id
                FROM plan_transitions
                WHERE plan_id = ?
                ORDER BY id
                """,
                (plan_id,),
            ).fetchall()
            assert any(
                row["transition_type"] == "step_started"
                and int(row["source_job_id"]) == int(travel_job["id"])
                for row in transitions
            )
            assert any(
                row["transition_type"] == "step_outcome"
                and int(row["source_job_id"]) == int(travel_job["id"])
                for row in transitions
            )

        # Physical interruption can pause without deleting the initiating Memory.
        ok, message = transition_plan(
            "bex",
            plan_id,
            operation="pause",
            now=int(travel_job["end_minute"]) + 1,
            source_job_id=int(travel_job["id"]),
        )
        assert ok, message
        assert plan_snapshot_for("bex", include_closed=False)[0]["status"] == "paused"

        # Paused plan cannot be attached to a new physical step.
        survey = next(a for a in possible_actions("bex") if a["action"] == "survey")
        ok, message = start_action(
            "bex",
            {
                "action": "survey",
                "target": survey["target"],
                "reason": "Try to survey while plan is paused.",
                "plan_id": plan_id,
            },
        )
        assert not ok
        assert "not an active plan" in message

        ok, message = transition_plan(
            "bex",
            plan_id,
            operation="resume",
            now=int(travel_job["end_minute"]) + 5,
        )
        assert ok, message

        # Resume and complete another real step.
        with connect() as conn:
            set_time(conn, int(travel_job["end_minute"]) + 10)
        survey = next(a for a in possible_actions("bex") if a["action"] == "survey")
        ok, message = start_action(
            "bex",
            {
                "action": "survey",
                "target": survey["target"],
                "reason": "Resume and complete the Resin Grove survey.",
                "plan_id": plan_id,
            },
        )
        assert ok, message
        survey_job = active_job("bex")
        finish("bex")

        practice = practice_snapshot_for("bex")
        survey_practice = next(p for p in practice if p["job_id"] == survey_job["id"])
        assert survey_practice["activity_type"] == "survey"
        assert survey_practice["plan_id"] == plan_id

        # The real survey job may close the intent, but completion remains a
        # separate citizen-plan lifecycle decision.
        ok, message = transition_plan(
            "bex",
            plan_id,
            operation="complete",
            now=int(survey_job["end_minute"]) + 1,
            source_job_id=int(survey_job["id"]),
        )
        assert ok, message
        closed = plan_snapshot_for("bex", include_closed=True)[0]
        assert closed["status"] == "completed"
        assert closed["memory_event_ids"] == [reason_id]

        # A closed plan cannot command more work.
        with connect() as conn:
            conn.execute(
                "UPDATE citizens SET active_job_id = NULL, current_activity = 'Available' WHERE id = 'bex'"
            )
            set_time(conn, int(survey_job["end_minute"]) + 20)
        wait = next(a for a in possible_actions("bex") if a["action"] == "wait")
        ok, message = start_action(
            "bex",
            {
                "action": "wait",
                "target": wait["target"],
                "reason": "Idle observation.",
                "plan_id": plan_id,
            },
        )
        assert not ok

        # Talking/waiting are not practice evidence.
        before_count = len(practice_snapshot_for("cato"))
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET active_job_id = NULL, current_activity = 'Available', energy = 100
                WHERE id = 'cato'
                """
            )
            set_time(conn, int(survey_job["end_minute"]) + 30)
        wait = next(a for a in possible_actions("cato") if a["action"] == "wait")
        ok, _ = start_action(
            "cato",
            {"action": "wait", "target": wait["target"], "reason": "Wait without practice gain."},
        )
        assert ok
        finish("cato")
        assert len(practice_snapshot_for("cato")) == before_count

        state = snapshot()
        assert "plans" in state
        assert "plan_transitions" in state
        assert "practice_events" in state
        assert not any(
            key in state
            for key in ("roles", "classes", "specializations", "xp", "reputation")
        )

        with connect() as conn:
            plan_columns = {
                row["name"] for row in conn.execute("PRAGMA table_info(citizen_plans)")
            }
            assert "role" not in plan_columns
            assert "class" not in plan_columns
            assert "specialization" not in plan_columns

        print("Agent City v0.9 Simulation continuity Stage 1 smoke test passed.")


if __name__ == "__main__":
    main()
