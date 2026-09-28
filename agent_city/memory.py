from __future__ import annotations

from typing import Any

from .db import connect
from .world import format_sim_time

MAX_RELATIONSHIPS_IN_CONTEXT = 4
MEMORIES_PER_RELATIONSHIP = 2
MAX_CONTEXT_CHARS = 1800


def ensure_memory_schema() -> None:
    """Create durable social-memory storage and backfill existing citizen conversations."""
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                sim_minute INTEGER NOT NULL,
                event_kind TEXT NOT NULL,
                counterparty_id TEXT,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                source_role TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 0.5,
                status TEXT NOT NULL DEFAULT 'remembered',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                UNIQUE(owner_id, source_type, source_id, event_kind, source_role)
            );

            CREATE INDEX IF NOT EXISTS idx_memory_events_owner_time
            ON memory_events(owner_id, sim_minute DESC, id DESC);

            CREATE INDEX IF NOT EXISTS idx_memory_events_relationship
            ON memory_events(owner_id, counterparty_id, sim_minute DESC, id DESC);

            CREATE TABLE IF NOT EXISTS relationship_state (
                owner_id TEXT NOT NULL,
                other_id TEXT NOT NULL,
                first_interaction_minute INTEGER NOT NULL,
                last_interaction_minute INTEGER NOT NULL,
                conversation_count INTEGER NOT NULL DEFAULT 0,
                cooperation_count INTEGER NOT NULL DEFAULT 0,
                disagreement_count INTEGER NOT NULL DEFAULT 0,
                help_given_count INTEGER NOT NULL DEFAULT 0,
                help_received_count INTEGER NOT NULL DEFAULT 0,
                promise_made_count INTEGER NOT NULL DEFAULT 0,
                promise_received_count INTEGER NOT NULL DEFAULT 0,
                promise_fulfilled_count INTEGER NOT NULL DEFAULT 0,
                promise_broken_count INTEGER NOT NULL DEFAULT 0,
                verified_claim_count INTEGER NOT NULL DEFAULT 0,
                contradicted_claim_count INTEGER NOT NULL DEFAULT 0,
                summary TEXT NOT NULL DEFAULT '',
                last_event_id INTEGER,
                PRIMARY KEY(owner_id, other_id)
            );
            """
        )

        rows = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id, summary
            FROM citizen_conversations
            ORDER BY id
            """
        ).fetchall()
        for row in rows:
            _remember_conversation_row(conn, row)

        conn.commit()


def _upsert_relationship_for_conversation(
    conn,
    owner_id: str,
    other_id: str,
    sim_minute: int,
    memory_event_id: int,
) -> None:
    conn.execute(
        """
        INSERT INTO relationship_state(
            owner_id, other_id,
            first_interaction_minute, last_interaction_minute,
            conversation_count, last_event_id
        )
        VALUES (?, ?, ?, ?, 1, ?)
        ON CONFLICT(owner_id, other_id) DO UPDATE SET
            first_interaction_minute = MIN(
                relationship_state.first_interaction_minute,
                excluded.first_interaction_minute
            ),
            last_interaction_minute = MAX(
                relationship_state.last_interaction_minute,
                excluded.last_interaction_minute
            ),
            conversation_count = relationship_state.conversation_count + 1,
            last_event_id = excluded.last_event_id
        """,
        (owner_id, other_id, sim_minute, sim_minute, memory_event_id),
    )


