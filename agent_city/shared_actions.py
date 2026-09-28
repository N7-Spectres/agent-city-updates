from __future__ import annotations

import json
import secrets
from typing import Any

import httpx

from .db import connect, get_meta
from .visitors import visit_access_payload

OLLAMA_URL = "http://127.0.0.1:11434"

LOCAL_STATUSES = {
    "proposed",
    "accepted",
    "started",
    "completed",
    "rejected",
    "failed",
    "cancelled",
    "expired",
}
TERMINAL_STATUSES = {"completed", "rejected", "failed", "cancelled", "expired"}


def ensure_shared_action_schema() -> None:
    """
    Communication-owned proposal state.

    These rows are conversational proposals/acceptance records, not physical
    actions. Simulation owns physical action IDs, status, movement and outcome.
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
                option_key TEXT NOT NULL,
                action_kind TEXT NOT NULL,
                label TEXT NOT NULL,
                objective TEXT,
                frame_id TEXT,
                target_x_m REAL,
                target_y_m REAL,
                target_subject_type TEXT,
                target_subject_id TEXT,
                requested_tool_id TEXT,
                status TEXT NOT NULL DEFAULT 'proposed',
                acceptance_available INTEGER NOT NULL DEFAULT 1,
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
            """
        )
        conn.commit()


