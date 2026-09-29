from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .db import connect, get_meta
from .world import format_sim_time

HABIT_MIN_SUPPORT = 3
HABIT_MIN_DISTINCT_DAYS = 2
HABIT_RECENT_WINDOW = 5
CUSTOM_MIN_EVIDENCE = 3
CUSTOM_MIN_DISTINCT_ACTORS = 2
CUSTOM_MIN_DISTINCT_DAYS = 2
PLACE_MIN_EVIDENCE = 2
PLACE_MAX_EVENTS = 8

FORCED_ACTION_KEYS = {
    "wait",
    "recharge",
    "charge",
    "travel",
    "service_chassis",
    "replace_battery",
    "service_equipment",
    "service_structure",
}

TRANSMISSION_MODES = {
    "observed",
    "heard",
    "participated",
}


def ensure_pattern_memory_schema_in_conn(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS memory_pattern_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id TEXT NOT NULL,
            sim_minute INTEGER NOT NULL,
            evidence_kind TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            source_role TEXT NOT NULL DEFAULT '',
            action_key TEXT NOT NULL DEFAULT '',
            context_key TEXT NOT NULL DEFAULT '',
            location_id TEXT NOT NULL DEFAULT '',
            actor_id TEXT NOT NULL DEFAULT '',
            transmission_mode TEXT NOT NULL DEFAULT '',
            verification_state TEXT NOT NULL DEFAULT 'verified',
            summary TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            UNIQUE(
                owner_id, evidence_kind, source_type, source_id, source_role,
                action_key, context_key, location_id, actor_id, transmission_mode
            )
        );

        CREATE INDEX IF NOT EXISTS idx_pattern_evidence_owner_kind
        ON memory_pattern_evidence(owner_id, evidence_kind, sim_minute, id);

        CREATE INDEX IF NOT EXISTS idx_pattern_evidence_context
        ON memory_pattern_evidence(owner_id, context_key, action_key, sim_minute, id);

        CREATE INDEX IF NOT EXISTS idx_pattern_evidence_place
        ON memory_pattern_evidence(owner_id, location_id, sim_minute, id);
        """
    )


def ensure_pattern_memory_schema() -> None:
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        conn.commit()


def _clean(value: Any, max_len: int = 180) -> str:
    return " ".join(str(value or "").split()).strip()[:max_len]


def _insert_evidence(
    conn,
    *,
    owner_id: str,
    sim_minute: int,
    evidence_kind: str,
    source_type: str,
    source_id: int,
    source_role: str = "",
    action_key: str = "",
    context_key: str = "",
    location_id: str = "",
    actor_id: str = "",
    transmission_mode: str = "",
    verification_state: str = "verified",
    summary: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO memory_pattern_evidence(
            owner_id, sim_minute, evidence_kind,
            source_type, source_id, source_role,
            action_key, context_key, location_id,
            actor_id, transmission_mode, verification_state,
            summary, metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            owner_id,
            int(sim_minute),
            evidence_kind,
            source_type,
            int(source_id),
            source_role,
            action_key,
            context_key,
            location_id,
            actor_id,
            transmission_mode,
            verification_state,
            _clean(summary, 1200),
            json.dumps(metadata or {}, sort_keys=True, separators=(",", ":")),
        ),
    )
    if cur.rowcount:
        return int(cur.lastrowid)

    row = conn.execute(
        """
        SELECT id
        FROM memory_pattern_evidence
        WHERE owner_id = ?
          AND evidence_kind = ?
          AND source_type = ?
          AND source_id = ?
          AND source_role = ?
          AND action_key = ?
          AND context_key = ?
          AND location_id = ?
          AND actor_id = ?
          AND transmission_mode = ?
        LIMIT 1
        """,
        (
            owner_id,
            evidence_kind,
            source_type,
            int(source_id),
            source_role,
            action_key,
            context_key,
            location_id,
            actor_id,
            transmission_mode,
        ),
    ).fetchone()
    return int(row["id"])


def _job_row(conn, job_id: int):
    return conn.execute(
        """
        SELECT id, citizen_id, action, target, status, outcome,
               end_minute, intent_reason, plan_id
        FROM jobs
        WHERE id = ?
        """,
        (int(job_id),),
    ).fetchone()


def record_voluntary_choice_evidence(
    owner_id: str,
    job_id: int,
    *,
    action_key: str,
    context_key: str,
    location_id: str | None = None,
    summary: str | None = None,
) -> int | None:
    """
    Record one Simulation-classified voluntary choice as pattern evidence.

    The caller is expected to be Simulation/planner integration code that has
    already classified the choice as voluntary. Memory still validates that the
    job belongs to the citizen, is terminal, has a recorded decision reason, and
    is not one of the known forced/survival maintenance actions.
    """
    action = _clean(action_key, 120)
    context = _clean(context_key, 180)
    location = _clean(location_id, 120)
    if not action or not context or action in FORCED_ACTION_KEYS:
        return None

    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        job = _job_row(conn, int(job_id))
        if not job or str(job["citizen_id"]) != str(owner_id):
            return None
        if str(job["status"]) not in {"complete", "failed"}:
            return None
        if not _clean(job["intent_reason"], 500):
            return None
        if str(job["action"]) in FORCED_ACTION_KEYS:
            return None
        if action != str(job["action"]):
            return None

        minute = int(job["end_minute"])
        evidence_id = _insert_evidence(
            conn,
            owner_id=str(owner_id),
            sim_minute=minute,
            evidence_kind="voluntary_choice",
            source_type="job",
            source_id=int(job_id),
            source_role="actor",
            action_key=action,
            context_key=context,
            location_id=location,
            summary=summary or (
                f"Chose {action} in context {context}; "
                f"job #{int(job_id)} ended {job['status']} with outcome {job['outcome']}."
            ),
            metadata={
                "job_status": str(job["status"]),
                "outcome": str(job["outcome"] or ""),
                "plan_id": int(job["plan_id"]) if job["plan_id"] is not None else None,
            },
        )
        conn.commit()
        return evidence_id


def record_social_pattern_evidence(
    memory_event_id: int,
    *,
    pattern_key: str,
    actor_id: str,
    transmission_mode: str,
    context_key: str = "",
) -> int | None:
    """
    Mark a real owner-scoped Memory event as evidence that a social pattern was
    observed/heard/participated in.

    This function never creates the source memory. Communication/Simulation must
    first establish the legitimate information path.
    """
    pattern = _clean(pattern_key, 180)
    actor = _clean(actor_id, 120)
    mode = _clean(transmission_mode, 40)
    context = _clean(context_key, 180)
    if not pattern or not actor or mode not in TRANSMISSION_MODES:
        return None

    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        row = conn.execute(
            """
            SELECT id, owner_id, sim_minute, source_type, source_id,
                   source_role, summary, status, metadata_json
            FROM memory_events
            WHERE id = ?
            """,
            (int(memory_event_id),),
        ).fetchone()
        if not row:
            return None

        try:
            metadata = json.loads(str(row["metadata_json"] or "{}"))
            if not isinstance(metadata, dict):
                metadata = {}
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        verification = str(
            metadata.get("verification")
            or ("verified" if str(row["status"]) == "verified" else "unverified")
        )
        evidence_id = _insert_evidence(
            conn,
            owner_id=str(row["owner_id"]),
            sim_minute=int(row["sim_minute"]),
            evidence_kind="social_transmission",
            source_type="memory_event",
            source_id=int(row["id"]),
            source_role=str(row["source_role"] or ""),
            action_key=pattern,
            context_key=context,
            actor_id=actor,
            transmission_mode=mode,
            verification_state=verification,
            summary=str(row["summary"]),
            metadata={
                "underlying_source_type": str(row["source_type"]),
                "underlying_source_id": int(row["source_id"]),
            },
        )
        conn.commit()
        return evidence_id


def _prune_orphan_evidence_in_conn(conn) -> None:
    rows = conn.execute(
        """
        SELECT id, owner_id, source_type, source_id
        FROM memory_pattern_evidence
        ORDER BY id
        """
    ).fetchall()
    stale: list[int] = []
    for row in rows:
        source_type = str(row["source_type"])
        source_id = int(row["source_id"])
        owner_id = str(row["owner_id"])

        if source_type == "job":
            valid = conn.execute(
                "SELECT 1 FROM jobs WHERE id = ? AND citizen_id = ?",
                (source_id, owner_id),
            ).fetchone()
        elif source_type == "memory_event":
            valid = conn.execute(
                "SELECT 1 FROM memory_events WHERE id = ? AND owner_id = ?",
                (source_id, owner_id),
            ).fetchone()
        else:
            valid = None

        if not valid:
            stale.append(int(row["id"]))

    for evidence_id in stale:
        conn.execute(
            "DELETE FROM memory_pattern_evidence WHERE id = ?",
            (evidence_id,),
        )


def prune_orphan_pattern_evidence() -> None:
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        _prune_orphan_evidence_in_conn(conn)
        conn.commit()


def _evidence_rows(conn, owner_id: str, kind: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT *
        FROM memory_pattern_evidence
        WHERE owner_id = ? AND evidence_kind = ?
        ORDER BY sim_minute, id
        """,
        (owner_id, kind),
    ).fetchall()
    return [dict(row) for row in rows]