def _insert_conversation_memory(
    conn,
    *,
    owner_id: str,
    other_id: str,
    source_id: int,
    source_role: str,
    sim_minute: int,
    summary: str,
) -> None:
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status
        )
        VALUES (?, ?, 'conversation', ?, 'citizen_conversation', ?, ?, ?, 0.45, 'remembered')
        """,
        (
            owner_id,
            sim_minute,
            other_id,
            source_id,
            source_role,
            summary[:1200],
        ),
    )
    if cur.rowcount:
        _upsert_relationship_for_conversation(
            conn,
            owner_id,
            other_id,
            sim_minute,
            int(cur.lastrowid),
        )


def _remember_conversation_row(conn, row) -> None:
    source_id = int(row["id"])
    sim_minute = int(row["sim_minute"])
    initiator_id = str(row["initiator_id"])
    target_id = str(row["target_id"])
    summary = str(row["summary"] or "").strip()
    if not summary:
        summary = "A face-to-face conversation occurred; no detailed summary was retained."

    _insert_conversation_memory(
        conn,
        owner_id=initiator_id,
        other_id=target_id,
        source_id=source_id,
        source_role="initiator",
        sim_minute=sim_minute,
        summary=summary,
    )
    _insert_conversation_memory(
        conn,
        owner_id=target_id,
        other_id=initiator_id,
        source_id=source_id,
        source_role="target",
        sim_minute=sim_minute,
        summary=summary,
    )


def record_conversation_memory(conversation_id: int) -> None:
    """Remember one validated stored conversation for both participants, once."""
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id, summary
            FROM citizen_conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()
        if not row:
            return
        _remember_conversation_row(conn, row)
        conn.commit()


def _relationship_rows(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT rs.*, c.name AS other_name
            FROM relationship_state rs
            JOIN citizens c ON c.id = rs.other_id
            WHERE rs.owner_id = ?
            ORDER BY rs.last_interaction_minute DESC, c.rowid
            """,
            (citizen_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def _recent_memories(owner_id: str, other_id: str, limit: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, sim_minute, event_kind, summary, source_type, source_id, status
            FROM memory_events
            WHERE owner_id = ? AND counterparty_id = ?
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (owner_id, other_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def social_context_for(
    citizen_id: str,
    *,
    preferred_counterparties: list[str] | None = None,
    limit: int = MAX_RELATIONSHIPS_IN_CONTEXT,
) -> str:
    """
    Build bounded, explainable social context.

    The text describes recorded interaction history. It never promotes remembered
    conversation content into authoritative physical truth.
    """
    rows = _relationship_rows(citizen_id)
    if not rows:
        return "- no durable relationship history yet"

    preferred = preferred_counterparties or []
    preferred_rank = {cid: i for i, cid in enumerate(preferred)}
    rows.sort(
        key=lambda r: (
            0 if r["other_id"] in preferred_rank else 1,
            preferred_rank.get(r["other_id"], 999),
            -int(r["last_interaction_minute"]),
        )
    )

    parts: list[str] = []
    for row in rows[: max(1, limit)]:
        count = int(row["conversation_count"])
        first_label = format_sim_time(int(row["first_interaction_minute"]))
        last_label = format_sim_time(int(row["last_interaction_minute"]))
        memories = _recent_memories(
            citizen_id,
            str(row["other_id"]),
            MEMORIES_PER_RELATIONSHIP,
        )
        memory_text = " | ".join(
            " ".join(str(m["summary"]).split())[:280]
            for m in reversed(memories)
        ) or "no detailed memory retained"

        parts.append(
            f"- {row['other_name']}: {count} recorded face-to-face conversation"
            f"{'s' if count != 1 else ''}; first {first_label}; last {last_label}. "
            f"Remembered conversation content (claims, not automatic physical facts): {memory_text}"
        )

        if sum(len(p) + 1 for p in parts) >= MAX_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_CONTEXT_CHARS]


def relationship_snapshot(citizen_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Read-only relationship history for future UI/API use; contains no social score."""
    rows = _relationship_rows(citizen_id)[: max(1, limit)]
    result: list[dict[str, Any]] = []

    for row in rows:
        recent = _recent_memories(citizen_id, str(row["other_id"]), 3)
        item = dict(row)
        item["first_interaction_label"] = format_sim_time(int(row["first_interaction_minute"]))
        item["last_interaction_label"] = format_sim_time(int(row["last_interaction_minute"]))
        item["recent_memories"] = recent
        result.append(item)

    return result
