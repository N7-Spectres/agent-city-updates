from __future__ import annotations

from typing import Any

import httpx

from .db import connect, get_meta

OLLAMA_URL = "http://127.0.0.1:11434"

RECENT_CONTEXT_EXCHANGES = 8
DISPLAY_EXCHANGES = 12
SUMMARY_TRIGGER_EXCHANGES = 14
SUMMARY_BATCH_LIMIT = 18
MAX_SUMMARY_WORDS = 180


def ensure_visit_schema() -> None:
    """Create visit/session storage and migrate pre-session conversations safely."""
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversation_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor TEXT NOT NULL,
                citizen_id TEXT NOT NULL,
                started_minute INTEGER NOT NULL,
                ended_minute INTEGER,
                summary TEXT NOT NULL DEFAULT '',
                last_summarized_conversation_id INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_visits_lookup
            ON conversation_visits(visitor, citizen_id, ended_minute, id);
            """
        )

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(conversations)")
        }
        if "visit_id" not in columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN visit_id INTEGER")

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_visit ON conversations(visit_id, id)"
        )

        if get_meta(conn, "visit_schema_migrated") is None:
            current_minute = int(get_meta(conn, "sim_minute") or "360")
            pairs = conn.execute(
                """
                SELECT visitor, citizen_id,
                       MIN(sim_minute) AS first_minute,
                       MAX(sim_minute) AS last_minute,
                       COUNT(*) AS exchange_count
                FROM conversations
                WHERE visit_id IS NULL
                GROUP BY visitor, citizen_id
                """
            ).fetchall()

            for pair in pairs:
                is_recent = current_minute - int(pair["last_minute"]) <= 360
                ended = None if is_recent else int(pair["last_minute"])
                cur = conn.execute(
                    """
                    INSERT INTO conversation_visits
                    (visitor, citizen_id, started_minute, ended_minute, summary)
                    VALUES (?, ?, ?, ?, '')
                    """,
                    (
                        pair["visitor"],
                        pair["citizen_id"],
                        int(pair["first_minute"]),
                        ended,
                    ),
                )
                visit_id = cur.lastrowid
                conn.execute(
                    """
                    UPDATE conversations
                    SET visit_id = ?
                    WHERE visit_id IS NULL AND visitor = ? AND citizen_id = ?
                    """,
                    (visit_id, pair["visitor"], pair["citizen_id"]),
                )

            conn.execute(
                """
                INSERT INTO meta(key, value) VALUES ('visit_schema_migrated', 'true')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """
            )

        conn.commit()


def get_active_visit(conn, visitor: str, citizen_id: str):
    return conn.execute(
        """
        SELECT * FROM conversation_visits
        WHERE visitor = ? AND citizen_id = ? AND ended_minute IS NULL
        ORDER BY id DESC LIMIT 1
        """,
        (visitor, citizen_id),
    ).fetchone()


def get_or_create_active_visit(conn, visitor: str, citizen_id: str, sim_minute: int):
    visit = get_active_visit(conn, visitor, citizen_id)
    if visit:
        return visit

    cur = conn.execute(
        """
        INSERT INTO conversation_visits
        (visitor, citizen_id, started_minute, ended_minute, summary)
        VALUES (?, ?, ?, NULL, '')
        """,
        (visitor, citizen_id, sim_minute),
    )
    conn.commit()
    return conn.execute(
        "SELECT * FROM conversation_visits WHERE id = ?", (cur.lastrowid,)
    ).fetchone()


def get_recent_exchanges(conn, visit_id: int, limit: int = RECENT_CONTEXT_EXCHANGES) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, sim_minute, visitor_text, citizen_text
        FROM conversations
        WHERE visit_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (visit_id, limit),
    ).fetchall()
    return list(reversed([dict(r) for r in rows]))


def visit_payload(conn, visit_id: int) -> dict[str, Any]:
    visit = conn.execute(
        "SELECT * FROM conversation_visits WHERE id = ?", (visit_id,)
    ).fetchone()
    if not visit:
        raise ValueError("Visit not found")

    count = int(
        conn.execute(
            "SELECT COUNT(*) AS n FROM conversations WHERE visit_id = ?", (visit_id,)
        ).fetchone()["n"]
    )
    messages = get_recent_exchanges(conn, visit_id, DISPLAY_EXCHANGES)

    return {
        "visit": dict(visit),
        "messages": messages,
        "exchange_count": count,
        "has_earlier": count > len(messages),
    }


def previous_visits(conn, visitor: str, citizen_id: str, limit: int = 5) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, started_minute, ended_minute, summary
        FROM conversation_visits
        WHERE visitor = ? AND citizen_id = ? AND ended_minute IS NOT NULL
        ORDER BY ended_minute DESC, id DESC LIMIT ?
        """,
        (visitor, citizen_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def close_visit(conn, visit_id: int, sim_minute: int) -> None:
    conn.execute(
        """
        UPDATE conversation_visits
        SET ended_minute = COALESCE(ended_minute, ?)
        WHERE id = ?
        """,
        (sim_minute, visit_id),
    )
    conn.commit()


def fallback_summary(rows: list[dict[str, Any]], existing: str = "") -> str:
    parts: list[str] = []
    if existing.strip():
        parts.append(existing.strip())

    for row in rows[-8:]:
        visitor_text = " ".join(str(row["visitor_text"]).split())[:180]
        citizen_text = " ".join(str(row["citizen_text"]).split())[:220]
        parts.append(f"Visitor: {visitor_text} | Citizen: {citizen_text}")

    merged = " ".join(parts)
    words = merged.split()
    return " ".join(words[:MAX_SUMMARY_WORDS])


async def summarize_visit_if_needed(
    visit_id: int,
    model: str,
    *,
    force: bool = False,
) -> str:
    """Maintain a bounded rolling visit summary while preserving full raw history."""
    with connect() as conn:
        visit = conn.execute(
            "SELECT * FROM conversation_visits WHERE id = ?", (visit_id,)
        ).fetchone()
        if not visit:
            return ""

        total = int(
            conn.execute(
                "SELECT COUNT(*) AS n FROM conversations WHERE visit_id = ?", (visit_id,)
            ).fetchone()["n"]
        )
        existing = str(visit["summary"] or "")
        last_summarized = int(visit["last_summarized_conversation_id"] or 0)

        if not force and total <= SUMMARY_TRIGGER_EXCHANGES:
            return existing

        if force:
            rows = conn.execute(
                """
                SELECT id, visitor_text, citizen_text
                FROM conversations
                WHERE visit_id = ? AND id > ?
                ORDER BY id ASC LIMIT ?
                """,
                (visit_id, last_summarized, SUMMARY_BATCH_LIMIT),
            ).fetchall()
        else:
            recent = conn.execute(
                """
                SELECT id FROM conversations
                WHERE visit_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (visit_id, RECENT_CONTEXT_EXCHANGES),
            ).fetchall()
            if not recent:
                return existing
            cutoff_id = min(int(r["id"]) for r in recent)
            rows = conn.execute(
                """
                SELECT id, visitor_text, citizen_text
                FROM conversations
                WHERE visit_id = ? AND id > ? AND id < ?
                ORDER BY id ASC LIMIT ?
                """,
                (visit_id, last_summarized, cutoff_id, SUMMARY_BATCH_LIMIT),
            ).fetchall()

        rows = [dict(r) for r in rows]
        if not rows:
            return existing

    transcript = "\n".join(
        f"Visitor: {r['visitor_text']}\nCitizen: {r['citizen_text']}" for r in rows
    )

    prompt = f"""
Create a compact memory summary for a continuing conversation between a visitor and one Agent City citizen.
Keep factual conversational continuity only. Do not turn claims into physical world facts.
Preserve important preferences, questions, promises, relationship context, and unresolved topics.
Maximum {MAX_SUMMARY_WORDS} words.

Existing summary:
{existing or '(none)'}

New conversation segment:
{transcript}

Return only the updated summary.
""".strip()

    summary = ""
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Summarize compactly and conservatively."},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0.2,
                        "num_ctx": 2048,
                        "num_predict": 240,
                    },
                },
            )
            response.raise_for_status()
            summary = response.json()["message"]["content"].strip()
    except Exception:
        summary = fallback_summary(rows, existing)

    if not summary:
        summary = fallback_summary(rows, existing)

    max_id = max(int(r["id"]) for r in rows)
    with connect() as conn:
        conn.execute(
            """
            UPDATE conversation_visits
            SET summary = ?, last_summarized_conversation_id = ?
            WHERE id = ?
            """,
            (summary, max_id, visit_id),
        )
        conn.commit()

    if force:
        with connect() as conn:
            remaining = int(
                conn.execute(
                    """
                    SELECT COUNT(*) AS n FROM conversations
                    WHERE visit_id = ? AND id > ?
                    """,
                    (visit_id, max_id),
                ).fetchone()["n"]
            )
        if remaining:
            return await summarize_visit_if_needed(visit_id, model, force=True)

    return summary
