from __future__ import annotations

import json
import math
from collections import defaultdict
from typing import Any, Iterable

from .db import connect, get_meta
from .world import format_sim_time

MAX_RECALL_ITEMS = 8
MAX_RECALL_CONTEXT_CHARS = 2400
MAX_RECALL_CANDIDATES = 240

# Facets that can legitimately reinforce retrieval when repeated.
# Generic storage categories such as source_type/event_kind are useful filters
# but should not make every conversation or every observation reinforce every
# other one.
REINFORCING_FACET_KINDS = {
    "counterparty",
    "visitor",
    "subject",
    "target",
    "location",
    "material",
    "process",
    "activity",
    "plan",
    "place",
}


def ensure_causal_memory_schema_in_conn(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS memory_event_facets (
            owner_id TEXT NOT NULL,
            memory_event_id INTEGER NOT NULL,
            facet_kind TEXT NOT NULL,
            facet_value TEXT NOT NULL,
            PRIMARY KEY(owner_id, memory_event_id, facet_kind, facet_value)
        );

        CREATE INDEX IF NOT EXISTS idx_memory_facets_lookup
        ON memory_event_facets(owner_id, facet_kind, facet_value, memory_event_id);

        CREATE INDEX IF NOT EXISTS idx_memory_facets_event
        ON memory_event_facets(memory_event_id, facet_kind, facet_value);
        """
    )
    _sync_memory_facets_in_conn(conn)


def ensure_causal_memory_schema() -> None:
    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        conn.commit()


def _clean(value: Any, max_len: int = 180) -> str | None:
    text = " ".join(str(value or "").split()).strip()
    return text[:max_len] if text else None


def _facet_pairs(row: Any) -> set[tuple[str, str]]:
    facets: set[tuple[str, str]] = set()

    event_kind = _clean(row["event_kind"], 80)
    source_type = _clean(row["source_type"], 80)
    counterparty = _clean(row["counterparty_id"], 120)
    if event_kind:
        facets.add(("event_kind", event_kind))
    if source_type:
        facets.add(("source_type", source_type))
    if counterparty:
        facets.add(("counterparty", counterparty))

    try:
        metadata = json.loads(str(row["metadata_json"] or "{}"))
        if not isinstance(metadata, dict):
            metadata = {}
    except (TypeError, ValueError, json.JSONDecodeError):
        metadata = {}

    direct = {
        "location": metadata.get("location_id"),
        "material": metadata.get("material"),
        "process": metadata.get("process"),
        "visitor": metadata.get("visitor"),
        "plan": metadata.get("plan_id"),
        "place": metadata.get("place_id"),
    }
    for kind, value in direct.items():
        clean = _clean(value)
        if clean:
            facets.add((kind, clean))

    subject_type = _clean(metadata.get("subject_type"), 80)
    subject_id = _clean(metadata.get("subject_id"), 160)
    if subject_type and subject_id:
        facets.add(("subject", f"{subject_type}:{subject_id}"))
    elif subject_id:
        facets.add(("subject", subject_id))

    target_type = _clean(metadata.get("target_type"), 80)
    target_id = _clean(metadata.get("target_id"), 160)
    if target_type and target_id:
        facets.add(("target", f"{target_type}:{target_id}"))
    elif target_id:
        facets.add(("target", target_id))

    # Activity is deliberately descriptive, not an identity/class label.
    for key in (
        "activity_type",
        "event_type",
        "observation_kind",
        "discovery_kind",
        "action",
    ):
        value = _clean(metadata.get(key), 120)
        if value:
            facets.add(("activity", value))

    return facets


def _sync_memory_facets_in_conn(conn) -> None:
    rows = conn.execute(
        """
        SELECT me.id, me.owner_id, me.event_kind, me.counterparty_id,
               me.source_type, me.metadata_json
        FROM memory_events me
        WHERE NOT EXISTS (
            SELECT 1
            FROM memory_event_facets mf
            WHERE mf.owner_id = me.owner_id
              AND mf.memory_event_id = me.id
              AND mf.facet_kind = 'event_kind'
        )
        ORDER BY me.id
        """
    ).fetchall()

    for row in rows:
        for kind, value in _facet_pairs(row):
            conn.execute(
                """
                INSERT OR IGNORE INTO memory_event_facets(
                    owner_id, memory_event_id, facet_kind, facet_value
                )
                VALUES (?, ?, ?, ?)
                """,
                (str(row["owner_id"]), int(row["id"]), kind, value),
            )


def sync_memory_facets() -> None:
    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        conn.commit()


def link_memory_event(memory_event_id: int, facet_kind: str, facet_value: str) -> bool:
    """
    Explicitly add a source-safe continuity facet to an existing memory event.

    Intended future use includes linking one or more real memories to a
    persistent plan ID. This does not alter the underlying event or invent a
    memory.
    """
    kind = _clean(facet_kind, 80)
    value = _clean(facet_value, 180)
    if not kind or not value:
        return False

    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        row = conn.execute(
            "SELECT owner_id FROM memory_events WHERE id = ?",
            (int(memory_event_id),),
        ).fetchone()
        if not row:
            return False
        conn.execute(
            """
            INSERT OR IGNORE INTO memory_event_facets(
                owner_id, memory_event_id, facet_kind, facet_value
            )
            VALUES (?, ?, ?, ?)
            """,
            (str(row["owner_id"]), int(memory_event_id), kind, value),
        )
        conn.commit()
        return True


def _normalize_filters(
    facet_filters: dict[str, str | Iterable[str]] | None,
) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if not facet_filters:
        return result
    for raw_kind, raw_values in facet_filters.items():
        kind = _clean(raw_kind, 80)
        if not kind:
            continue
        if isinstance(raw_values, str):
            values = [raw_values]
        else:
            values = list(raw_values)
        for raw_value in values:
            value = _clean(raw_value, 180)
            if value:
                result.append((kind, value))
    return result


def _candidate_rows(
    conn,
    owner_id: str,
    filters: list[tuple[str, str]],
    pinned_ids: list[int],
    required_facet_kind: str | None = None,
) -> list[dict[str, Any]]:
    rows_by_id: dict[int, dict[str, Any]] = {}

    required_kind = _clean(required_facet_kind, 80) if required_facet_kind else None

    if filters:
        conditions = " OR ".join("(mf.facet_kind = ? AND mf.facet_value = ?)" for _ in filters)
        params: list[Any] = [owner_id]
        for kind, value in filters:
            params.extend([kind, value])
        required_clause = ""
        if required_kind:
            required_clause = """
              AND EXISTS (
                  SELECT 1
                  FROM memory_event_facets req
                  WHERE req.owner_id = me.owner_id
                    AND req.memory_event_id = me.id
                    AND req.facet_kind = ?
              )
            """
            params.append(required_kind)
        params.append(MAX_RECALL_CANDIDATES)
        rows = conn.execute(
            f"""
            SELECT DISTINCT me.*
            FROM memory_events me
            JOIN memory_event_facets mf
              ON mf.owner_id = me.owner_id
             AND mf.memory_event_id = me.id
            WHERE me.owner_id = ?
              AND ({conditions})
              {required_clause}
            ORDER BY me.importance DESC, me.sim_minute DESC, me.id DESC
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()
    elif required_kind:
        rows = conn.execute(
            """
            SELECT DISTINCT me.*
            FROM memory_events me
            JOIN memory_event_facets req
              ON req.owner_id = me.owner_id
             AND req.memory_event_id = me.id
             AND req.facet_kind = ?
            WHERE me.owner_id = ?
            ORDER BY me.importance DESC, me.sim_minute DESC, me.id DESC
            LIMIT ?
            """,
            (required_kind, owner_id, MAX_RECALL_CANDIDATES),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT *
            FROM memory_events
            WHERE owner_id = ?
            ORDER BY importance DESC, sim_minute DESC, id DESC
            LIMIT ?
            """,
            (owner_id, MAX_RECALL_CANDIDATES),
        ).fetchall()

    for row in rows:
        rows_by_id[int(row["id"])] = dict(row)

    if pinned_ids:
        placeholders = ",".join("?" for _ in pinned_ids)
        pinned_rows = conn.execute(
            f"""
            SELECT *
            FROM memory_events
            WHERE owner_id = ? AND id IN ({placeholders})
            """,
            (owner_id, *pinned_ids),
        ).fetchall()
        for row in pinned_rows:
            rows_by_id[int(row["id"])] = dict(row)

    return list(rows_by_id.values())


def _facets_for_events(conn, owner_id: str, event_ids: list[int]) -> dict[int, list[dict[str, str]]]:
    if not event_ids:
        return {}
    placeholders = ",".join("?" for _ in event_ids)
    rows = conn.execute(
        f"""
        SELECT memory_event_id, facet_kind, facet_value
        FROM memory_event_facets
        WHERE owner_id = ?
          AND memory_event_id IN ({placeholders})
        ORDER BY memory_event_id, facet_kind, facet_value
        """,
        (owner_id, *event_ids),
    ).fetchall()
    result: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        result[int(row["memory_event_id"])].append(
            {"kind": str(row["facet_kind"]), "value": str(row["facet_value"])}
        )
    return dict(result)


def _reinforcement_counts(
    conn,
    owner_id: str,
    event_facets: dict[int, list[dict[str, str]]],
) -> dict[int, int]:
    relevant_pairs = {
        (facet["kind"], facet["value"])
        for facets in event_facets.values()
        for facet in facets
        if facet["kind"] in REINFORCING_FACET_KINDS
    }
    if not relevant_pairs:
        return {event_id: 1 for event_id in event_facets}

    counts: dict[tuple[str, str], int] = {}
    for kind, value in relevant_pairs:
        row = conn.execute(
            """
            SELECT COUNT(DISTINCT memory_event_id) AS n
            FROM memory_event_facets
            WHERE owner_id = ? AND facet_kind = ? AND facet_value = ?
            """,
            (owner_id, kind, value),
        ).fetchone()
        counts[(kind, value)] = int(row["n"] or 0)

    result: dict[int, int] = {}
    for event_id, facets in event_facets.items():
        related = [
            counts.get((facet["kind"], facet["value"]), 1)
            for facet in facets
            if facet["kind"] in REINFORCING_FACET_KINDS
        ]
        result[event_id] = max(related, default=1)
    return result


def _recall_score(
    *,
    importance: float,
    age_minutes: int,
    reinforcement_count: int,
    pinned: bool,
) -> float:
    age_days = max(0.0, float(age_minutes) / 1440.0)
    recency = 1.0 / (1.0 + age_days / 14.0)
    reinforcement = min(0.20, 0.04 * max(0, int(reinforcement_count) - 1))
    score = 0.55 * max(0.0, min(1.0, float(importance))) + 0.25 * recency + reinforcement
    if pinned:
        score += 1.0
    return round(score, 6)


def causal_recall_snapshot(
    owner_id: str,
    *,
    now_minute: int | None = None,
    facet_filters: dict[str, str | Iterable[str]] | None = None,
    pinned_event_ids: Iterable[int] | None = None,
    required_facet_kind: str | None = None,
    limit: int = MAX_RECALL_ITEMS,
) -> list[dict[str, Any]]:
    """
    Return a bounded active-recall packet from the durable archive.

    - filters are relevance hints and match ANY supplied facet
    - pinned event IDs are guaranteed candidate inclusion for unfinished plans
    - reinforcement affects retrieval priority only, never truth/verification
    - aging reduces priority but never edits/deletes the durable event
    """
    safe_limit = max(1, min(int(limit), 24))
    filters = _normalize_filters(facet_filters)
    pinned_ids = sorted({int(v) for v in (pinned_event_ids or []) if int(v) > 0})

    with connect() as conn:
        ensure_causal_memory_schema_in_conn(conn)
        now = (
            int(now_minute)
            if now_minute is not None
            else int(get_meta(conn, "sim_minute") or "360")
        )
        rows = _candidate_rows(
            conn,
            owner_id,
            filters,
            pinned_ids,
            required_facet_kind=required_facet_kind,
        )
        ids = [int(row["id"]) for row in rows]
        facets = _facets_for_events(conn, owner_id, ids)
        reinforcement = _reinforcement_counts(conn, owner_id, facets)

    result: list[dict[str, Any]] = []
    filter_set = set(filters)
    pinned_set = set(pinned_ids)

    for row in rows:
        event_id = int(row["id"])
        event_facets = facets.get(event_id, [])
        matching = [
            facet for facet in event_facets
            if (facet["kind"], facet["value"]) in filter_set
        ]
        age_minutes = max(0, now - int(row["sim_minute"]))
        pinned = event_id in pinned_set
        score = _recall_score(
            importance=float(row["importance"]),
            age_minutes=age_minutes,
            reinforcement_count=reinforcement.get(event_id, 1),
            pinned=pinned,
        )

        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
            if not isinstance(metadata, dict):
                metadata = {}
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        result.append({
            "memory_event_id": event_id,
            "owner_id": str(row["owner_id"]),
            "sim_minute": int(row["sim_minute"]),
            "sim_label": format_sim_time(int(row["sim_minute"])),
            "age_minutes": age_minutes,
            "event_kind": str(row["event_kind"]),
            "counterparty_id": row["counterparty_id"],
            "source_type": str(row["source_type"]),
            "source_id": int(row["source_id"]),
            "source_role": str(row["source_role"]),
            "summary": str(row["summary"]),
            "importance": float(row["importance"]),
            "status": str(row["status"]),
            "verification": str(
                metadata.get("verification")
                or ("verified" if str(row["status"]) == "verified" else "unverified")
            ),
            "facets": event_facets,
            "matching_facets": matching,
            "reinforcement_count": reinforcement.get(event_id, 1),
            "recall_score": score,
            "pinned": pinned,
        })

    result.sort(
        key=lambda item: (
            0 if item["pinned"] else 1,
            -float(item["recall_score"]),
            -int(item["sim_minute"]),
            -int(item["memory_event_id"]),
        )
    )
    return result[:safe_limit]


def causal_recall_context_for(
    owner_id: str,
    *,
    now_minute: int | None = None,
    facet_filters: dict[str, str | Iterable[str]] | None = None,
    pinned_event_ids: Iterable[int] | None = None,
    required_facet_kind: str | None = None,
    limit: int = MAX_RECALL_ITEMS,
) -> str:
    memories = causal_recall_snapshot(
        owner_id,
        now_minute=now_minute,
        facet_filters=facet_filters,
        pinned_event_ids=pinned_event_ids,
        required_facet_kind=required_facet_kind,
        limit=limit,
    )
    if not memories:
        return "- no source-backed continuity memory matched this decision"

    parts: list[str] = []
    for memory in memories:
        truth_label = "Verified" if memory["verification"] == "verified" else "Remembered/claim"
        reinforcement = (
            f"; related experience x{memory['reinforcement_count']}"
            if int(memory["reinforcement_count"]) > 1
            else ""
        )
        pin = "; pinned by unfinished continuity" if memory["pinned"] else ""
        parts.append(
            f"- {truth_label}, {memory['sim_label']} "
            f"({memory['source_type']} #{memory['source_id']}{reinforcement}{pin}): "
            f"{' '.join(memory['summary'].split())[:420]}"
        )
        if sum(len(part) + 1 for part in parts) >= MAX_RECALL_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_RECALL_CONTEXT_CHARS]

UI_SAFE_FACET_KINDS = {
    "event_kind",
    "source_type",
    "counterparty",
    "visitor",
    "subject",
    "target",
    "location",
    "material",
    "process",
    "activity",
    "plan",
    "place",
}


def display_recall_snapshot(
    owner_id: str,
    *,
    plan_id: int | str | None = None,
    now_minute: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Return a bounded citizen-facing continuity projection.

    This is intentionally narrower than causal_recall_snapshot(). It exposes
    source-backed remembered perspective while withholding internal ranking,
    reinforcement, salience, and global aggregation machinery.
    """
    safe_limit = max(1, min(int(limit), 16))
    filters = {"plan": str(plan_id)} if plan_id is not None else None
    recalled = causal_recall_snapshot(
        owner_id,
        now_minute=now_minute,
        facet_filters=filters,
        limit=safe_limit,
    )

    result: list[dict[str, Any]] = []
    for item in recalled:
        safe_facets = [
            {"kind": str(facet["kind"]), "value": str(facet["value"])}
            for facet in (item.get("facets") or [])
            if str(facet.get("kind")) in UI_SAFE_FACET_KINDS
        ]
        linked_plan_ids = sorted({
            str(facet["value"])
            for facet in safe_facets
            if facet["kind"] == "plan"
        })

        result.append({
            "owner_id": str(item["owner_id"]),
            "memory_event_id": int(item["memory_event_id"]),
            "source_type": str(item["source_type"]),
            "source_id": int(item["source_id"]),
            "source_role": str(item["source_role"]),
            "event_kind": str(item["event_kind"]),
            "sim_minute": int(item["sim_minute"]),
            "sim_label": str(item["sim_label"]),
            "summary": str(item["summary"]),
            "verification": str(item["verification"]),
            "status": str(item["status"]),
            "pinned_by_plan": bool(linked_plan_ids),
            "plan_ids": linked_plan_ids,
            "facets": safe_facets,
        })

    return result

