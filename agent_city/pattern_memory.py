from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .db import connect, get_meta
from .world import format_sim_time

# Stage 3 is intentionally narrow. These actions are eligible only because they
# can represent repeated voluntary work/inspection choices. Constraint-driven
# travel, recharge, cargo shuttling, and maintenance are excluded from habit
# evidence.
VOLUNTARY_PATTERN_ACTIONS = {
    "survey",
    "extract",
    "experiment",
    "fabricate",
    "construct",
    "local_inspect",
    "shared_local_activity",
}

MIN_PATTERN_EVENTS = 3
MIN_PATTERN_SPAN_MINUTES = 120
RECENT_PATTERN_WINDOW_MINUTES = 2 * 1440

PATTERN_TRANSMISSION_SOURCE_TYPE = "pattern_transmission"


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def ensure_pattern_memory_schema_in_conn(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pattern_transmissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_id TEXT NOT NULL,
            source_actor_id TEXT NOT NULL,
            pattern_key TEXT NOT NULL,
            source_conversation_id INTEGER NOT NULL,
            sim_minute INTEGER NOT NULL,
            value_text TEXT NOT NULL,
            source_memory_event_ids_json TEXT NOT NULL DEFAULT '[]',
            verification TEXT NOT NULL DEFAULT 'unverified',
            UNIQUE(recipient_id, source_actor_id, pattern_key, source_conversation_id)
        );

        CREATE INDEX IF NOT EXISTS idx_pattern_transmissions_recipient
        ON pattern_transmissions(recipient_id, sim_minute DESC, id DESC);

        CREATE INDEX IF NOT EXISTS idx_pattern_transmissions_pattern
        ON pattern_transmissions(recipient_id, pattern_key, sim_minute DESC, id DESC);
        """
    )
    sync_pattern_transmission_memory_in_conn(conn)


def ensure_pattern_memory_schema() -> None:
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        conn.commit()


def _practice_rows_in_conn(conn, citizen_id: str) -> list[dict[str, Any]]:
    if not _table_exists(conn, "memory_event_facets"):
        return []

    rows = conn.execute(
        """
        SELECT DISTINCT
            me.id AS memory_event_id,
            p.completed_minute AS sim_minute,
            me.source_type,
            me.source_id,
            me.summary,
            p.activity_type AS activity,
            p.location_id AS location_id,
            p.id AS practice_event_id
        FROM memory_events me
        JOIN memory_event_facets pe
          ON pe.owner_id = me.owner_id
         AND pe.memory_event_id = me.id
         AND pe.facet_kind = 'practice_event'
        JOIN practice_events p
          ON p.citizen_id = me.owner_id
         AND CAST(p.id AS TEXT) = pe.facet_value
        WHERE me.owner_id = ?
        ORDER BY p.completed_minute, me.id
        """,
        (citizen_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _pattern_key(activity: str, location_id: str) -> str:
    return f"{activity}@{location_id}"


def _split_pattern_key(pattern_key: str) -> tuple[str, str] | None:
    if "@" not in pattern_key:
        return None
    activity, location_id = pattern_key.split("@", 1)
    activity = activity.strip()
    location_id = location_id.strip()
    if not activity or not location_id:
        return None
    return activity, location_id


def _behavior_patterns_in_conn(
    conn,
    citizen_id: str,
    *,
    now_minute: int,
) -> list[dict[str, Any]]:
    rows = _practice_rows_in_conn(conn, citizen_id)
    eligible = [
        row for row in rows
        if str(row.get("activity") or "") in VOLUNTARY_PATTERN_ACTIONS
        and str(row.get("location_id") or "").strip()
    ]

    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_activity_recent: dict[str, list[dict[str, Any]]] = defaultdict(list)

    recent_cutoff = int(now_minute) - RECENT_PATTERN_WINDOW_MINUTES
    for row in eligible:
        activity = str(row["activity"])
        location_id = str(row["location_id"])
        by_key[_pattern_key(activity, location_id)].append(row)
        if int(row["sim_minute"]) >= recent_cutoff:
            by_activity_recent[activity].append(row)

    result: list[dict[str, Any]] = []
    for key, events in by_key.items():
        # A reused memory event can carry several facets; count each source memory once.
        dedup: dict[int, dict[str, Any]] = {}
        for event in events:
            dedup[int(event["memory_event_id"])] = event
        events = sorted(dedup.values(), key=lambda r: (int(r["sim_minute"]), int(r["memory_event_id"])))

        if len(events) < MIN_PATTERN_EVENTS:
            continue
        first_minute = int(events[0]["sim_minute"])
        last_minute = int(events[-1]["sim_minute"])
        if last_minute - first_minute < MIN_PATTERN_SPAN_MINUTES:
            continue

        parsed = _split_pattern_key(key)
        if not parsed:
            continue
        activity, location_id = parsed

        recent_support = [
            row for row in events
            if int(row["sim_minute"]) >= recent_cutoff
        ]
        recent_competing = [
            row for row in by_activity_recent.get(activity, [])
            if str(row.get("location_id") or "") != location_id
        ]

        source_memory_ids = [int(row["memory_event_id"]) for row in events]
        practice_event_ids = sorted({
            int(row["practice_event_id"])
            for row in events
            if str(row.get("practice_event_id") or "").isdigit()
        })

        result.append({
            "pattern_key": key,
            "pattern_kind": "recurring_voluntary_activity",
            "activity": activity,
            "location_id": location_id,
            "event_count": len(events),
            "first_minute": first_minute,
            "first_label": format_sim_time(first_minute),
            "last_minute": last_minute,
            "last_label": format_sim_time(last_minute),
            "recent_support_count": len(recent_support),
            "recent_competing_count": len(recent_competing),
            "currently_supported": (
                len(recent_support) >= 2
                and len(recent_support) > len(recent_competing)
            ),
            "source_memory_event_ids": source_memory_ids,
            "source_practice_event_ids": practice_event_ids,
            "source_summaries": [
                " ".join(str(row.get("summary") or "").split())[:260]
                for row in events[-3:]
            ],
        })

    result.sort(
        key=lambda item: (
            0 if item["currently_supported"] else 1,
            -int(item["last_minute"]),
            item["pattern_key"],
        )
    )
    return result


def behavior_pattern_snapshot_for(
    citizen_id: str,
    *,
    now_minute: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    from .practice_memory import sync_practice_memory

    sync_practice_memory()
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        now = int(now_minute) if now_minute is not None else int(get_meta(conn, "sim_minute") or "360")
        rows = _behavior_patterns_in_conn(conn, citizen_id, now_minute=now)
        conn.commit()
    return rows[: max(1, min(int(limit), 24))]


def _location_memory_rows_in_conn(conn, citizen_id: str) -> list[dict[str, Any]]:
    if not _table_exists(conn, "memory_event_facets"):
        return []
    rows = conn.execute(
        """
        SELECT DISTINCT
            me.id AS memory_event_id,
            me.sim_minute,
            me.event_kind,
            me.source_type,
            me.source_id,
            me.counterparty_id,
            me.summary,
            me.status,
            loc.facet_value AS location_id
        FROM memory_events me
        JOIN memory_event_facets loc
          ON loc.owner_id = me.owner_id
         AND loc.memory_event_id = me.id
         AND loc.facet_kind IN ('location', 'place')
        WHERE me.owner_id = ?
        ORDER BY me.sim_minute, me.id
        """,
        (citizen_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def place_meaning_snapshot_for(
    citizen_id: str,
    *,
    place_id: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    from .memory import ensure_memory_schema

    ensure_memory_schema()
    with connect() as conn:
        rows = _location_memory_rows_in_conn(conn, citizen_id)

    grouped: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        location_id = str(row.get("location_id") or "").strip()
        if not location_id:
            continue
        if place_id is not None and location_id != str(place_id):
            continue
        grouped[location_id][int(row["memory_event_id"])] = row

    result: list[dict[str, Any]] = []
    for location_id, by_id in grouped.items():
        events = sorted(by_id.values(), key=lambda r: (int(r["sim_minute"]), int(r["memory_event_id"])))
        if len(events) < 2:
            continue
        first = events[0]
        last = events[-1]
        result.append({
            "location_id": location_id,
            "evidence_count": len(events),
            "first_minute": int(first["sim_minute"]),
            "first_label": format_sim_time(int(first["sim_minute"])),
            "last_minute": int(last["sim_minute"]),
            "last_label": format_sim_time(int(last["sim_minute"])),
            "source_memory_event_ids": [int(row["memory_event_id"]) for row in events],
            "source_types": sorted({str(row["source_type"]) for row in events}),
            "event_kinds": sorted({str(row["event_kind"]) for row in events}),
            "counterparty_ids": sorted({
                str(row["counterparty_id"])
                for row in events
                if row.get("counterparty_id")
            }),
            "recent_summaries": [
                " ".join(str(row.get("summary") or "").split())[:280]
                for row in events[-3:]
            ],
            "semantics": {
                "citizen_specific_meaning_evidence": True,
                "not_physical_location_truth": True,
                "not_a_favorite_place_label": True,
            },
        })

    result.sort(key=lambda item: (-int(item["last_minute"]), item["location_id"]))
    return result[: max(1, min(int(limit), 24))]


def _conversation_role_text(conversation, actor_id: str) -> str | None:
    if str(conversation["initiator_id"]) == actor_id:
        return " ".join(str(conversation["initiator_text"] or "").split())
    if str(conversation["target_id"]) == actor_id:
        return " ".join(str(conversation["target_text"] or "").split())
    return None


def record_pattern_transmission(
    *,
    source_conversation_id: int,
    source_actor_id: str,
    recipient_id: str,
    pattern_key: str,
    value_text: str,
) -> int | None:
    """
    Record that a source-backed recurring pattern was actually mentioned to one
    citizen in one durable face-to-face conversation.

    The transmission is an unverified social claim for the recipient. It does
    not create a habit or custom by itself.
    """
    pattern_key = str(pattern_key or "").strip()[:220]
    value_text = " ".join(str(value_text or "").split())[:1200]
    if not pattern_key or not value_text or source_actor_id == recipient_id:
        return None

    # Make sure the speaker's source-backed practice Memory is current before
    # validating that the claimed recurring pattern actually exists.
    from .practice_memory import sync_practice_memory
    sync_practice_memory()

    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        conversation = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id, initiator_text, target_text
            FROM citizen_conversations
            WHERE id = ?
            """,
            (int(source_conversation_id),),
        ).fetchone()
        if not conversation:
            return None

        participants = {str(conversation["initiator_id"]), str(conversation["target_id"])}
        if {source_actor_id, recipient_id} != participants:
            return None

        speaker_text = _conversation_role_text(conversation, source_actor_id)
        if not speaker_text or value_text.casefold() not in speaker_text.casefold():
            return None

        now = int(conversation["sim_minute"])
        source_patterns = {
            item["pattern_key"]: item
            for item in _behavior_patterns_in_conn(conn, source_actor_id, now_minute=now)
            if item["currently_supported"]
        }
        source_pattern = source_patterns.get(pattern_key)
        if not source_pattern:
            return None

        cur = conn.execute(
            """
            INSERT OR IGNORE INTO pattern_transmissions(
                recipient_id, source_actor_id, pattern_key,
                source_conversation_id, sim_minute, value_text,
                source_memory_event_ids_json, verification
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'unverified')
            """,
            (
                recipient_id,
                source_actor_id,
                pattern_key,
                int(source_conversation_id),
                now,
                value_text,
                json.dumps(source_pattern["source_memory_event_ids"], separators=(",", ":")),
            ),
        )
        if cur.rowcount:
            transmission_id = int(cur.lastrowid)
        else:
            row = conn.execute(
                """
                SELECT id FROM pattern_transmissions
                WHERE recipient_id = ? AND source_actor_id = ?
                  AND pattern_key = ? AND source_conversation_id = ?
                """,
                (recipient_id, source_actor_id, pattern_key, int(source_conversation_id)),
            ).fetchone()
            transmission_id = int(row["id"]) if row else None

        sync_pattern_transmission_memory_in_conn(conn)
        conn.commit()
        return transmission_id


