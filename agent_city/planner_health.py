"""
Planner decision health.

Records every autonomous planning attempt so long unattended runs can be
audited afterwards: how many citizen turns produced a real choice, how many
were refused by Simulation, how many failed before a choice existed (Ollama
offline, invalid JSON, truncated reply), and how close the prompt came to the
model's context window.

This module is observational only. It never changes citizen behavior, world
truth, or Simulation authority. A telemetry failure must never stop the planner.
"""

from __future__ import annotations

import sys
import time
from typing import Any

from .db import connect

# Outcomes where the citizen ended up with a validated physical choice, or the
# Simulation legitimately said no. Neither is a planner malfunction.
HEALTHY_OUTCOMES = {"chosen", "rejected", "no_actions"}

# Outcomes where the citizen lost a turn because the planner itself failed.
FAILURE_OUTCOMES = {
    "ollama_error",
    "invalid_json",
    "truncated_reply",
    "dialogue_error",
    "error",
}

MAX_RETAINED_ATTEMPTS = 5000
NEAR_OVERFLOW_RATIO = 0.95


def ensure_planner_health_schema() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS planner_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                real_ts REAL NOT NULL,
                sim_minute INTEGER NOT NULL,
                citizen_id TEXT NOT NULL,
                outcome TEXT NOT NULL,
                detail TEXT,
                prompt_tokens_estimate INTEGER,
                prompt_tokens_actual INTEGER,
                num_ctx INTEGER,
                detail_level INTEGER,
                duration_ms INTEGER
            );

            CREATE INDEX IF NOT EXISTS idx_planner_attempts_time
            ON planner_attempts(real_ts DESC, id DESC);
            """
        )
        conn.commit()


def record_attempt(
    *,
    citizen_id: str,
    sim_minute: int,
    outcome: str,
    detail: str = "",
    prompt_tokens_estimate: int | None = None,
    prompt_tokens_actual: int | None = None,
    num_ctx: int | None = None,
    detail_level: int | None = None,
    duration_ms: int | None = None,
) -> None:
    detail = " ".join(str(detail or "").split())[:400]
    if outcome in FAILURE_OUTCOMES:
        print(
            f"[planner] {citizen_id} lost a turn at sim minute {sim_minute}: "
            f"{outcome}{f' - {detail}' if detail else ''}",
            file=sys.stderr,
            flush=True,
        )
    elif (
        prompt_tokens_actual
        and num_ctx
        and prompt_tokens_actual >= int(num_ctx * NEAR_OVERFLOW_RATIO)
    ):
        print(
            f"[planner] {citizen_id} prompt used {prompt_tokens_actual}/{num_ctx} "
            "context tokens; older memory may have been cut by Ollama.",
            file=sys.stderr,
            flush=True,
        )

    try:
        ensure_planner_health_schema()
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO planner_attempts(
                    real_ts, sim_minute, citizen_id, outcome, detail,
                    prompt_tokens_estimate, prompt_tokens_actual, num_ctx,
                    detail_level, duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    int(sim_minute),
                    str(citizen_id),
                    str(outcome),
                    detail,
                    prompt_tokens_estimate,
                    prompt_tokens_actual,
                    num_ctx,
                    detail_level,
                    duration_ms,
                ),
            )
            conn.execute(
                """
                DELETE FROM planner_attempts
                WHERE id <= (SELECT MAX(id) FROM planner_attempts) - ?
                """,
                (MAX_RETAINED_ATTEMPTS,),
            )
            conn.commit()
    except Exception as exc:  # telemetry must never stop the planner
        print(f"[planner] could not record planner health: {exc}", file=sys.stderr, flush=True)


def _summarize(rows: list[Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["outcome"]] = counts.get(row["outcome"], 0) + 1

    total = len(rows)
    failures = sum(n for outcome, n in counts.items() if outcome in FAILURE_OUTCOMES)
    actual = [int(r["prompt_tokens_actual"]) for r in rows if r["prompt_tokens_actual"]]
    trimmed = sum(1 for r in rows if (r["detail_level"] or 0) > 0)
    near_overflow = sum(
        1
        for r in rows
        if r["prompt_tokens_actual"]
        and r["num_ctx"]
        and int(r["prompt_tokens_actual"]) >= int(int(r["num_ctx"]) * NEAR_OVERFLOW_RATIO)
    )
    return {
        "attempts": total,
        "chosen": counts.get("chosen", 0),
        "rejected_by_simulation": counts.get("rejected", 0),
        "failures": failures,
        "failure_rate": round(failures / total, 4) if total else 0.0,
        "by_outcome": counts,
        "prompt_tokens_max": max(actual) if actual else None,
        "prompt_tokens_avg": round(sum(actual) / len(actual)) if actual else None,
        "memory_trimmed_attempts": trimmed,
        "near_overflow_attempts": near_overflow,
    }


def planner_health_summary() -> dict[str, Any]:
    try:
        ensure_planner_health_schema()
        with connect() as conn:
            rows = conn.execute(
                "SELECT * FROM planner_attempts ORDER BY id DESC"
            ).fetchall()
    except Exception as exc:
        return {"available": False, "error": str(exc)}

    cutoff = time.time() - 24 * 3600
    recent = [row for row in rows if float(row["real_ts"]) >= cutoff]
    last_failure = next((row for row in rows if row["outcome"] in FAILURE_OUTCOMES), None)
    num_ctx = next((int(row["num_ctx"]) for row in rows if row["num_ctx"]), None)

    return {
        "available": True,
        "num_ctx": num_ctx,
        "last_24h": _summarize(recent),
        "retained": _summarize(rows),
        "last_failure": (
            {
                "citizen_id": last_failure["citizen_id"],
                "outcome": last_failure["outcome"],
                "detail": last_failure["detail"],
                "sim_minute": int(last_failure["sim_minute"]),
                "real_ts": float(last_failure["real_ts"]),
            }
            if last_failure
            else None
        ),
    }
