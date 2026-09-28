from __future__ import annotations

import json
import math
import re
import secrets
from typing import Any

import httpx

from .db import connect, get_meta
from .visitors import visit_access_payload

OLLAMA_URL = "http://127.0.0.1:11434"

_WORD_NUMBERS = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "eleven": 11.0,
    "twelve": 12.0,
    "thirteen": 13.0,
    "fourteen": 14.0,
    "fifteen": 15.0,
    "sixteen": 16.0,
    "seventeen": 17.0,
    "eighteen": 18.0,
    "nineteen": 19.0,
    "twenty": 20.0,
}
_DIRECTION_VECTORS = {
    "east": (1.0, 0.0),
    "west": (-1.0, 0.0),
    "north": (0.0, 1.0),
    "south": (0.0, -1.0),
}


def ensure_shared_action_schema() -> None:
    """
    Communication-owned conversational/source projection.

    Simulation owns the actual shared_activities row and physical job. This table
    stores how that Simulation proposal came from a durable visitor exchange and
    supplies a small UI/read model without making chat physical authority.
    """
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS shared_action_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_token TEXT NOT NULL UNIQUE,
                visitor TEXT NOT NULL,
                citizen_id TEXT NOT NULL,
                visit_id INTEGER NOT NULL,
                source_exchange_id INTEGER NOT NULL UNIQUE,
                action_kind TEXT NOT NULL,
                label TEXT NOT NULL,
                objective TEXT,
                frame_id TEXT,
                target_x_m REAL,
                target_y_m REAL,
                requested_tool_id TEXT,
                status TEXT NOT NULL DEFAULT 'proposed',
                acceptance_available INTEGER NOT NULL DEFAULT 1,
                simulation_activity_id INTEGER,
                simulation_action_id TEXT,
                simulation_status TEXT,
                simulation_progress REAL,
                simulation_start_minute INTEGER,
                simulation_end_minute INTEGER,
                observation_ids_json TEXT NOT NULL DEFAULT '[]',
                outcome_text TEXT,
                created_minute INTEGER NOT NULL,
                updated_minute INTEGER NOT NULL,
                accepted_minute INTEGER,
                rejected_minute INTEGER
            );

            CREATE INDEX IF NOT EXISTS idx_shared_action_visit
            ON shared_action_proposals(visitor, citizen_id, visit_id, id DESC);

            CREATE INDEX IF NOT EXISTS idx_shared_action_status
            ON shared_action_proposals(status, id);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_shared_action_sim_activity
            ON shared_action_proposals(simulation_activity_id)
            WHERE simulation_activity_id IS NOT NULL;
            """
        )

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(shared_action_proposals)")
        }
        if "simulation_activity_id" not in columns:
            conn.execute(
                "ALTER TABLE shared_action_proposals ADD COLUMN simulation_activity_id INTEGER"
            )
        conn.commit()


def _number_value(raw: str) -> float | None:
    token = str(raw or "").strip().lower()
    if token in _WORD_NUMBERS:
        return _WORD_NUMBERS[token]
    try:
        value = float(token)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_explicit_relative_target(text: str) -> tuple[float, float] | None:
    """
    Parse only explicit meter + cardinal-direction language.

    Examples:
      "walk five meters east"
      "move 2 m north and 3 meters west"

    "over there", pointing gestures, or unspecified "this way" intentionally do
    not become coordinates.
    """
    source = " ".join(str(text or "").lower().split())
    if not source:
        return None

    number = r"(?:\d+(?:\.\d+)?|" + "|".join(_WORD_NUMBERS) + r")"
    unit = r"(?:m|meter|meters|metre|metres)"
    direction = r"(?:north|south|east|west)"

    matches: list[tuple[float, str]] = []
    used_spans: set[tuple[int, int]] = set()

    patterns = [
        re.compile(rf"\b(?P<n>{number})\s*(?:{unit})\s+(?P<d>{direction})\b"),
        re.compile(rf"\b(?P<d>{direction})\s+(?P<n>{number})\s*(?:{unit})\b"),
    ]

    for pattern in patterns:
        for match in pattern.finditer(source):
            span = match.span()
            if span in used_spans:
                continue
            value = _number_value(match.group("n"))
            if value is None or value <= 0:
                continue
            used_spans.add(span)
            matches.append((value, match.group("d")))

    if not matches:
        return None

    dx = 0.0
    dy = 0.0
    for value, direction_name in matches:
        vx, vy = _DIRECTION_VECTORS[direction_name]
        dx += vx * value
        dy += vy * value

    if math.hypot(dx, dy) < 0.1:
        return None
    return round(dx, 4), round(dy, 4)


def _simulation_contract_available() -> bool:
    try:
        from . import exploration
    except Exception:
        return False
    return all(
        callable(getattr(exploration, name, None))
        for name in (
            "propose_shared_activity",
            "accept_shared_activity",
            "shared_activity_payload",
        )
    )


def _safe_simulation_payload(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    movement = raw.get("movement") if isinstance(raw.get("movement"), dict) else {}
    progress = movement.get("progress")
    if progress is None:
        progress = raw.get("progress")

    observation_ids: list[int] = []
    observation_id = raw.get("observation_id")
    if isinstance(observation_id, int):
        observation_ids.append(observation_id)

    status = str(raw.get("status") or "").strip().lower() or None
    action_id = raw.get("citizen_job_id")

    return {
        "activity_id": int(raw["id"]) if raw.get("id") is not None else None,
        "status": status,
        "action_id": str(action_id) if action_id is not None else None,
        "progress": float(progress) if isinstance(progress, (int, float)) else None,
        "start_minute": (
            int(raw["started_minute"])
            if raw.get("started_minute") is not None
            else None
        ),
        "end_minute": (
            int(raw["completed_minute"])
            if raw.get("completed_minute") is not None
            else None
        ),
        "observation_ids": observation_ids,
        "outcome": " ".join(str(raw.get("outcome") or "").split())[:500] or None,
        "failure_reason": " ".join(str(raw.get("failure_reason") or "").split())[:300] or None,
        "frame_id": str(raw.get("frame_id") or "").strip()[:80] or None,
        "target_x_m": (
            float(raw["target_x_m"])
            if raw.get("target_x_m") is not None
            else None
        ),
        "target_y_m": (
            float(raw["target_y_m"])
            if raw.get("target_y_m") is not None
            else None
        ),
        "activity_type": str(raw.get("activity_type") or "").strip()[:80] or None,
        "objective": " ".join(str(raw.get("objective") or "").split())[:500] or None,
        "tool_equipment_id": (
            str(raw["tool_equipment_id"])
            if raw.get("tool_equipment_id") is not None
            else None
        ),
    }


def simulation_propose_shared_activity(
    *,
    visitor: str,
    citizen_id: str,
    target_x_m: float,
    target_y_m: float,
    objective: str,
    source_visit_id: int,
    source_exchange_id: int,
    requested_tool_id: str | None = None,
) -> dict[str, Any]:
    try:
        from .exploration import propose_shared_activity, shared_activity_payload
    except Exception:
        return {
            "available": False,
            "ok": False,
            "reason": "Simulation shared-activity proposal lifecycle is unavailable.",
        }

    tool_id: int | None = None
    if requested_tool_id:
        try:
            tool_id = int(requested_tool_id)
        except ValueError:
            return {
                "available": True,
                "ok": False,
                "reason": "Requested tool/equipment ID is invalid.",
            }

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        try:
            ok, activity_id, message = propose_shared_activity(
                conn,
                visitor=visitor,
                citizen_id=citizen_id,
                target_x_m=float(target_x_m),
                target_y_m=float(target_y_m),
                objective=objective,
                source_visit_id=int(source_visit_id),
                source_exchange_id=int(source_exchange_id),
                tool_equipment_id=tool_id,
                now=now,
            )
        except Exception as exc:
            return {
                "available": True,
                "ok": False,
                "reason": f"Simulation proposal validation failed: {type(exc).__name__}.",
            }
        if not ok or activity_id is None:
            return {
                "available": True,
                "ok": False,
                "reason": str(message or "Simulation rejected the shared activity proposal."),
            }
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)

    safe = _safe_simulation_payload(payload)
    return {
        "available": True,
        "ok": True,
        "reason": str(message or ""),
        "payload": safe,
    }


def simulation_accept_shared_activity(activity_id: int, visitor: str) -> dict[str, Any]:
    try:
        from .exploration import accept_shared_activity, shared_activity_payload
    except Exception:
        return {
            "available": False,
            "ok": False,
            "reason": "Simulation shared-activity acceptance lifecycle is unavailable.",
        }

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        try:
            ok, job_id, message = accept_shared_activity(
                conn,
                int(activity_id),
                visitor,
                now=now,
            )
        except Exception as exc:
            return {
                "available": True,
                "ok": False,
                "reason": f"Simulation shared-activity start failed: {type(exc).__name__}.",
            }
        if not ok:
            return {
                "available": True,
                "ok": False,
                "reason": str(message or "Simulation rejected the accepted shared activity."),
            }
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)

    safe = _safe_simulation_payload(payload) or {}
    if safe.get("action_id") is None and job_id is not None:
        safe["action_id"] = str(job_id)
    return {
        "available": True,
        "ok": True,
        "reason": str(message or ""),
        "payload": safe,
    }


def simulation_shared_activity_status(activity_id: int) -> dict[str, Any] | None:
    try:
        from .exploration import shared_activity_payload
    except Exception:
        return None

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        try:
            payload = shared_activity_payload(conn, int(activity_id), now)
        except Exception:
            return None
    return _safe_simulation_payload(payload)


def simulation_cancel_shared_activity(
    activity_id: int,
    visitor: str,
    *,
    reason: str,
) -> dict[str, Any]:
    """
    Ask Simulation to cancel/reject an unstarted canonical proposal.

    Communication never mutates Simulation's shared_activities table directly.
    Until Simulation exposes this primitive, rejection/expiry fails closed.
    """
    try:
        from . import exploration
    except Exception:
        return {
            "available": False,
            "ok": False,
            "reason": "Simulation shared-activity cancellation is unavailable.",
        }

    cancel = getattr(exploration, "cancel_shared_activity", None)
    if not callable(cancel):
        return {
            "available": False,
            "ok": False,
            "reason": "Simulation shared-activity cancellation is unavailable.",
        }

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        try:
            raw = cancel(
                conn,
                int(activity_id),
                visitor,
                now=now,
                reason=reason,
            )
        except Exception as exc:
            return {
                "available": True,
                "ok": False,
                "reason": f"Simulation shared-activity cancellation failed: {type(exc).__name__}.",
            }

        if isinstance(raw, tuple):
            ok = bool(raw[0]) if raw else False
            message = str(raw[1] if len(raw) > 1 else "")
        elif isinstance(raw, dict):
            ok = bool(raw.get("ok"))
            message = str(raw.get("message") or raw.get("reason") or "")
        else:
            ok = bool(raw)
            message = ""

        if not ok:
            return {
                "available": True,
                "ok": False,
                "reason": message or "Simulation refused to cancel the shared activity proposal.",
            }

        conn.commit()

    return {
        "available": True,
        "ok": True,
        "reason": message or "Simulation cancelled the shared activity proposal.",
    }


def _row_payload(row: Any) -> dict[str, Any]:
    item = dict(row)
    try:
        observation_ids = json.loads(item.get("observation_ids_json") or "[]")
    except json.JSONDecodeError:
        observation_ids = []

    return {
        "id": int(item["id"]),
        "proposal_token": item["proposal_token"],
        "visitor": item["visitor"],
        "citizen_id": item["citizen_id"],
        "visit_id": int(item["visit_id"]),
        "source_exchange_id": int(item["source_exchange_id"]),
        "action_kind": item["action_kind"],
        "label": item["label"],
        "objective": item.get("objective"),
        "target": {
            "frame_id": item.get("frame_id"),
            "x_m": item.get("target_x_m"),
            "y_m": item.get("target_y_m"),
        },
        "requested_tool_id": item.get("requested_tool_id"),
        "status": item["status"],
        "acceptance_available": bool(item["acceptance_available"]),
        "simulation_activity_id": item.get("simulation_activity_id"),
        "simulation_action_id": item.get("simulation_action_id"),
        "simulation_status": item.get("simulation_status"),
        "progress": item.get("simulation_progress"),
        "start_minute": item.get("simulation_start_minute"),
        "end_minute": item.get("simulation_end_minute"),
        "observation_ids": observation_ids if isinstance(observation_ids, list) else [],
        "outcome": item.get("outcome_text"),
        "created_minute": int(item["created_minute"]),
        "updated_minute": int(item["updated_minute"]),
        "accepted_minute": item.get("accepted_minute"),
        "rejected_minute": item.get("rejected_minute"),
    }


def _local_status(sim_status: str | None, current: str) -> str:
    status = str(sim_status or "").lower()
    if status == "proposed":
        return "proposed"
    if status in {"active", "started", "moving", "inspecting"}:
        return "started"
    if status in {"complete", "completed", "success"}:
        return "completed"
    if status in {"failed", "rejected"}:
        return "failed"
    if status in {"cancelled", "canceled"}:
        return "cancelled"
    return current


def _sync_one(conn, row: Any, now: int) -> Any:
    activity_id = row["simulation_activity_id"]
    if activity_id is None:
        return row

    status = simulation_shared_activity_status(int(activity_id))
    if not status:
        return row

    local_status = _local_status(status.get("status"), str(row["status"]))
    conn.execute(
        """
        UPDATE shared_action_proposals
        SET status = ?,
            simulation_status = ?,
            simulation_action_id = COALESCE(?, simulation_action_id),
            simulation_progress = COALESCE(?, simulation_progress),
            simulation_start_minute = COALESCE(?, simulation_start_minute),
            simulation_end_minute = COALESCE(?, simulation_end_minute),
            observation_ids_json = ?,
            outcome_text = COALESCE(?, outcome_text),
            acceptance_available = CASE WHEN ? = 'proposed' THEN 1 ELSE 0 END,
            updated_minute = ?
        WHERE id = ?
        """,
        (
            local_status,
            status.get("status"),
            status.get("action_id"),
            status.get("progress"),
            status.get("start_minute"),
            status.get("end_minute"),
            json.dumps(status.get("observation_ids") or []),
            status.get("outcome") or status.get("failure_reason"),
            local_status,
            now,
            int(row["id"]),
        ),
    )
    return conn.execute(
        "SELECT * FROM shared_action_proposals WHERE id = ?",
        (int(row["id"]),),
    ).fetchone()


def proposal_payload(proposal_id: int, *, sync: bool = True) -> dict[str, Any] | None:
    ensure_shared_action_schema()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM shared_action_proposals WHERE id = ?",
            (int(proposal_id),),
        ).fetchone()
        if not row:
            return None
        if sync:
            now = int(get_meta(conn, "sim_minute") or "360")
            row = _sync_one(conn, row, now)
            conn.commit()
        return _row_payload(row)


def proposals_for_visit(
    visitor: str,
    citizen_id: str,
    *,
    visit_id: int | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    ensure_shared_action_schema()
    with connect() as conn:
        params: list[Any] = [visitor, citizen_id]
        where = "visitor = ? AND citizen_id = ?"
        if visit_id is not None:
            where += " AND visit_id = ?"
            params.append(int(visit_id))
        params.append(max(1, min(int(limit), 30)))

        rows = conn.execute(
            f"""
            SELECT * FROM shared_action_proposals
            WHERE {where}
            ORDER BY id DESC LIMIT ?
            """,
            tuple(params),
        ).fetchall()

        now = int(get_meta(conn, "sim_minute") or "360")
        result = []
        for row in rows:
            if row["simulation_activity_id"] is not None:
                row = _sync_one(conn, row, now)
            result.append(_row_payload(row))
        conn.commit()
        return list(reversed(result))


def shared_action_option_context(visitor: str, citizen_id: str) -> str:
    if not _simulation_contract_available():
        return (
            "AVAILABLE SHARED PHYSICAL ACTIVITIES:\n"
            "- Simulation shared-action lifecycle is not available in this runtime"
        )

    access = visit_access_payload(visitor, citizen_id)
    if not access.get("accessible"):
        return (
            "AVAILABLE SHARED PHYSICAL ACTIVITIES:\n"
            "- none while visitor and citizen are not physically available face-to-face"
        )

    return (
        "AVAILABLE SHARED PHYSICAL ACTIVITIES:\n"
        "- a short local walk + baseline inspection may be PROPOSED when the visitor "
        "explicitly gives a meter distance and cardinal direction (north/south/east/west)\n"
        "- Simulation validates the exact target, proximity, range, energy reserve, "
        "tool availability, and action legality before any structured proposal exists\n"
        "- proposal acceptance still does not count as started until Simulation creates the real physical job"
    )


def shared_action_context(visitor: str, citizen_id: str, *, visit_id: int | None = None) -> str:
    proposals = proposals_for_visit(visitor, citizen_id, visit_id=visit_id, limit=4)
    if not proposals:
        return (
            "SHARED PHYSICAL ACTIVITY:\n"
            "- no current shared-action proposal or validated shared activity"
        )

    lines = ["SHARED PHYSICAL ACTIVITY:"]
    for item in proposals:
        status = item["status"]
        if status == "proposed":
            lines.append(
                f"- proposal #{item['id']} pending visitor acceptance: {item['label']}. "
                "It has NOT physically started."
            )
        elif status == "accepted" and not item.get("simulation_action_id"):
            lines.append(
                f"- proposal #{item['id']} was accepted conversationally, but Simulation has "
                "not returned a physical job ID. It has NOT started."
            )
        elif status == "started":
            progress = item.get("progress")
            progress_text = f" ({float(progress) * 100:.0f}% progress)" if progress is not None else ""
            lines.append(
                f"- Simulation shared activity #{item.get('simulation_activity_id')} / "
                f"job {item.get('simulation_action_id')} is ACTIVE: {item['label']}{progress_text}."
            )
        elif status == "completed":
            lines.append(
                f"- Simulation shared activity #{item.get('simulation_activity_id')} COMPLETED: "
                f"{item['label']}."
            )
        elif status in {"failed", "cancelled", "rejected", "expired"}:
            lines.append(f"- proposal #{item['id']} ended as {status}: {item['label']}.")
    lines.append(
        "- Only a proposal with a real active Simulation job ID may be described as physically started."
    )
    return "\n".join(lines)


async def _exchange_mutually_proposes_walk(
    *,
    model: str,
    visitor_text: str,
    citizen_text: str,
    dx_m: float,
    dy_m: float,
) -> bool:
    prompt = f"""
