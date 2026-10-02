from __future__ import annotations

import json
from typing import Any, Iterable

from .db import add_history, connect, get_meta

PLAN_OPEN_STATUSES = {"active", "paused"}
PLAN_FINAL_STATUSES = {"completed", "abandoned", "superseded"}
PLAN_STATUSES = PLAN_OPEN_STATUSES | PLAN_FINAL_STATUSES

PRACTICE_ACTIONS = {
    "travel",
    "local_move",
    "local_inspect",
    "shared_local_activity",
    "survey",
    "extract",
    "deposit_cargo",
    "experiment",
    "fabricate",
    "process_material",
    "construct",
    "service_chassis",
    "replace_battery",
    "service_equipment",
    "service_structure",
}


def _clean(value: Any, max_len: int) -> str:
    return " ".join(str(value or "").split()).strip()[:max_len]


def _memory_rows(conn, owner_id: str, memory_event_ids: Iterable[int]) -> list[Any]:
    ids = sorted({int(v) for v in memory_event_ids if int(v) > 0})
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"""
        SELECT id, owner_id, sim_minute, source_type, source_id, summary, status
        FROM memory_events
        WHERE owner_id = ? AND id IN ({placeholders})
        ORDER BY id
        """,
        (owner_id, *ids),
    ).fetchall()
    if {int(row["id"]) for row in rows} != set(ids):
        return []
    return rows


def _try_link_memory_facet(memory_event_id: int, plan_id: int) -> None:
    try:
        from .causal_memory import link_memory_event
    except ImportError:
        return
    try:
        link_memory_event(int(memory_event_id), "plan", str(plan_id))
    except Exception:
        # Memory linking is an integration convenience. The canonical source link
        # remains in Simulation even if the Memory projection is unavailable.
        return


def _insert_transition(
    conn,
    *,
    plan_id: int,
    owner_id: str,
    sim_minute: int,
    transition_type: str,
    from_status: str | None,
    to_status: str,
    summary: str,
    source_job_id: int | None = None,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO plan_transitions
        (plan_id, owner_id, sim_minute, transition_type, from_status, to_status,
         source_job_id, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(plan_id),
            owner_id,
            int(sim_minute),
            transition_type,
            from_status,
            to_status,
            source_job_id,
            _clean(summary, 900),
        ),
    )
    return int(cur.lastrowid)


def _link_plan_memories(
    conn,
    *,
    plan_id: int,
    transition_id: int,
    owner_id: str,
    memory_rows: list[Any],
    source_role: str,
    linked_minute: int,
) -> None:
    for row in memory_rows:
        memory_id = int(row["id"])
        conn.execute(
            """
            INSERT OR IGNORE INTO plan_memory_sources
            (plan_id, transition_id, owner_id, memory_event_id, source_role, linked_minute)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(plan_id),
                int(transition_id),
                owner_id,
                memory_id,
                source_role,
                int(linked_minute),
            ),
        )


def create_plan(
    owner_id: str,
    *,
    intent: str,
    next_step: str,
    unresolved_question: str | None,
    memory_event_ids: Iterable[int],
    now: int | None = None,
) -> tuple[bool, int | None, str]:
    intent_text = _clean(intent, 700)
    step_text = _clean(next_step, 700)
    question_text = _clean(unresolved_question, 700)
    if not intent_text or not step_text:
        return False, None, "A plan needs both a current intent and a next known step."

    with connect() as conn:
        citizen = conn.execute("SELECT id, name FROM citizens WHERE id = ?", (owner_id,)).fetchone()
        if not citizen:
            return False, None, "Plan owner not found."

        memory_rows = _memory_rows(conn, owner_id, memory_event_ids)
        if not memory_rows:
            return False, None, "A persistent plan requires at least one source Memory event owned by the citizen."

        minute = int(now) if now is not None else int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            INSERT INTO citizen_plans
            (owner_id, created_minute, updated_minute, status,
             current_intent, next_step, unresolved_question)
            VALUES (?, ?, ?, 'active', ?, ?, ?)
            """,
            (owner_id, minute, minute, intent_text, step_text, question_text or None),
        )
        plan_id = int(cur.lastrowid)
        transition_id = _insert_transition(
            conn,
            plan_id=plan_id,
            owner_id=owner_id,
            sim_minute=minute,
            transition_type="created",
            from_status=None,
            to_status="active",
            summary=f"Created plan: {intent_text}",
        )
        _link_plan_memories(
            conn,
            plan_id=plan_id,
            transition_id=transition_id,
            owner_id=owner_id,
            memory_rows=memory_rows,
            source_role="initiating_reason",
            linked_minute=minute,
        )
        add_history(conn, minute, "continuity", f"{citizen['name']} formed plan #{plan_id}: {intent_text}")
        conn.commit()

    for row in memory_rows:
        _try_link_memory_facet(int(row["id"]), plan_id)
    return True, plan_id, "Persistent plan created."


