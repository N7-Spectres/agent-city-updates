from __future__ import annotations

import json
from typing import Any

from .db import connect

SOURCE_TYPE = "simulation_practice_event"


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _memory_rows_for_owner(conn, owner_id: str) -> list[Any]:
    return conn.execute(
        """
        SELECT id, source_type, source_id, metadata_json
        FROM memory_events
        WHERE owner_id = ?
        ORDER BY id
        """,
        (owner_id,),
    ).fetchall()


def _same_job_memory_ids(conn, owner_id: str, job_id: int) -> list[int]:
    """
    Find durable memories that already represent this physical job.

    If a maintenance/spatial/discovery/shared event already retained the same
    job, practice evidence should reinforce/link that memory instead of creating
    a second autobiographical copy.
    """
    result: list[int] = []
    for row in _memory_rows_for_owner(conn, owner_id):
        if str(row["source_type"]) == "job" and int(row["source_id"]) == int(job_id):
            result.append(int(row["id"]))
            continue

        try:
            metadata = json.loads(str(row["metadata_json"] or "{}"))
            if not isinstance(metadata, dict):
                continue
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

        for key in ("job_id", "source_job_id", "citizen_job_id"):
            value = metadata.get(key)
            try:
                if value is not None and int(value) == int(job_id):
                    result.append(int(row["id"]))
                    break
            except (TypeError, ValueError):
                pass

    return sorted(set(result))


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


def _stage2_job_links(conn, job_id: int) -> tuple[str | None, int | None]:
    columns = {
        str(row["name"])
        for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
    }
    if "competence_family" not in columns and "guidance_session_id" not in columns:
        return None, None

    select = []
    if "competence_family" in columns:
        select.append("competence_family")
    if "guidance_session_id" in columns:
        select.append("guidance_session_id")
    row = conn.execute(
        f"SELECT {', '.join(select)} FROM jobs WHERE id = ?",
        (int(job_id),),
    ).fetchone()
    if not row:
        return None, None

    family = (
        str(row["competence_family"]).strip()
        if "competence_family" in columns and row["competence_family"] is not None
        else None
    )
    guidance_id = (
        int(row["guidance_session_id"])
        if "guidance_session_id" in columns and row["guidance_session_id"] is not None
        else None
    )
    return family or None, guidance_id


def _link_practice_facets(conn, memory_event_id: int, practice) -> None:
    owner_id = str(practice["citizen_id"])
    _insert_facet(conn, owner_id, memory_event_id, "practice_event", int(practice["id"]))
    _insert_facet(conn, owner_id, memory_event_id, "activity", practice["activity_type"])
    _insert_facet(conn, owner_id, memory_event_id, "location", practice["location_id"])
    _insert_facet(conn, owner_id, memory_event_id, "material", practice["material"])
    if practice["target"] is not None:
        _insert_facet(conn, owner_id, memory_event_id, "target", str(practice["target"]))
    if practice["plan_id"] is not None:
        _insert_facet(conn, owner_id, memory_event_id, "plan", str(int(practice["plan_id"])))

    family, guidance_session_id = _stage2_job_links(conn, int(practice["job_id"]))
    if family:
        _insert_facet(conn, owner_id, memory_event_id, "competence_family", family)
    if guidance_session_id is not None:
        _insert_facet(
            conn,
            owner_id,
            memory_event_id,
            "guided_practice_session",
            guidance_session_id,
        )


def _practice_importance(practice) -> float:
    status = str(practice["job_status"] or "")
    outcome = str(practice["outcome"] or "")
    if status == "failed" or outcome in {"failed", "no_yield"}:
        return 0.66
    return 0.58