Determine whether this durable face-to-face exchange mutually proposes taking the
explicit visitor-requested local movement together.

VISITOR:
{visitor_text}

CITIZEN:
{citizen_text}

PARSED EXPLICIT RELATIVE REQUEST:
east_delta_m={dx_m}
north_delta_m={dy_m}

Return JSON only:
{{"propose": true or false}}

Rules:
- true only if the visitor proposes the movement/activity and the citizen response is willing/proposing, not refusing.
- a capability question alone is false.
- do not create/change coordinates or action parameters.
""".strip()

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return only JSON with one boolean field: propose.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {"temperature": 0.0, "num_ctx": 1536, "num_predict": 40},
                },
            )
            response.raise_for_status()
            raw = str((response.json().get("message") or {}).get("content") or "").strip()
            data = json.loads(raw)
    except Exception:
        return False
    return bool(data.get("propose")) if isinstance(data, dict) else False


async def maybe_create_proposal_from_exchange(
    *,
    visitor: str,
    citizen_id: str,
    visit_id: int,
    source_exchange_id: int,
    visitor_text: str,
    citizen_text: str,
    model: str,
) -> dict[str, Any] | None:
    """
    Translate explicit conversational intent into a Simulation-validated proposal.

    Communication parses only relative meter/cardinal intent. Simulation decides
    whether the resulting proposed target/activity is physically legal and owns
    the canonical shared_activities row.
    """
    ensure_shared_action_schema()

    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM shared_action_proposals WHERE source_exchange_id = ?",
            (int(source_exchange_id),),
        ).fetchone()
        if existing:
            return _row_payload(existing)

    access = visit_access_payload(visitor, citizen_id)
    if not access.get("accessible"):
        return None

    relative = parse_explicit_relative_target(visitor_text)
    if relative is None:
        return None
    dx_m, dy_m = relative

    if not await _exchange_mutually_proposes_walk(
        model=model,
        visitor_text=visitor_text,
        citizen_text=citizen_text,
        dx_m=dx_m,
        dy_m=dy_m,
    ):
        return None

    with connect() as conn:
        citizen = conn.execute(
            "SELECT position_x_m, position_y_m FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
        presence = conn.execute(
            "SELECT x_m, y_m FROM visitor_presence WHERE visitor = ?",
            (visitor,),
        ).fetchone()
        if not citizen or not presence:
            return None

        cx = float(citizen["position_x_m"] or 0.0)
        cy = float(citizen["position_y_m"] or 0.0)
        vx = float(presence["x_m"] or 0.0)
        vy = float(presence["y_m"] or 0.0)
        if math.hypot(cx - vx, cy - vy) > 2.0:
            return None

    target_x = round(cx + dx_m, 4)
    target_y = round(cy + dy_m, 4)
    objective = (
        f"Walk together {dx_m:+g} m east/west and {dy_m:+g} m north/south, "
        "then perform a baseline local inspection."
    )

    simulation = simulation_propose_shared_activity(
        visitor=visitor,
        citizen_id=citizen_id,
        target_x_m=target_x,
        target_y_m=target_y,
        objective=objective,
        source_visit_id=visit_id,
        source_exchange_id=source_exchange_id,
    )
    if not simulation.get("available") or not simulation.get("ok"):
        return None

    safe = simulation.get("payload") or {}
    activity_id = safe.get("activity_id")
    if activity_id is None:
        return None

    now = None
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO shared_action_proposals(
                proposal_token, visitor, citizen_id, visit_id, source_exchange_id,
                action_kind, label, objective, frame_id,
                target_x_m, target_y_m, requested_tool_id,
                status, acceptance_available, simulation_activity_id,
                simulation_status, created_minute, updated_minute
            )
            VALUES (?, ?, ?, ?, ?, 'shared_walk_inspect', ?, ?, ?, ?, ?, ?,
                    'proposed', 1, ?, 'proposed', ?, ?)
            """,
            (
                secrets.token_urlsafe(12),
                visitor,
                citizen_id,
                int(visit_id),
                int(source_exchange_id),
                "Walk together and inspect the destination",
                safe.get("objective") or objective,
                safe.get("frame_id") or "seed_site_local",
                safe.get("target_x_m"),
                safe.get("target_y_m"),
                safe.get("tool_equipment_id"),
                int(activity_id),
                now,
                now,
            ),
        )
        if cur.rowcount:
            proposal_id = int(cur.lastrowid)
        else:
            row = conn.execute(
                "SELECT id FROM shared_action_proposals WHERE source_exchange_id = ?",
                (int(source_exchange_id),),
            ).fetchone()
            if not row:
                return None
            proposal_id = int(row["id"])
        conn.commit()

    return proposal_payload(proposal_id, sync=False)


