from __future__ import annotations

from typing import Any

from .db import connect, get_meta


def ensure_talk_diagnostic_schema() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS talk_diagnostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_job_id INTEGER NOT NULL,
                sim_minute INTEGER NOT NULL,
                stage TEXT NOT NULL,
                outcome TEXT NOT NULL,
                code TEXT NOT NULL,
                detail TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_talk_diagnostics_job
            ON talk_diagnostics(source_job_id, id);
            """
        )
        conn.commit()


def record_talk_diagnostic(
    source_job_id: int,
    *,
    stage: str,
    outcome: str,
    code: str,
    detail: str | None = None,
) -> int:
    ensure_talk_diagnostic_schema()
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            INSERT INTO talk_diagnostics
            (source_job_id, sim_minute, stage, outcome, code, detail)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(source_job_id),
                now,
                str(stage or "unknown")[:80],
                str(outcome or "unknown")[:40],
                str(code or "unknown")[:120],
                str(detail or "").strip()[:500] or None,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def talk_diagnostics_for(source_job_id: int) -> list[dict[str, Any]]:
    ensure_talk_diagnostic_schema()
    with connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT *
                FROM talk_diagnostics
                WHERE source_job_id = ?
                ORDER BY id
                """,
                (int(source_job_id),),
            ).fetchall()
        ]


def latest_talk_diagnostic(
    source_job_id: int,
    *,
    outcome: str | None = None,
) -> dict[str, Any] | None:
    ensure_talk_diagnostic_schema()
    with connect() as conn:
        if outcome is None:
            row = conn.execute(
                """
                SELECT *
                FROM talk_diagnostics
                WHERE source_job_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (int(source_job_id),),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT *
                FROM talk_diagnostics
                WHERE source_job_id = ? AND outcome = ?
                ORDER BY id DESC LIMIT 1
                """,
                (int(source_job_id), outcome),
            ).fetchone()
        return dict(row) if row else None


def concise_failure_code(source_job_id: int) -> str | None:
    row = latest_talk_diagnostic(source_job_id, outcome="failure")
    return str(row["code"]) if row else None


def concise_failure_code_from_conn(conn, source_job_id: int) -> str | None:
    """
    Read a diagnostic inside an existing transaction without opening/migrating
    another SQLite connection. This keeps diagnostics observational during
    physical job completion.
    """
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'talk_diagnostics'"
    ).fetchone()
    if not table:
        return None
    row = conn.execute(
        """
        SELECT code
        FROM talk_diagnostics
        WHERE source_job_id = ? AND outcome = 'failure'
        ORDER BY id DESC LIMIT 1
        """,
        (int(source_job_id),),
    ).fetchone()
    return str(row["code"]) if row else None
