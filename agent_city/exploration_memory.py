from __future__ import annotations

import json
from typing import Any

from .db import connect
from .world import format_sim_time

SOURCE_TYPE = "simulation_shared_activity"
MAX_SHARED_EXPLORATION_CONTEXT_CHARS = 1200
MAX_SHARED_EXPLORATION_EVENTS = 8


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _insert_shared_exploration_memory(conn, activity) -> None:
    citizen_id = str(activity["citizen_id"])
    visitor = str(activity["visitor"])
    objective = " ".join(str(activity["objective"] or "").split()).strip()
    activity_type = str(activity["activity_type"] or "shared_activity")
    observation_id = int(activity["observation_id"])
    source_visit_id = activity["source_visit_id"]
    source_exchange_id = activity["source_exchange_id"]
    citizen_job_id = activity["citizen_job_id"]

    summary = (
        f"Completed shared exploration with {visitor}: "
        f"{objective or activity_type}. "
        f"Validated spatial observation #{observation_id} was recorded."
    )

    metadata = {
        "verification": "verified",
        "channel": "shared_physical_activity",
        "visitor": visitor,
        "activity_type": activity_type,
        "objective": objective or None,
        "frame_id": str(activity["frame_id"]),
        "source_visit_id": source_visit_id,
        "source_exchange_id": source_exchange_id,
        "citizen_job_id": citizen_job_id,
        "observation_id": observation_id,
        "outcome": str(activity["outcome"]),
        "physical_status": str(activity["status"]),
    }

    conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status, metadata_json
        )
        VALUES (?, ?, 'shared_exploration', NULL, ?, ?, 'citizen_participant',
                ?, 0.78, 'verified', ?)
        """,
        (
            citizen_id,
            int(activity["completed_minute"]),
            SOURCE_TYPE,
            int(activity["id"]),
            summary[:1200],
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ),
    )


def sync_shared_exploration_in_conn(conn) -> None:
    """
    Project only successfully completed Simulation-owned shared activities.

    Proposal, acceptance and active states are intentionally ignored. The linked
    spatial observation keeps its own evidence identity in spatial memory.
    """
    if not _table_exists(conn, "shared_activities"):
        return

    rows = conn.execute(
        """
        SELECT id, visitor, citizen_id, activity_type, objective, frame_id,
               status, completed_minute, source_visit_id, source_exchange_id,
               citizen_job_id, observation_id, outcome
        FROM shared_activities
        WHERE status = 'complete'
          AND outcome = 'success'
          AND completed_minute IS NOT NULL
          AND observation_id IS NOT NULL
        ORDER BY id
        """
    ).fetchall()

    for activity in rows:
        citizen_id = str(activity["citizen_id"])
        if not conn.execute("SELECT 1 FROM citizens WHERE id = ?", (citizen_id,)).fetchone():
            continue
        _insert_shared_exploration_memory(conn, activity)


def sync_shared_exploration() -> None:
    with connect() as conn:
        sync_shared_exploration_in_conn(conn)
        conn.commit()


def _rows(citizen_id: str, limit: int = MAX_SHARED_EXPLORATION_EVENTS) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, sim_minute, event_kind, source_type, source_id,
                   source_role, summary, importance, status, metadata_json
            FROM memory_events
            WHERE owner_id = ? AND source_type = ?
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (citizen_id, SOURCE_TYPE, max(1, min(int(limit), 30))),
        ).fetchall()
        return [dict(row) for row in rows]


def shared_exploration_snapshot_for(
    citizen_id: str,
    *,
    visitor: str | None = None,
    limit: int = MAX_SHARED_EXPLORATION_EVENTS,
) -> list[dict[str, Any]]:
    sync_shared_exploration()

    result: list[dict[str, Any]] = []
    visitor_key = visitor.strip().casefold() if visitor else None
    for row in _rows(citizen_id, limit=max(limit * 3, limit)):
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        if visitor_key and str(metadata.get("visitor") or "").casefold() != visitor_key:
            continue

        item = dict(row)
        item["metadata"] = metadata
        item.pop("metadata_json", None)
        item["sim_label"] = format_sim_time(int(row["sim_minute"]))
        result.append(item)
        if len(result) >= max(1, limit):
            break
    return result


def shared_exploration_context_for(
    citizen_id: str,
    *,
    visitor: str | None = None,
    limit: int = 3,
) -> str:
    events = shared_exploration_snapshot_for(citizen_id, visitor=visitor, limit=limit)
    if not events:
        return "- no completed shared exploration memory with this visitor"

    parts: list[str] = []
    for event in reversed(events):
        meta = event["metadata"]
        parts.append(
            f"- {event['sim_label']}: {event['summary']} "
            f"[shared activity #{event['source_id']}; observation #{meta.get('observation_id')}]"
        )
        if sum(len(part) + 1 for part in parts) >= MAX_SHARED_EXPLORATION_CONTEXT_CHARS:
            break
    return "\n".join(parts)[:MAX_SHARED_EXPLORATION_CONTEXT_CHARS]