def expire_pending_proposals_for_visitor(visitor: str) -> int:
    """
    Expire unstarted proposals only when Simulation can cancel its canonical row.

    This avoids Communication saying "expired" while Simulation still exposes the
    physical proposal as available.
    """
    ensure_shared_action_schema()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM shared_action_proposals
            WHERE visitor = ?
              AND status IN ('proposed', 'accepted')
              AND simulation_action_id IS NULL
            ORDER BY id
            """,
            (visitor,),
        ).fetchall()

    expired = 0
    for row in rows:
        activity_id = row["simulation_activity_id"]
        if activity_id is not None:
            result = simulation_cancel_shared_activity(
                int(activity_id),
                visitor,
                reason="visitor_left_or_traveled",
            )
            if not result.get("ok"):
                continue

        with connect() as conn:
            now = int(get_meta(conn, "sim_minute") or "360")
            cur = conn.execute(
                """
                UPDATE shared_action_proposals
                SET status = 'expired', acceptance_available = 0, updated_minute = ?
                WHERE id = ?
                  AND status IN ('proposed', 'accepted')
                  AND simulation_action_id IS NULL
                """,
                (now, int(row["id"])),
            )
            conn.commit()
            expired += int(cur.rowcount or 0)

    return expired


def accept_proposal(proposal_id: int, visitor: str) -> tuple[bool, str, dict[str, Any] | None]:
    ensure_shared_action_schema()

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM shared_action_proposals WHERE id = ?",
            (int(proposal_id),),
        ).fetchone()
        if not row:
            return False, "Shared-action proposal not found.", None
        if str(row["visitor"]) != visitor:
            return False, "This proposal belongs to a different visitor.", None
        if row["status"] != "proposed":
            return False, f"Proposal is already {row['status']}.", _row_payload(row)

        access = visit_access_payload(visitor, str(row["citizen_id"]))
        if not access.get("accessible"):
            now = int(get_meta(conn, "sim_minute") or "360")
            conn.execute(
                """
                UPDATE shared_action_proposals
                SET status = 'expired', acceptance_available = 0, updated_minute = ?
                WHERE id = ?
                """,
                (now, int(proposal_id)),
            )
            conn.commit()
            return False, "You are no longer physically available for this proposal.", proposal_payload(proposal_id, sync=False)

        activity_id = row["simulation_activity_id"]
        if activity_id is None:
            return False, "Simulation proposal identity is missing.", _row_payload(row)

    start = simulation_accept_shared_activity(int(activity_id), visitor)
    if not start.get("available"):
        return False, start.get("reason") or "Simulation shared activity is unavailable.", proposal_payload(proposal_id, sync=False)

    if not start.get("ok"):
        with connect() as conn:
            now = int(get_meta(conn, "sim_minute") or "360")
            conn.execute(
                """
                UPDATE shared_action_proposals
                SET status = 'failed', acceptance_available = 0,
                    simulation_status = 'failed',
                    outcome_text = ?, updated_minute = ?
                WHERE id = ?
                """,
                (
                    start.get("reason") or "Simulation rejected the accepted activity.",
                    now,
                    int(proposal_id),
                ),
            )
            conn.commit()
        return False, start.get("reason") or "Simulation rejected the shared activity.", proposal_payload(proposal_id, sync=False)

    safe = start.get("payload") or {}
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        conn.execute(
            """
            UPDATE shared_action_proposals
            SET status = 'started',
                acceptance_available = 0,
                accepted_minute = ?,
                simulation_action_id = ?,
                simulation_status = ?,
                simulation_progress = ?,
                simulation_start_minute = ?,
                simulation_end_minute = ?,
                observation_ids_json = ?,
                outcome_text = ?,
                updated_minute = ?
            WHERE id = ?
            """,
            (
                now,
                safe.get("action_id"),
                safe.get("status") or "active",
                safe.get("progress"),
                safe.get("start_minute"),
                safe.get("end_minute"),
                json.dumps(safe.get("observation_ids") or []),
                safe.get("outcome"),
                now,
                int(proposal_id),
            ),
        )
        conn.commit()

    return True, "Accepted. Simulation started the shared physical activity.", proposal_payload(proposal_id)


def reject_proposal(proposal_id: int, visitor: str) -> tuple[bool, str, dict[str, Any] | None]:
    ensure_shared_action_schema()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM shared_action_proposals WHERE id = ?",
            (int(proposal_id),),
        ).fetchone()
        if not row:
            return False, "Shared-action proposal not found.", None
        if str(row["visitor"]) != visitor:
            return False, "This proposal belongs to a different visitor.", None
        if row["status"] != "proposed":
            return False, f"Proposal is already {row['status']}.", _row_payload(row)

        activity_id = row["simulation_activity_id"]

    if activity_id is not None:
        result = simulation_cancel_shared_activity(
            int(activity_id),
            visitor,
            reason="visitor_rejected",
        )
        if not result.get("ok"):
            return (
                False,
                result.get("reason")
                or "Simulation has not cancelled the physical proposal, so Communication will not mark it rejected.",
                proposal_payload(proposal_id, sync=False),
            )

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        conn.execute(
            """
            UPDATE shared_action_proposals
            SET status = 'rejected', acceptance_available = 0,
                rejected_minute = ?, updated_minute = ?
            WHERE id = ?
            """,
            (now, now, int(proposal_id)),
        )
        conn.commit()

    return True, "Proposal declined. No physical action was started.", proposal_payload(proposal_id, sync=False)