def _latest_plan_job(conn, plan_id: int):
    return conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE plan_id = ?
        ORDER BY COALESCE(end_minute, start_minute) DESC, id DESC
        LIMIT 1
        """,
        (int(plan_id),),
    ).fetchone()


def transition_plan(
    owner_id: str,
    plan_id: int,
    *,
    operation: str,
    now: int | None = None,
    intent: str | None = None,
    next_step: str | None = None,
    unresolved_question: str | None = None,
    memory_event_ids: Iterable[int] = (),
    source_job_id: int | None = None,
) -> tuple[bool, str]:
    operation = _clean(operation, 40).lower()
    allowed = {"revise", "pause", "resume", "abandon", "complete", "supersede"}
    if operation not in allowed:
        return False, "Unsupported plan transition."

    with connect() as conn:
        plan = conn.execute(
            "SELECT * FROM citizen_plans WHERE id = ? AND owner_id = ?",
            (int(plan_id), owner_id),
        ).fetchone()
        if not plan:
            return False, "Plan not found for this citizen."

        old_status = str(plan["status"])
        if old_status in PLAN_FINAL_STATUSES:
            return False, f"Plan is already {old_status}."

        if operation == "resume" and old_status != "paused":
            return False, "Only a paused plan can resume."
        if operation == "pause" and old_status != "active":
            return False, "Only an active plan can pause."

        target_status = {
            "revise": old_status,
            "pause": "paused",
            "resume": "active",
            "abandon": "abandoned",
            "complete": "completed",
            "supersede": "superseded",
        }[operation]

        memory_rows = _memory_rows(conn, owner_id, memory_event_ids)
        requested_ids = sorted({int(v) for v in memory_event_ids if int(v) > 0})
        if requested_ids and len(memory_rows) != len(requested_ids):
            return False, "One or more plan source memories do not belong to this citizen."

        job = None
        if source_job_id is not None:
            job = conn.execute(
                "SELECT * FROM jobs WHERE id = ? AND citizen_id = ? AND plan_id = ?",
                (int(source_job_id), owner_id, int(plan_id)),
            ).fetchone()
            if not job:
                return False, "Plan transition source job is not a job from this plan."
        elif operation in {"revise", "pause", "abandon", "complete", "supersede"} and not memory_rows:
            job = _latest_plan_job(conn, int(plan_id))
            if not job:
                return False, "This plan transition requires source Memory or a real prior plan job."

        minute = int(now) if now is not None else int(get_meta(conn, "sim_minute") or "360")
        new_intent = _clean(intent, 700) if intent is not None else str(plan["current_intent"])
        new_step = _clean(next_step, 700) if next_step is not None else str(plan["next_step"])
        new_question = (
            _clean(unresolved_question, 700)
            if unresolved_question is not None
            else str(plan["unresolved_question"] or "")
        )
        if operation == "revise" and (not new_intent or not new_step):
            return False, "A revised plan still needs intent and a next step."

        transition_id = _insert_transition(
            conn,
            plan_id=int(plan_id),
            owner_id=owner_id,
            sim_minute=minute,
            transition_type=operation,
            from_status=old_status,
            to_status=target_status,
            source_job_id=int(job["id"]) if job else source_job_id,
            summary=(
                f"{operation}: {new_intent}"
                if operation == "revise"
                else f"{operation} plan: {plan['current_intent']}"
            ),
        )
        _link_plan_memories(
            conn,
            plan_id=int(plan_id),
            transition_id=transition_id,
            owner_id=owner_id,
            memory_rows=memory_rows,
            source_role=f"{operation}_reason",
            linked_minute=minute,
        )
        conn.execute(
            """
            UPDATE citizen_plans
            SET updated_minute = ?, status = ?,
                current_intent = ?, next_step = ?, unresolved_question = ?
            WHERE id = ?
            """,
            (
                minute,
                target_status,
                new_intent,
                new_step,
                new_question or None,
                int(plan_id),
            ),
        )
        citizen = conn.execute("SELECT name FROM citizens WHERE id = ?", (owner_id,)).fetchone()
        add_history(
            conn,
            minute,
            "continuity",
            f"{citizen['name'] if citizen else owner_id} {operation} plan #{plan_id}.",
        )
        conn.commit()

    for row in memory_rows:
        _try_link_memory_facet(int(row["id"]), int(plan_id))
    return True, f"Plan {operation} recorded."


def plan_memory_event_ids(owner_id: str, plan_id: int) -> list[int]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT memory_event_id
            FROM plan_memory_sources
            WHERE plan_id = ? AND owner_id = ?
            ORDER BY memory_event_id
            """,
            (int(plan_id), owner_id),
        ).fetchall()
        return [int(row["memory_event_id"]) for row in rows]