def _normalize_option(raw: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    option_key = str(raw.get("option_key") or raw.get("id") or "").strip()
    action_kind = str(raw.get("action_kind") or raw.get("kind") or "").strip()
    label = " ".join(str(raw.get("label") or "").split())[:180]

    if not option_key or not action_kind or not label:
        return None

    result: dict[str, Any] = {
        "option_key": option_key[:120],
        "action_kind": action_kind[:80],
        "label": label,
        "objective": " ".join(str(raw.get("objective") or "").split())[:300] or None,
        "frame_id": str(raw.get("frame_id") or "").strip()[:80] or None,
        "target_x_m": raw.get("target_x_m"),
        "target_y_m": raw.get("target_y_m"),
        "target_subject_type": str(raw.get("target_subject_type") or "").strip()[:80] or None,
        "target_subject_id": str(raw.get("target_subject_id") or "").strip()[:160] or None,
        "requested_tool_id": str(raw.get("requested_tool_id") or "").strip()[:160] or None,
    }

    for key in ("target_x_m", "target_y_m"):
        value = result[key]
        if value is not None:
            try:
                result[key] = float(value)
            except (TypeError, ValueError):
                return None

    return result


def simulation_shared_action_options(visitor: str, citizen_id: str) -> list[dict[str, Any]]:
    """
    Adapter for Simulation's Stage 2 legal shared-action option provider.

    Until Simulation exposes this callable, no proposal is eligible.
    """
    try:
        from . import simulation
    except Exception:
        return []

    provider = getattr(simulation, "shared_activity_options", None)
    if not callable(provider):
        return []

    try:
        raw_options = provider(visitor, citizen_id)
    except Exception:
        return []

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_options or []:
        option = _normalize_option(raw)
        if not option or option["option_key"] in seen:
            continue
        seen.add(option["option_key"])
        result.append(option)
    return result


def _safe_start_result(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"ok": False, "reason": "Simulation did not return a structured start result."}

    action_id = raw.get("action_id") or raw.get("shared_action_id") or raw.get("id")
    status = str(raw.get("status") or "").strip().lower()
    ok = bool(raw.get("ok", action_id is not None and status in {"active", "started"}))

    result: dict[str, Any] = {
        "ok": ok,
        "action_id": str(action_id) if action_id is not None else None,
        "status": status or None,
        "reason": " ".join(str(raw.get("reason") or "").split())[:300] or None,
    }

    for key in ("progress", "start_minute", "end_minute"):
        value = raw.get(key)
        if value is None:
            result[key] = None
            continue
        try:
            result[key] = float(value) if key == "progress" else int(value)
        except (TypeError, ValueError):
            result[key] = None

    observations = raw.get("observation_ids")
    result["observation_ids"] = [
        int(value)
        for value in observations or []
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    ][:20]
    result["outcome"] = " ".join(str(raw.get("outcome") or "").split())[:500] or None
    return result


def simulation_start_shared_action(proposal: dict[str, Any]) -> dict[str, Any]:
    try:
        from . import simulation
    except Exception:
        return {"ok": False, "available": False, "reason": "Simulation shared-action start is unavailable."}

    starter = getattr(simulation, "start_shared_activity", None)
    if not callable(starter):
        return {"ok": False, "available": False, "reason": "Simulation shared-action start is unavailable."}

    request = {
        "visitor": proposal["visitor"],
        "citizen_id": proposal["citizen_id"],
        "proposal_id": proposal["id"],
        "proposal_token": proposal["proposal_token"],
        "source_visit_id": proposal["visit_id"],
        "source_exchange_id": proposal["source_exchange_id"],
        "option_key": proposal["option_key"],
        "action_kind": proposal["action_kind"],
        "objective": proposal.get("objective"),
        "frame_id": proposal.get("frame_id"),
        "target_x_m": proposal.get("target_x_m"),
        "target_y_m": proposal.get("target_y_m"),
        "target_subject_type": proposal.get("target_subject_type"),
        "target_subject_id": proposal.get("target_subject_id"),
        "requested_tool_id": proposal.get("requested_tool_id"),
    }
    try:
        raw = starter(request)
    except Exception as exc:
        return {
            "ok": False,
            "available": True,
            "reason": f"Simulation rejected/failed shared-action start: {type(exc).__name__}.",
        }

    result = _safe_start_result(raw)
    result["available"] = True
    return result


def simulation_shared_action_status(action_id: str) -> dict[str, Any] | None:
    try:
        from . import simulation
    except Exception:
        return None

    getter = getattr(simulation, "shared_activity_status", None)
    if not callable(getter):
        return None

    try:
        raw = getter(action_id)
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None

    result = _safe_start_result(raw)
    result["ok"] = True
    result["action_id"] = str(raw.get("action_id") or raw.get("shared_action_id") or action_id)
    return result


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
        "option_key": item["option_key"],
        "action_kind": item["action_kind"],
        "label": item["label"],
        "objective": item.get("objective"),
        "target": {
            "frame_id": item.get("frame_id"),
            "x_m": item.get("target_x_m"),
            "y_m": item.get("target_y_m"),
            "subject_type": item.get("target_subject_type"),
            "subject_id": item.get("target_subject_id"),
        },
        "requested_tool_id": item.get("requested_tool_id"),
        "status": item["status"],
        "acceptance_available": bool(item["acceptance_available"]),
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


def _sync_one(conn, row: Any, now: int) -> Any:
    action_id = row["simulation_action_id"]
    if not action_id:
        return row

    status = simulation_shared_action_status(str(action_id))
    if not status:
        return row

    simulation_status = str(status.get("status") or row["simulation_status"] or "").lower()
    local_status = str(row["status"])
    if simulation_status in {"active", "started", "moving", "inspecting"}:
        local_status = "started"
    elif simulation_status in {"complete", "completed", "success"}:
        local_status = "completed"
    elif simulation_status in {"failed", "rejected"}:
        local_status = "failed"
    elif simulation_status in {"cancelled", "canceled"}:
        local_status = "cancelled"

    conn.execute(
        """
        UPDATE shared_action_proposals
        SET status = ?,
            simulation_status = ?,
            simulation_progress = COALESCE(?, simulation_progress),
            simulation_start_minute = COALESCE(?, simulation_start_minute),
            simulation_end_minute = COALESCE(?, simulation_end_minute),
            observation_ids_json = ?,
            outcome_text = COALESCE(?, outcome_text),
            acceptance_available = 0,
            updated_minute = ?
        WHERE id = ?
        """,
        (
            local_status,
            simulation_status or None,
            status.get("progress"),
            status.get("start_minute"),
            status.get("end_minute"),
            json.dumps(status.get("observation_ids") or []),
            status.get("outcome"),
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
            if row["simulation_action_id"]:
                row = _sync_one(conn, row, now)
            result.append(_row_payload(row))
        conn.commit()
        return list(reversed(result))


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
                "not returned a physical action ID. It has NOT started."
            )
        elif status == "started":
            progress = item.get("progress")
            progress_text = f" ({float(progress) * 100:.0f}% progress)" if progress is not None else ""
            lines.append(
                f"- Simulation shared action {item.get('simulation_action_id')} is ACTIVE: "
                f"{item['label']}{progress_text}."
            )
        elif status == "completed":
            lines.append(
                f"- Simulation shared action {item.get('simulation_action_id')} COMPLETED: "
                f"{item['label']}."
            )
        elif status in {"failed", "cancelled", "rejected", "expired"}:
            lines.append(f"- proposal #{item['id']} ended as {status}: {item['label']}.")
    lines.append(
        "- Only a proposal with a real Simulation action ID/status may be described as physically started."
    )
    return "\n".join(lines)


async def _select_option_from_exchange(
    *,
    model: str,
    visitor_text: str,
    citizen_text: str,
    options: list[dict[str, Any]],
) -> str | None:
    safe_options = [
        {
            "option_key": item["option_key"],
            "action_kind": item["action_kind"],
            "label": item["label"],
            "objective": item.get("objective"),
            "frame_id": item.get("frame_id"),
            "target_x_m": item.get("target_x_m"),
            "target_y_m": item.get("target_y_m"),
            "target_subject_type": item.get("target_subject_type"),
            "target_subject_id": item.get("target_subject_id"),
            "requested_tool_id": item.get("requested_tool_id"),
        }
        for item in options
    ]

    prompt = f"""
Classify whether this face-to-face exchange clearly proposes ONE of the currently
legal Simulation-supplied shared physical activity options.

VISITOR:
{visitor_text}

CITIZEN:
{citizen_text}

LEGAL SAFE OPTIONS:
{json.dumps(safe_options, ensure_ascii=False)}

Return JSON only:
{{
  "proposal_key": "exact option_key or null"
}}

Rules:
- Select an option only when the exchange clearly proposes doing it together.
- A question about capability is not automatically a proposal.
- A refusal/disagreement produces null.
- Do not invent coordinates, tools, targets, action types, or option keys.
- If no supplied option matches, return null.
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
                            "content": "Select only a supplied safe option key. Return valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {"temperature": 0.0, "num_ctx": 2048, "num_predict": 80},
                },
            )
            response.raise_for_status()
            raw = str((response.json().get("message") or {}).get("content") or "").strip()
            data = json.loads(raw)
    except Exception:
        return None

    key = data.get("proposal_key") if isinstance(data, dict) else None
    if key is None:
        return None
    key = str(key).strip()
    return key if any(item["option_key"] == key for item in options) else None


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
    Best-effort proposal extraction after a durable visitor exchange exists.

    No legal Simulation option -> no proposal.
    No explicit matching exchange -> no proposal.
    """
    ensure_shared_action_schema()

    access = visit_access_payload(visitor, citizen_id)
    if not access.get("accessible"):
        return None

    options = simulation_shared_action_options(visitor, citizen_id)
    if not options:
        return None

    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM shared_action_proposals WHERE source_exchange_id = ?",
            (int(source_exchange_id),),
        ).fetchone()
        if existing:
            return _row_payload(existing)

    selected_key = await _select_option_from_exchange(
        model=model,
        visitor_text=visitor_text,
        citizen_text=citizen_text,
        options=options,
    )
    if not selected_key:
        return None

    selected = next(item for item in options if item["option_key"] == selected_key)
    now = None
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO shared_action_proposals(
                proposal_token, visitor, citizen_id, visit_id, source_exchange_id,
                option_key, action_kind, label, objective, frame_id,
                target_x_m, target_y_m, target_subject_type, target_subject_id,
                requested_tool_id, status, acceptance_available,
                created_minute, updated_minute
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', 1, ?, ?)
            """,
            (
                secrets.token_urlsafe(12),
                visitor,
                citizen_id,
                int(visit_id),
                int(source_exchange_id),
                selected["option_key"],
                selected["action_kind"],
                selected["label"],
                selected.get("objective"),
                selected.get("frame_id"),
                selected.get("target_x_m"),
                selected.get("target_y_m"),
                selected.get("target_subject_type"),
                selected.get("target_subject_id"),
                selected.get("requested_tool_id"),
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
    """Expire unstarted proposals when the visitor physically leaves/moves."""
    ensure_shared_action_schema()
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            UPDATE shared_action_proposals
            SET status = 'expired', acceptance_available = 0, updated_minute = ?
            WHERE visitor = ?
              AND status IN ('proposed', 'accepted')
              AND simulation_action_id IS NULL
            """,
            (now, visitor),
        )
        conn.commit()
        return int(cur.rowcount or 0)



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

        # Revalidate that the option is still currently legal before recording
        # acceptance. Proposal existence never freezes physical legality.
        current = {
            option["option_key"]: option
            for option in simulation_shared_action_options(visitor, str(row["citizen_id"]))
        }
        if row["option_key"] not in current:
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
            return False, "The proposed physical activity is no longer legal/available.", proposal_payload(proposal_id, sync=False)

        now = int(get_meta(conn, "sim_minute") or "360")
        conn.execute(
            """
            UPDATE shared_action_proposals
            SET status = 'accepted', acceptance_available = 0,
                accepted_minute = ?, updated_minute = ?
            WHERE id = ?
            """,
            (now, now, int(proposal_id)),
        )
        conn.commit()

    proposal = proposal_payload(proposal_id, sync=False)
    if not proposal:
        return False, "Proposal could not be reloaded.", None

    start = simulation_start_shared_action(proposal)
    if not start.get("available"):
        # Acceptance is durable human intent, but remains explicitly not started.
        return True, "Accepted. Waiting for Simulation to expose/start the physical shared action.", proposal

    if not start.get("ok") or not start.get("action_id"):
        with connect() as conn:
            now = int(get_meta(conn, "sim_minute") or "360")
            conn.execute(
                """
                UPDATE shared_action_proposals
                SET status = 'failed', simulation_status = ?,
                    outcome_text = ?, updated_minute = ?
                WHERE id = ?
                """,
                (
                    start.get("status"),
                    start.get("reason") or "Simulation did not start the accepted activity.",
                    now,
                    int(proposal_id),
                ),
            )
            conn.commit()
        return False, start.get("reason") or "Simulation rejected the shared activity.", proposal_payload(proposal_id, sync=False)

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        conn.execute(
            """
            UPDATE shared_action_proposals
            SET status = 'started',
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
                start["action_id"],
                start.get("status") or "active",
                start.get("progress"),
                start.get("start_minute"),
                start.get("end_minute"),
                json.dumps(start.get("observation_ids") or []),
                start.get("outcome"),
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