def _insert_practice_memory(conn, practice) -> int:
    owner_id = str(practice["citizen_id"])
    activity = str(practice["activity_type"] or "physical_work")
    metadata = {
        "verification": "verified",
        "channel": "personal_experience",
        "practice_event_id": int(practice["id"]),
        "job_id": int(practice["job_id"]),
        "plan_id": int(practice["plan_id"]) if practice["plan_id"] is not None else None,
        "activity_type": activity,
        "job_status": str(practice["job_status"]),
        "outcome": str(practice["outcome"]),
        "location_id": practice["location_id"],
        "target": practice["target"],
        "material": practice["material"],
        "project_id": int(practice["project_id"]) if practice["project_id"] is not None else None,
        "observation_id": int(practice["observation_id"]) if practice["observation_id"] is not None else None,
        "shared_activity_id": int(practice["shared_activity_id"]) if practice["shared_activity_id"] is not None else None,
    }
    summary = " ".join(str(practice["summary"] or "").split()).strip()
    if not summary:
        summary = (
            f"{activity} job #{int(practice['job_id'])} ended "
            f"with outcome {practice['outcome']}."
        )

    cur = conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status, metadata_json
        )
        VALUES (?, ?, ?, NULL, ?, ?, 'actor',
                ?, ?, 'verified', ?)
        """,
        (
            owner_id,
            int(practice["completed_minute"]),
            f"practice_{activity}"[:80],
            SOURCE_TYPE,
            int(practice["id"]),
            summary[:1200],
            _practice_importance(practice),
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ),
    )
    if cur.rowcount:
        return int(cur.lastrowid)

    row = conn.execute(
        """
        SELECT id FROM memory_events
        WHERE owner_id = ?
          AND source_type = ?
          AND source_id = ?
          AND event_kind = ?
          AND source_role = 'actor'
        LIMIT 1
        """,
        (owner_id, SOURCE_TYPE, int(practice["id"]), f"practice_{activity}"[:80]),
    ).fetchone()
    return int(row["id"])


def sync_practice_memory_in_conn(conn) -> None:
    """
    Project canonical Simulation practice evidence into personal Memory.

    Existing durable memories for the same physical job are reused and linked.
    Only otherwise-unremembered physical practice receives a new Memory event.
    """
    if not _table_exists(conn, "practice_events"):
        return
    if not _table_exists(conn, "memory_event_facets"):
        return

    rows = conn.execute(
        """
        SELECT id, citizen_id, job_id, plan_id, activity_type,
               job_status, outcome, completed_minute, location_id,
               target, material, project_id, observation_id,
               shared_activity_id, summary
        FROM practice_events
        ORDER BY id
        """
    ).fetchall()

    for practice in rows:
        owner_id = str(practice["citizen_id"])
        if not conn.execute("SELECT 1 FROM citizens WHERE id = ?", (owner_id,)).fetchone():
            continue

        already = conn.execute(
            """
            SELECT memory_event_id
            FROM memory_event_facets
            WHERE owner_id = ?
              AND facet_kind = 'practice_event'
              AND facet_value = ?
            """,
            (owner_id, str(int(practice["id"]))),
        ).fetchall()
        if already:
            continue

        memory_ids = _same_job_memory_ids(conn, owner_id, int(practice["job_id"]))
        if not memory_ids:
            memory_ids = [_insert_practice_memory(conn, practice)]

        for memory_id in memory_ids:
            _link_practice_facets(conn, memory_id, practice)


def sync_practice_memory() -> None:
    from .causal_memory import ensure_causal_memory_schema_in_conn

    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        sync_practice_memory_in_conn(conn)
        ensure_causal_memory_schema_in_conn(conn)
        conn.commit()



def practice_recall_snapshot_for(
    citizen_id: str,
    *,
    activity: str | None = None,
    family: str | None = None,
    now_minute: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Return bounded actively recalled physical practice for one citizen.

    This is the model-facing bridge for self-assessment/teaching. It preserves
    Memory aging/salience instead of exposing the full Simulation practice ledger.
    """
    from .causal_memory import causal_recall_snapshot

    sync_practice_memory()
    filters = (
        {"competence_family": family}
        if family
        else {"activity": activity} if activity else None
    )
    recalled = causal_recall_snapshot(
        citizen_id,
        now_minute=now_minute,
        facet_filters=filters,
        required_facet_kind="practice_event",
        limit=max(1, min(int(limit) * 3, 24)),
    )

    result: list[dict[str, Any]] = []
    seen_practice_ids: set[str] = set()
    for item in recalled:
        practice_ids = [
            str(facet["value"])
            for facet in item.get("facets") or []
            if str(facet.get("kind")) == "practice_event"
        ]
        if not practice_ids:
            continue

        fresh_ids = [pid for pid in practice_ids if pid not in seen_practice_ids]
        if not fresh_ids:
            continue
        seen_practice_ids.update(fresh_ids)

        if activity is not None and not any(
            str(facet.get("kind")) == "activity"
            and str(facet.get("value")) == str(activity)
            for facet in item.get("facets") or []
        ):
            continue

        clean = dict(item)
        clean["practice_event_ids"] = fresh_ids
        # Internal ranking machinery is intentionally omitted from this surface.
        clean.pop("recall_score", None)
        clean.pop("reinforcement_count", None)
        clean.pop("matching_facets", None)
        result.append(clean)
        if len(result) >= max(1, min(int(limit), 16)):
            break

    return result


def practice_recall_context_for(
    citizen_id: str,
    *,
    activity: str | None = None,
    family: str | None = None,
    now_minute: int | None = None,
    limit: int = 6,
) -> str:
    memories = practice_recall_snapshot_for(
        citizen_id,
        activity=activity,
        family=family,
        now_minute=now_minute,
        limit=limit,
    )
    if not memories:
        return "- no actively recalled source-backed physical practice matching this subject"

    lines: list[str] = []
    for item in memories:
        truth = "Verified" if item.get("verification") == "verified" else "Remembered/claim"
        lines.append(
            f"- {truth}, {item.get('sim_label')} "
            f"({item.get('source_type')} #{item.get('source_id')}): "
            f"{' '.join(str(item.get('summary') or '').split())[:360]}"
        )
    return "\n".join(lines)[:1800]