def plan_snapshot_for(owner_id: str, *, include_closed: bool = True, limit: int = 12) -> list[dict[str, Any]]:
    with connect() as conn:
        where = "owner_id = ?"
        params: list[Any] = [owner_id]
        if not include_closed:
            where += " AND status IN ('active', 'paused')"
        params.append(max(1, min(int(limit), 50)))
        plans = [
            dict(row)
            for row in conn.execute(
                f"""
                SELECT *
                FROM citizen_plans
                WHERE {where}
                ORDER BY
                    CASE status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END,
                    updated_minute DESC, id DESC
                LIMIT ?
                """,
                tuple(params),
            ).fetchall()
        ]
        for plan in plans:
            pid = int(plan["id"])
            plan["memory_event_ids"] = [
                int(row["memory_event_id"])
                for row in conn.execute(
                    """
                    SELECT DISTINCT memory_event_id
                    FROM plan_memory_sources
                    WHERE plan_id = ?
                    ORDER BY memory_event_id
                    """,
                    (pid,),
                ).fetchall()
            ]
            plan["recent_transitions"] = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT *
                    FROM plan_transitions
                    WHERE plan_id = ?
                    ORDER BY id DESC LIMIT 8
                    """,
                    (pid,),
                ).fetchall()
            ]
        return plans


def _memory_context_for_plan(owner_id: str, plan: dict[str, Any], now: int) -> str:
    pinned = [int(v) for v in plan.get("memory_event_ids", [])]
    try:
        from .causal_memory import causal_recall_context_for
    except ImportError:
        causal_recall_context_for = None

    if causal_recall_context_for:
        try:
            return causal_recall_context_for(
                owner_id,
                now_minute=now,
                facet_filters={"plan": str(plan["id"])},
                pinned_event_ids=pinned,
                limit=5,
            )
        except Exception:
            pass

    if not pinned:
        return "- no linked source Memory"
    with connect() as conn:
        placeholders = ",".join("?" for _ in pinned)
        rows = conn.execute(
            f"""
            SELECT id, source_type, source_id, summary
            FROM memory_events
            WHERE owner_id = ? AND id IN ({placeholders})
            ORDER BY sim_minute DESC, id DESC
            LIMIT 5
            """,
            (owner_id, *pinned),
        ).fetchall()
    return "\n".join(
        f"- Memory #{row['id']} ({row['source_type']} #{row['source_id']}): {row['summary']}"
        for row in rows
    ) or "- no linked source Memory"


def sync_plan_memory_facets() -> int:
    try:
        from .causal_memory import link_memory_event
    except ImportError:
        return 0

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT plan_id, memory_event_id
            FROM plan_memory_sources
            ORDER BY plan_id, memory_event_id
            """
        ).fetchall()

    linked = 0
    for row in rows:
        try:
            if link_memory_event(
                int(row["memory_event_id"]),
                "plan",
                str(int(row["plan_id"])),
            ):
                linked += 1
        except Exception:
            continue
    return linked