def habit_candidates_for(
    owner_id: str,
    *,
    now_minute: int | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """
    Compute score-free habit candidates from explicit voluntary-choice evidence.

    Historical support is never deleted. Recent contrary choices in the same
    context can move a candidate from current -> mixed -> fading.
    """
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        _prune_orphan_evidence_in_conn(conn)
        rows = _evidence_rows(conn, owner_id, "voluntary_choice")
        now = (
            int(now_minute)
            if now_minute is not None
            else int(get_meta(conn, "sim_minute") or "360")
        )
        conn.commit()

    by_context: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_context[str(row["context_key"])].append(row)

    candidates: list[dict[str, Any]] = []
    for context_key, choices in by_context.items():
        choices.sort(key=lambda item: (int(item["sim_minute"]), int(item["id"])))
        by_action: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in choices:
            by_action[str(row["action_key"])].append(row)

        recent = choices[-HABIT_RECENT_WINDOW:]
        recent3 = choices[-3:]

        for action_key, support in by_action.items():
            days = {int(row["sim_minute"]) // 1440 for row in support}
            if len(support) < HABIT_MIN_SUPPORT or len(days) < HABIT_MIN_DISTINCT_DAYS:
                continue

            recent_support = sum(1 for row in recent if row["action_key"] == action_key)
            recent3_support = sum(1 for row in recent3 if row["action_key"] == action_key)
            if len(recent3) >= 3 and recent3_support >= 2:
                state = "current"
            elif recent_support >= 2:
                state = "mixed"
            else:
                state = "fading"

            contrary = [
                row for row in reversed(recent)
                if row["action_key"] != action_key
            ][:3]

            candidates.append({
                "owner_id": owner_id,
                "action_key": action_key,
                "context_key": context_key,
                "state": state,
                "support_count": len(support),
                "distinct_days": len(days),
                "latest_support_minute": int(support[-1]["sim_minute"]),
                "latest_support_label": format_sim_time(int(support[-1]["sim_minute"])),
                "age_minutes": max(0, now - int(support[-1]["sim_minute"])),
                "support_sources": [
                    {"type": row["source_type"], "id": int(row["source_id"])}
                    for row in support[-6:]
                ],
                "recent_contrary_sources": [
                    {
                        "type": row["source_type"],
                        "id": int(row["source_id"]),
                        "action_key": str(row["action_key"]),
                    }
                    for row in contrary
                ],
            })

    candidates.sort(
        key=lambda item: (
            {"current": 0, "mixed": 1, "fading": 2}[item["state"]],
            -int(item["latest_support_minute"]),
            item["context_key"],
            item["action_key"],
        )
    )
    return candidates[: max(1, min(int(limit), 30))]


def _place_rows(conn, owner_id: str, location_id: str | None = None) -> list[dict[str, Any]]:
    params: list[Any] = [owner_id]
    extra = ""
    if location_id:
        extra = "AND mf.facet_value = ?"
        params.append(str(location_id))

    rows = conn.execute(
        f"""
        SELECT DISTINCT me.*
        FROM memory_events me
        JOIN memory_event_facets mf
          ON mf.owner_id = me.owner_id
         AND mf.memory_event_id = me.id
         AND mf.facet_kind IN ('location', 'place')
        WHERE me.owner_id = ?
          {extra}
        ORDER BY me.sim_minute, me.id
        """,
        tuple(params),
    ).fetchall()
    return [dict(row) for row in rows]


def place_continuity_for(
    owner_id: str,
    *,
    location_id: str | None = None,
    limit_places: int = 12,
) -> list[dict[str, Any]]:
    """
    Return citizen-specific place significance evidence, not favorites.

    A place becomes eligible after either:
    - at least two source-backed experiences from at least two event kinds, or
    - one unusually important retained event (importance >= 0.75).

    The result exposes evidence trails, not a preference score.
    """
    with connect() as conn:
        rows = _place_rows(conn, owner_id, location_id)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
            if not isinstance(metadata, dict):
                metadata = {}
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        candidate_locations: set[str] = set()
        for key in ("location_id", "place_id"):
            value = _clean(metadata.get(key), 120)
            if value:
                candidate_locations.add(value)

        if not candidate_locations:
            # Pull location facets directly when metadata does not carry them.
            # This keeps the read model source-linked without inventing place names.
            with connect() as conn:
                facets = conn.execute(
                    """
                    SELECT facet_value
                    FROM memory_event_facets
                    WHERE owner_id = ?
                      AND memory_event_id = ?
                      AND facet_kind IN ('location', 'place')
                    """,
                    (owner_id, int(row["id"])),
                ).fetchall()
            candidate_locations.update(str(f["facet_value"]) for f in facets)

        for place in candidate_locations:
            if location_id and place != str(location_id):
                continue
            grouped[place].append(row)

    result: list[dict[str, Any]] = []
    for place, events in grouped.items():
        events.sort(key=lambda item: (int(item["sim_minute"]), int(item["id"])))
        kinds = {str(item["event_kind"]) for item in events}
        qualifies = (
            (len(events) >= PLACE_MIN_EVIDENCE and len(kinds) >= 2)
            or any(float(item["importance"]) >= 0.75 for item in events)
        )
        if not qualifies:
            continue

        result.append({
            "owner_id": owner_id,
            "location_id": place,
            "evidence_count": len(events),
            "event_kinds": sorted(kinds),
            "latest_minute": int(events[-1]["sim_minute"]),
            "latest_label": format_sim_time(int(events[-1]["sim_minute"])),
            "evidence": [
                {
                    "memory_event_id": int(item["id"]),
                    "source_type": str(item["source_type"]),
                    "source_id": int(item["source_id"]),
                    "event_kind": str(item["event_kind"]),
                    "sim_minute": int(item["sim_minute"]),
                    "summary": str(item["summary"]),
                    "status": str(item["status"]),
                }
                for item in events[-PLACE_MAX_EVENTS:]
            ],
        })

    result.sort(key=lambda item: (-int(item["latest_minute"]), item["location_id"]))
    return result[: max(1, min(int(limit_places), 30))]


def custom_candidates_for(
    owner_id: str,
    *,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """
    Return owner-perspective social custom candidates.

    A candidate requires:
    - at least 3 transmitted/observed/participated evidence events
    - at least 2 distinct actors
    - at least 2 distinct simulation days
    - at least one actor other than the observer

    One private citizen repeating something can never satisfy this.
    """
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        _prune_orphan_evidence_in_conn(conn)
        rows = _evidence_rows(conn, owner_id, "social_transmission")
        conn.commit()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["action_key"])].append(row)

    result: list[dict[str, Any]] = []
    for pattern_key, evidence in grouped.items():
        actors = {str(row["actor_id"]) for row in evidence if str(row["actor_id"])}
        days = {int(row["sim_minute"]) // 1440 for row in evidence}
        has_other_actor = any(actor != owner_id for actor in actors)
        if (
            len(evidence) < CUSTOM_MIN_EVIDENCE
            or len(actors) < CUSTOM_MIN_DISTINCT_ACTORS
            or len(days) < CUSTOM_MIN_DISTINCT_DAYS
            or not has_other_actor
        ):
            continue

        evidence.sort(key=lambda item: (int(item["sim_minute"]), int(item["id"])))
        result.append({
            "owner_id": owner_id,
            "pattern_key": pattern_key,
            "evidence_count": len(evidence),
            "distinct_actors": sorted(actors),
            "transmission_modes": sorted({
                str(row["transmission_mode"]) for row in evidence
            }),
            "verification_states": sorted({
                str(row["verification_state"]) for row in evidence
            }),
            "latest_minute": int(evidence[-1]["sim_minute"]),
            "latest_label": format_sim_time(int(evidence[-1]["sim_minute"])),
            "sources": [
                {
                    "type": str(row["source_type"]),
                    "id": int(row["source_id"]),
                    "actor_id": str(row["actor_id"]),
                    "mode": str(row["transmission_mode"]),
                    "verification": str(row["verification_state"]),
                }
                for row in evidence[-8:]
            ],
        })

    result.sort(key=lambda item: (-int(item["latest_minute"]), item["pattern_key"]))
    return result[: max(1, min(int(limit), 30))]


def continuity_pattern_snapshot(
    owner_id: str,
    *,
    location_id: str | None = None,
) -> dict[str, Any]:
    return {
        "citizen_id": owner_id,
        "habits": habit_candidates_for(owner_id),
        "places": place_continuity_for(owner_id, location_id=location_id),
        "customs": custom_candidates_for(owner_id),
        "semantics": {
            "habit_candidates_not_identity": True,
            "place_evidence_not_favorite": True,
            "customs_are_owner_perspective": True,
            "no_global_score": True,
            "source_events_remain_authoritative": True,
        },
    }