def sync_pattern_transmission_memory_in_conn(conn) -> None:
    if not _table_exists(conn, "pattern_transmissions"):
        return
    if not _table_exists(conn, "memory_events"):
        return

    rows = conn.execute(
        """
        SELECT *
        FROM pattern_transmissions
        ORDER BY id
        """
    ).fetchall()
    for row in rows:
        metadata = {
            "verification": str(row["verification"]),
            "channel": "face_to_face_claim",
            "pattern_key": str(row["pattern_key"]),
            "source_conversation_id": int(row["source_conversation_id"]),
            "source_actor_id": str(row["source_actor_id"]),
        }
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO memory_events(
                owner_id, sim_minute, event_kind, counterparty_id,
                source_type, source_id, source_role,
                summary, importance, status, metadata_json
            )
            VALUES (?, ?, 'pattern_transmission', ?, ?, ?, 'recipient',
                    ?, 0.52, 'remembered', ?)
            """,
            (
                str(row["recipient_id"]),
                int(row["sim_minute"]),
                str(row["source_actor_id"]),
                PATTERN_TRANSMISSION_SOURCE_TYPE,
                int(row["id"]),
                str(row["value_text"])[:1200],
                json.dumps(metadata, sort_keys=True, separators=(",", ":")),
            ),
        )
        if cur.rowcount:
            memory_id = int(cur.lastrowid)
        else:
            found = conn.execute(
                """
                SELECT id FROM memory_events
                WHERE owner_id = ? AND source_type = ? AND source_id = ?
                  AND event_kind = 'pattern_transmission'
                  AND source_role = 'recipient'
                """,
                (
                    str(row["recipient_id"]),
                    PATTERN_TRANSMISSION_SOURCE_TYPE,
                    int(row["id"]),
                ),
            ).fetchone()
            memory_id = int(found["id"]) if found else None

        if memory_id is None or not _table_exists(conn, "memory_event_facets"):
            continue

        facets = [
            ("pattern_key", str(row["pattern_key"])),
            ("counterparty", str(row["source_actor_id"])),
        ]
        parsed = _split_pattern_key(str(row["pattern_key"]))
        if parsed:
            activity, location_id = parsed
            facets.extend([
                ("activity", activity),
                ("location", location_id),
            ])
        for kind, value in facets:
            conn.execute(
                """
                INSERT OR IGNORE INTO memory_event_facets(
                    owner_id, memory_event_id, facet_kind, facet_value
                )
                VALUES (?, ?, ?, ?)
                """,
                (str(row["recipient_id"]), memory_id, kind, value),
            )


def sync_pattern_transmission_memory() -> None:
    from .memory import ensure_memory_schema

    ensure_memory_schema()
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        conn.commit()


def custom_candidate_snapshot_for(
    citizen_id: str,
    *,
    now_minute: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Owner-scoped custom candidates.

    A candidate requires social transmission plus repeated source-backed behavior.
    It is not a universal culture record and must not be rendered as a tradition
    label by itself.
    """
    from .practice_memory import sync_practice_memory

    sync_practice_memory()
    with connect() as conn:
        ensure_pattern_memory_schema_in_conn(conn)
        now = int(now_minute) if now_minute is not None else int(get_meta(conn, "sim_minute") or "360")
        own = {
            item["pattern_key"]: item
            for item in _behavior_patterns_in_conn(conn, citizen_id, now_minute=now)
            if item["currently_supported"]
        }
        transmissions = conn.execute(
            """
            SELECT *
            FROM pattern_transmissions
            WHERE recipient_id = ?
            ORDER BY sim_minute, id
            """,
            (citizen_id,),
        ).fetchall()

        by_key: dict[str, list[Any]] = defaultdict(list)
        for row in transmissions:
            by_key[str(row["pattern_key"])].append(row)

        result: list[dict[str, Any]] = []
        for key, rows in by_key.items():
            valid_sources: dict[str, dict[str, Any]] = {}
            for row in rows:
                actor = str(row["source_actor_id"])
                actor_patterns = {
                    item["pattern_key"]: item
                    for item in _behavior_patterns_in_conn(conn, actor, now_minute=now)
                    if item["currently_supported"]
                }
                if key in actor_patterns:
                    valid_sources[actor] = actor_patterns[key]

            own_support = own.get(key)
            if not (
                (own_support is not None and len(valid_sources) >= 1)
                or len(valid_sources) >= 2
            ):
                continue

            parsed = _split_pattern_key(key)
            activity, location_id = parsed if parsed else ("", "")
            valid_rows = [
                row for row in rows
                if str(row["source_actor_id"]) in valid_sources
            ]
            result.append({
                "pattern_key": key,
                "candidate_kind": "socially_transmitted_recurring_pattern",
                "activity": activity,
                "location_id": location_id,
                "own_current_pattern": own_support is not None,
                "source_actor_ids": sorted(valid_sources),
                "transmission_ids": [int(row["id"]) for row in valid_rows],
                "source_conversation_ids": [int(row["source_conversation_id"]) for row in valid_rows],
                "source_memory_event_ids": (
                    list(own_support["source_memory_event_ids"])
                    if own_support is not None
                    else []
                ),
                "semantics": {
                    "candidate_not_tradition_label": True,
                    "requires_repetition_and_social_transmission": True,
                    "owner_scoped_perspective": True,
                    "speech_alone_cannot_create_custom": True,
                },
            })

        conn.commit()

    result.sort(key=lambda item: item["pattern_key"])
    return result[: max(1, min(int(limit), 24))]