def plan_context_for_planner(owner_id: str, *, now: int | None = None) -> str:
    sync_plan_memory_facets()
    minute = int(now) if now is not None else None
    if minute is None:
        with connect() as conn:
            minute = int(get_meta(conn, "sim_minute") or "360")

    plans = plan_snapshot_for(owner_id, include_closed=False, limit=3)
    if not plans:
        return "UNFINISHED PLANS:\n- none"

    chunks = ["UNFINISHED PLANS:"]
    for plan in plans:
        chunks.append(
            f"- Plan #{plan['id']} [{plan['status']}]: {plan['current_intent']}\n"
            f"  Next step: {plan['next_step']}\n"
            f"  Unresolved: {plan.get('unresolved_question') or 'none'}\n"
            f"  Linked source Memory IDs: {plan['memory_event_ids']}\n"
            f"  Source-backed recall:\n{_memory_context_for_plan(owner_id, plan, minute)}"
        )
    return "\n".join(chunks)[:4200]


def causal_candidates_for_new_plan(owner_id: str, *, now: int, limit: int = 6) -> list[dict[str, Any]]:
    try:
        from .causal_memory import causal_recall_snapshot
    except ImportError:
        return []
    try:
        return causal_recall_snapshot(owner_id, now_minute=now, limit=max(1, min(limit, 8)))
    except Exception:
        return []


def apply_planner_plan_decision(
    owner_id: str,
    decision: dict[str, Any],
    *,
    now: int,
) -> tuple[bool, int | None, str]:
    operation = _clean(decision.get("plan_operation"), 40).lower() or "none"
    if operation in {"none", "continue"}:
        plan_id = decision.get("plan_id")
        if operation == "continue" and plan_id:
            with connect() as conn:
                row = conn.execute(
                    "SELECT id FROM citizen_plans WHERE id = ? AND owner_id = ? AND status = 'active'",
                    (int(plan_id), owner_id),
                ).fetchone()
            if not row:
                return False, None, "Requested active plan does not exist."
            return True, int(plan_id), "Continuing active plan."
        return True, None, "No plan lifecycle change."

    memory_ids = [
        int(v) for v in (decision.get("plan_memory_event_ids") or [])
        if str(v).isdigit() and int(v) > 0
    ]

    if operation == "create":
        return create_plan(
            owner_id,
            intent=_clean(decision.get("plan_intent"), 700),
            next_step=_clean(decision.get("plan_next_step"), 700),
            unresolved_question=_clean(decision.get("plan_unresolved_question"), 700),
            memory_event_ids=memory_ids,
            now=now,
        )

    plan_id = decision.get("plan_id")
    if not plan_id:
        return False, None, "Plan transition requires a plan ID."

    ok, message = transition_plan(
        owner_id,
        int(plan_id),
        operation=operation,
        now=now,
        intent=decision.get("plan_intent"),
        next_step=decision.get("plan_next_step"),
        unresolved_question=decision.get("plan_unresolved_question"),
        memory_event_ids=memory_ids,
    )
    if not ok:
        return False, None, message
    with connect() as conn:
        row = conn.execute(
            "SELECT status FROM citizen_plans WHERE id = ? AND owner_id = ?",
            (int(plan_id), owner_id),
        ).fetchone()
    active_id = int(plan_id) if row and row["status"] == "active" else None
    return True, active_id, message


def attach_job_to_plan(
    conn,
    *,
    owner_id: str,
    plan_id: int,
    job_id: int,
    sim_minute: int,
) -> bool:
    plan = conn.execute(
        "SELECT * FROM citizen_plans WHERE id = ? AND owner_id = ? AND status = 'active'",
        (int(plan_id), owner_id),
    ).fetchone()
    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ? AND citizen_id = ?",
        (int(job_id), owner_id),
    ).fetchone()
    if not plan or not job:
        return False

    conn.execute("UPDATE jobs SET plan_id = ? WHERE id = ?", (int(plan_id), int(job_id)))
    _insert_transition(
        conn,
        plan_id=int(plan_id),
        owner_id=owner_id,
        sim_minute=int(sim_minute),
        transition_type="step_started",
        from_status="active",
        to_status="active",
        source_job_id=int(job_id),
        summary=f"Started plan step via {job['action']} job #{job_id}.",
    )
    conn.execute(
        "UPDATE citizen_plans SET updated_minute = ? WHERE id = ?",
        (int(sim_minute), int(plan_id)),
    )
    return True


