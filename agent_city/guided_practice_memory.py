from __future__ import annotations

import json
from typing import Any

from .db import connect

SOURCE_TYPE = "simulation_guided_practice_session"
TERMINAL_STATUSES = {"complete", "failed", "cancelled", "canceled"}


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _insert_facet(conn, owner_id: str, memory_event_id: int, kind: str, value: Any) -> None:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return
    conn.execute(
        """
        INSERT OR IGNORE INTO memory_event_facets(
            owner_id, memory_event_id, facet_kind, facet_value
        )
        VALUES (?, ?, ?, ?)
        """,
        (owner_id, int(memory_event_id), kind[:80], text[:180]),
    )


def _citizen_name(conn, citizen_id: str) -> str:
    row = conn.execute("SELECT name FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    return str(row["name"]) if row else citizen_id


def _importance(status: str) -> float:
    if status == "complete":
        return 0.72
    if status == "failed":
        return 0.68
    return 0.60


def _summary_for_role(conn, session, role: str) -> str:
    family = str(session["activity_family"])
    status = str(session["status"])
    teacher_id = str(session["teacher_id"])
    learner_id = str(session["learner_id"])
    if role == "teacher":
        other = _citizen_name(conn, learner_id)
        if status == "complete":
            return f"Completed guided {family} practice with {other} as the guide."
        return f"Guided {family} practice with {other} ended with status {status}."
    other = _citizen_name(conn, teacher_id)
    if status == "complete":
        return f"Completed guided {family} practice with {other} as the learner."
    return f"Guided {family} practice with {other} ended with status {status}."


def _ensure_role_memory(conn, session, role: str) -> int | None:
    owner_id = str(session["teacher_id"] if role == "teacher" else session["learner_id"])
    counterparty_id = str(session["learner_id"] if role == "teacher" else session["teacher_id"])
    if not conn.execute("SELECT 1 FROM citizens WHERE id = ?", (owner_id,)).fetchone():
        return None

    event_kind = f"guided_practice_{str(session['status'])}"[:80]
    metadata = {
        "verification": "verified",
        "channel": "personal_experience",
        "guided_practice_session_id": int(session["id"]),
        "job_id": int(session["job_id"]) if session["job_id"] is not None else None,
        "teacher_id": str(session["teacher_id"]),
        "learner_id": str(session["learner_id"]),
        "guided_role": role,
        "activity_family": str(session["activity_family"]),
        "session_status": str(session["status"]),
        "started_minute": int(session["started_minute"]),
        "completed_minute": int(session["completed_minute"]),
        "source_conversation_id": (
            int(session["source_conversation_id"])
            if session["source_conversation_id"] is not None
            else None
        ),
    }

    cur = conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'verified', ?)
        """,
        (
            owner_id,
            int(session["completed_minute"]),
            event_kind,
            counterparty_id,
            SOURCE_TYPE,
            int(session["id"]),
            role,
            _summary_for_role(conn, session, role)[:1200],
            _importance(str(session["status"])),
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ),
    )
    if cur.rowcount:
        memory_id = int(cur.lastrowid)
    else:
        row = conn.execute(
            """
            SELECT id FROM memory_events
            WHERE owner_id = ?
              AND source_type = ?
              AND source_id = ?
              AND event_kind = ?
              AND source_role = ?
            LIMIT 1
            """,
            (owner_id, SOURCE_TYPE, int(session["id"]), event_kind, role),
        ).fetchone()
        if not row:
            return None
        memory_id = int(row["id"])

    _insert_facet(conn, owner_id, memory_id, "guided_practice_session", int(session["id"]))
    _insert_facet(conn, owner_id, memory_id, "activity", "guided_practice")
    _insert_facet(conn, owner_id, memory_id, "competence_family", session["activity_family"])
    _insert_facet(conn, owner_id, memory_id, "guided_role", role)
    _insert_facet(conn, owner_id, memory_id, "counterparty", counterparty_id)
    if session["source_conversation_id"] is not None:
        _insert_facet(
            conn,
            owner_id,
            memory_id,
            "source_conversation",
            int(session["source_conversation_id"]),
        )
    if session["consumed_by_job_id"] is not None:
        _insert_facet(
            conn,
            owner_id,
            memory_id,
            "applied_job",
            int(session["consumed_by_job_id"]),
        )
    return memory_id


def sync_guided_practice_memory_in_conn(conn) -> None:
    """
    Retain terminal Simulation-guided practice as role-specific personal Memory.

    The session itself is NOT tagged as a practice_event and creates no
    competence. Teacher/learner roles are event-local, not identity labels.
    """
    if not _table_exists(conn, "guided_practice_sessions"):
        return
    if not _table_exists(conn, "memory_event_facets"):
        return

    placeholders = ",".join("?" for _ in sorted(TERMINAL_STATUSES))
    rows = conn.execute(
        f"""
        SELECT id, job_id, teacher_id, learner_id, activity_family, status,
               started_minute, completed_minute, source_conversation_id,
               consumed_by_job_id, summary
        FROM guided_practice_sessions
        WHERE status IN ({placeholders})
          AND completed_minute IS NOT NULL
        ORDER BY id
        """,
        tuple(sorted(TERMINAL_STATUSES)),
    ).fetchall()

    for session in rows:
        _ensure_role_memory(conn, session, "teacher")
        _ensure_role_memory(conn, session, "learner")


def sync_guided_practice_memory() -> None:
    from .causal_memory import ensure_causal_memory_schema_in_conn

    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        sync_guided_practice_memory_in_conn(conn)
        ensure_causal_memory_schema_in_conn(conn)
        conn.commit()


def guided_practice_recall_snapshot_for(
    citizen_id: str,
    *,
    family: str | None = None,
    counterpart_id: str | None = None,
    role: str | None = None,
    now_minute: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Return bounded actively recalled teaching/learning experiences for one owner.

    This never compares global citizen ledgers or exposes Simulation's competence
    weights. A past teacher/learner role describes that event only.
    """
    from .causal_memory import causal_recall_snapshot

    sync_guided_practice_memory()
    filters = {"competence_family": family} if family else None
    recalled = causal_recall_snapshot(
        citizen_id,
        now_minute=now_minute,
        facet_filters=filters,
        required_facet_kind="guided_practice_session",
        limit=24,
    )

    safe_limit = max(1, min(int(limit), 16))
    result: list[dict[str, Any]] = []
    for item in recalled:
        facets = item.get("facets") or []
        if counterpart_id is not None and not any(
            str(f.get("kind")) == "counterparty"
            and str(f.get("value")) == str(counterpart_id)
            for f in facets
        ):
            continue
        if role is not None and not any(
            str(f.get("kind")) == "guided_role"
            and str(f.get("value")) == str(role)
            for f in facets
        ):
            continue

        clean = dict(item)
        clean.pop("recall_score", None)
        clean.pop("reinforcement_count", None)
        clean.pop("matching_facets", None)
        result.append(clean)
        if len(result) >= safe_limit:
            break
    return result


def guided_practice_recall_context_for(
    citizen_id: str,
    *,
    family: str | None = None,
    counterpart_id: str | None = None,
    role: str | None = None,
    now_minute: int | None = None,
    limit: int = 6,
) -> str:
    memories = guided_practice_recall_snapshot_for(
        citizen_id,
        family=family,
        counterpart_id=counterpart_id,
        role=role,
        now_minute=now_minute,
        limit=limit,
    )
    if not memories:
        return "- no actively recalled source-backed guided-practice experience matched"

    lines: list[str] = []
    for item in memories:
        lines.append(
            f"- Verified, {item.get('sim_label')} "
            f"({item.get('source_type')} #{item.get('source_id')}, role {item.get('source_role')}): "
            f"{' '.join(str(item.get('summary') or '').split())[:360]}"
        )
    return "\n".join(lines)[:1800]