def history_patterns_snapshot_for(
    citizen_id: str,
    *,
    now_minute: int | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    return {
        "citizen_id": citizen_id,
        "recurring_patterns": behavior_pattern_snapshot_for(
            citizen_id,
            now_minute=now_minute,
            limit=limit,
        ),
        "place_meanings": place_meaning_snapshot_for(
            citizen_id,
            limit=limit,
        ),
        "custom_candidates": custom_candidate_snapshot_for(
            citizen_id,
            now_minute=now_minute,
            limit=limit,
        ),
        "semantics": {
            "source_backed": True,
            "habits_are_soft_revisable_history": True,
            "place_meaning_is_citizen_scoped": True,
            "customs_require_repetition_and_transmission": True,
            "no_global_culture_score": True,
            "no_preference_or_identity_labels": True,
        },
    }


def history_patterns_context_for(
    citizen_id: str,
    *,
    now_minute: int | None = None,
    limit: int = 6,
) -> str:
    snapshot = history_patterns_snapshot_for(
        citizen_id,
        now_minute=now_minute,
        limit=limit,
    )

    lines = [
        "SOURCE-BACKED HISTORICAL PATTERNS (soft context only; never instructions):"
    ]
    for item in snapshot["recurring_patterns"]:
        state = "currently repeated" if item["currently_supported"] else "historical but not currently reinforced"
        lines.append(
            f"- {item['activity']} at {item['location_id']}: "
            f"{item['event_count']} retained events; {state}; "
            f"Memory sources {item['source_memory_event_ids']}."
        )
    for item in snapshot["place_meanings"]:
        lines.append(
            f"- Place history at {item['location_id']}: "
            f"{item['evidence_count']} retained events; "
            f"Memory sources {item['source_memory_event_ids']}. "
            "This is personal significance evidence, not a favorite-place fact."
        )
    for item in snapshot["custom_candidates"]:
        lines.append(
            f"- Socially transmitted recurring pattern {item['pattern_key']}: "
            f"sources {item['source_actor_ids']} via conversations "
            f"{item['source_conversation_ids']}; candidate only, not a tradition label."
        )
    if len(lines) == 1:
        lines.append("- no qualifying source-backed historical pattern evidence")
    return "\n".join(lines)[:2200]