def record_plan_job_outcome(conn, job: Any, *, sim_minute: int) -> None:
    if job["plan_id"] is None:
        return
    plan = conn.execute(
        "SELECT * FROM citizen_plans WHERE id = ? AND owner_id = ?",
        (int(job["plan_id"]), str(job["citizen_id"])),
    ).fetchone()
    if not plan:
        return
    _insert_transition(
        conn,
        plan_id=int(plan["id"]),
        owner_id=str(plan["owner_id"]),
        sim_minute=int(sim_minute),
        transition_type="step_outcome",
        from_status=str(plan["status"]),
        to_status=str(plan["status"]),
        source_job_id=int(job["id"]),
        summary=f"{job['action']} job #{job['id']} ended with outcome {job['outcome']}.",
    )
    conn.execute(
        "UPDATE citizen_plans SET updated_minute = ? WHERE id = ?",
        (int(sim_minute), int(plan["id"])),
    )


def _practice_location_for_job(conn, job: Any) -> str | None:
    action = str(job["action"] or "")
    if action in {"travel", "survey"} and job["target"]:
        return str(job["target"])
    if action == "extract" and job["target"]:
        row = conn.execute(
            "SELECT location_id FROM deposits WHERE id = ?",
            (str(job["target"]),),
        ).fetchone()
        if row:
            return str(row["location_id"])
    if action == "construct" and job["project_id"] is not None:
        row = conn.execute(
            "SELECT location_id FROM projects WHERE id = ?",
            (int(job["project_id"]),),
        ).fetchone()
        if row:
            return str(row["location_id"])
    row = conn.execute(
        "SELECT location_id FROM citizens WHERE id = ?",
        (str(job["citizen_id"]),),
    ).fetchone()
    return str(row["location_id"]) if row else None


def record_practice_event_for_job(conn, job: Any, *, sim_minute: int) -> int | None:
    action = str(job["action"] or "")
    if action not in PRACTICE_ACTIONS or str(job["status"]) not in {"complete", "failed"}:
        return None

    existing = conn.execute(
        "SELECT id FROM practice_events WHERE job_id = ?",
        (int(job["id"]),),
    ).fetchone()
    if existing:
        return int(existing["id"])

    location_id = _practice_location_for_job(conn, job)
    verb = "Completed" if str(job["status"]) == "complete" else "Ended"
    summary = f"{verb} {action} job #{int(job['id'])} with outcome {job['outcome'] or job['status']}."
    cur = conn.execute(
        """
        INSERT INTO practice_events
        (citizen_id, job_id, plan_id, activity_type, job_status, outcome, completed_minute,
         location_id, target, material, project_id, observation_id,
         shared_activity_id, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(job["citizen_id"]),
            int(job["id"]),
            int(job["plan_id"]) if job["plan_id"] is not None else None,
            action,
            str(job["status"]),
            str(job["outcome"] or "success"),
            int(sim_minute),
            location_id,
            str(job["target"]) if job["target"] is not None else None,
            str(job["material"]) if job["material"] is not None else None,
            int(job["project_id"]) if job["project_id"] is not None else None,
            int(job["result_observation_id"]) if job["result_observation_id"] is not None else None,
            int(job["shared_activity_id"]) if job["shared_activity_id"] is not None else None,
            summary,
        ),
    )
    return int(cur.lastrowid)


def sync_practice_events_in_conn(conn) -> int:
    rows = conn.execute(
        """
        SELECT j.*
        FROM jobs j
        WHERE j.status IN ('complete', 'failed')
          AND NOT EXISTS (
              SELECT 1 FROM practice_events pe WHERE pe.job_id = j.id
          )
        ORDER BY j.end_minute, j.id
        """
    ).fetchall()
    added = 0
    for row in rows:
        if record_practice_event_for_job(
            conn,
            row,
            sim_minute=int(row["end_minute"]),
        ) is not None:
            added += 1
    return added


def practice_snapshot_for(citizen_id: str, *, limit: int = 40) -> list[dict[str, Any]]:
    with connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT *
                FROM practice_events
                WHERE citizen_id = ?
                ORDER BY completed_minute DESC, id DESC
                LIMIT ?
                """,
                (citizen_id, max(1, min(int(limit), 120))),
            ).fetchall()
        ]
