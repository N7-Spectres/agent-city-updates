from __future__ import annotations

import json
import math
from typing import Any

from .db import add_history, get_meta

COMPETENCE_FAMILIES: dict[str, set[str]] = {
    "surveying": {"survey"},
    "extraction": {"extract"},
    "experimentation": {"experiment"},
    "fabrication": {"fabricate"},
    "construction": {"construct"},
    "maintenance": {
        "service_chassis",
        "replace_battery",
        "service_equipment",
        "service_structure",
    },
}

MAX_PRACTICE_DURATION_BENEFIT = 0.08
GUIDANCE_DURATION_MULTIPLIER = 0.96
MAX_COMBINED_DURATION_BENEFIT = 0.10
GUIDED_PRACTICE_DURATION = 45
GUIDED_PRACTICE_ENERGY_COST = 1.0


def activity_family(action: str) -> str | None:
    action = str(action or "")
    for family, actions in COMPETENCE_FAMILIES.items():
        if action in actions:
            return family
    return None


def _practice_weight(row: Any) -> float:
    status = str(row["job_status"] or "")
    outcome = str(row["outcome"] or "")
    if status == "failed":
        return 0.25
    if outcome in {"success", "discovery", "verified"}:
        return 1.0
    if outcome == "legacy_complete":
        return 0.75
    if outcome in {"inconclusive", "no_yield"}:
        return 0.50
    return 0.75 if status == "complete" else 0.0


def competence_evidence(conn, citizen_id: str, family: str) -> dict[str, Any]:
    actions = sorted(COMPETENCE_FAMILIES.get(family, set()))
    if not actions:
        return {
            "family": family,
            "practice_count": 0,
            "completed_count": 0,
            "failed_count": 0,
            "weighted_evidence": 0.0,
            "duration_multiplier": 1.0,
            "source_practice_event_ids": [],
        }

    placeholders = ",".join("?" for _ in actions)
    rows = conn.execute(
        f"""
        SELECT *
        FROM practice_events
        WHERE citizen_id = ?
          AND activity_type IN ({placeholders})
        ORDER BY completed_minute, id
        """,
        (citizen_id, *actions),
    ).fetchall()

    weighted = sum(_practice_weight(row) for row in rows)
    benefit = min(
        MAX_PRACTICE_DURATION_BENEFIT,
        0.02 * math.log2(1.0 + max(0.0, weighted)),
    )
    return {
        "family": family,
        "practice_count": len(rows),
        "completed_count": sum(1 for row in rows if str(row["job_status"]) == "complete"),
        "failed_count": sum(1 for row in rows if str(row["job_status"]) == "failed"),
        "weighted_evidence": round(weighted, 4),
        "duration_multiplier": round(1.0 - benefit, 6),
        "source_practice_event_ids": [int(row["id"]) for row in rows],
    }


def competence_snapshot(conn, citizen_id: str) -> list[dict[str, Any]]:
    return [
        competence_evidence(conn, citizen_id, family)
        for family in sorted(COMPETENCE_FAMILIES)
    ]


def pending_guidance(conn, learner_id: str, family: str):
    return conn.execute(
        """
        SELECT *
        FROM guided_practice_sessions
        WHERE learner_id = ?
          AND activity_family = ?
          AND status = 'complete'
          AND consumed_by_job_id IS NULL
        ORDER BY completed_minute DESC, id DESC
        LIMIT 1
        """,
        (learner_id, family),
    ).fetchone()


def duration_effect_for_action(conn, citizen_id: str, action: str) -> dict[str, Any]:
    family = activity_family(action)
    if not family:
        return {
            "family": None,
            "practice_duration_multiplier": 1.0,
            "guidance_duration_multiplier": 1.0,
            "combined_duration_multiplier": 1.0,
            "guidance_session_id": None,
            "source_practice_event_ids": [],
        }

    evidence = competence_evidence(conn, citizen_id, family)
    guidance = pending_guidance(conn, citizen_id, family)
    practice_mult = float(evidence["duration_multiplier"])
    guidance_mult = GUIDANCE_DURATION_MULTIPLIER if guidance else 1.0
    combined = practice_mult * guidance_mult
    combined = max(1.0 - MAX_COMBINED_DURATION_BENEFIT, combined)
    return {
        "family": family,
        "practice_duration_multiplier": practice_mult,
        "guidance_duration_multiplier": guidance_mult,
        "combined_duration_multiplier": round(combined, 6),
        "guidance_session_id": int(guidance["id"]) if guidance else None,
        "source_practice_event_ids": list(evidence["source_practice_event_ids"]),
    }


def consume_guidance_for_job(conn, guidance_session_id: int | None, job_id: int) -> None:
    if guidance_session_id is None:
        return
    conn.execute(
        """
        UPDATE guided_practice_sessions
        SET consumed_by_job_id = ?
        WHERE id = ?
          AND status = 'complete'
          AND consumed_by_job_id IS NULL
        """,
        (int(job_id), int(guidance_session_id)),
    )


def _physically_close(a: Any, b: Any, radius_m: float = 2.0) -> bool:
    if a["location_id"] != b["location_id"]:
        return False
    return math.hypot(
        float(a["position_x_m"] or 0.0) - float(b["position_x_m"] or 0.0),
        float(a["position_y_m"] or 0.0) - float(b["position_y_m"] or 0.0),
    ) <= radius_m


def best_guided_practice_option(conn, teacher_id: str, learner_id: str) -> dict[str, Any] | None:
    teacher = conn.execute("SELECT * FROM citizens WHERE id = ?", (teacher_id,)).fetchone()
    learner = conn.execute("SELECT * FROM citizens WHERE id = ?", (learner_id,)).fetchone()
    if not teacher or not learner:
        return None
    if teacher["active_job_id"] is not None or learner["active_job_id"] is not None:
        return None
    if not _physically_close(teacher, learner):
        return None

    candidates = []
    for family in sorted(COMPETENCE_FAMILIES):
        teacher_ev = competence_evidence(conn, teacher_id, family)
        learner_ev = competence_evidence(conn, learner_id, family)
        gap = float(teacher_ev["weighted_evidence"]) - float(learner_ev["weighted_evidence"])
        if float(teacher_ev["weighted_evidence"]) >= 1.0 and gap > 0:
            candidates.append((gap, family, teacher_ev, learner_ev))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], item[1]))
    gap, family, teacher_ev, learner_ev = candidates[0]
    return {
        "family": family,
        "teacher_weighted_evidence": teacher_ev["weighted_evidence"],
        "learner_weighted_evidence": learner_ev["weighted_evidence"],
        "evidence_gap": round(gap, 4),
    }


def start_guided_practice(
    conn,
    teacher_id: str,
    learner_id: str,
    family: str,
    *,
    now: int | None = None,
    source_conversation_id: int | None = None,
) -> tuple[bool, int | None, str]:
    if family not in COMPETENCE_FAMILIES:
        return False, None, "Unsupported guided-practice family."
    if teacher_id == learner_id:
        return False, None, "Guided practice requires two different citizens."

    teacher = conn.execute("SELECT * FROM citizens WHERE id = ?", (teacher_id,)).fetchone()
    learner = conn.execute("SELECT * FROM citizens WHERE id = ?", (learner_id,)).fetchone()
    if not teacher or not learner:
        return False, None, "Teacher or learner citizen not found."
    if teacher["active_job_id"] is not None or learner["active_job_id"] is not None:
        return False, None, "Both citizens must be physically available."
    if not _physically_close(teacher, learner):
        return False, None, "Guided practice requires physical co-presence."
    if float(teacher["energy"]) < GUIDED_PRACTICE_ENERGY_COST or float(learner["energy"]) < GUIDED_PRACTICE_ENERGY_COST:
        return False, None, "Both citizens need enough energy for guided practice."

    teacher_ev = competence_evidence(conn, teacher_id, family)
    learner_ev = competence_evidence(conn, learner_id, family)
    if float(teacher_ev["weighted_evidence"]) < 1.0:
        return False, None, "The proposed guide has no real practice evidence in this activity family."
    if float(teacher_ev["weighted_evidence"]) <= float(learner_ev["weighted_evidence"]):
        return False, None, "Guided practice requires the guide to have more relevant practice evidence than the learner."

    if source_conversation_id is not None:
        convo = conn.execute(
            """
            SELECT * FROM citizen_conversations
            WHERE id = ?
              AND (
                  (initiator_id = ? AND target_id = ?)
                  OR
                  (initiator_id = ? AND target_id = ?)
              )
            """,
            (
                int(source_conversation_id),
                teacher_id,
                learner_id,
                learner_id,
                teacher_id,
            ),
        ).fetchone()
        if not convo:
            return False, None, "Guided-practice source conversation does not belong to these citizens."

    minute = int(now) if now is not None else int(get_meta(conn, "sim_minute") or "360")
    cur = conn.execute(
        """
        INSERT INTO guided_practice_sessions
        (teacher_id, learner_id, activity_family, status, started_minute,
         source_conversation_id, teacher_practice_count, learner_practice_count,
         summary)
        VALUES (?, ?, ?, 'active', ?, ?, ?, ?, ?)
        """,
        (
            teacher_id,
            learner_id,
            family,
            minute,
            source_conversation_id,
            int(teacher_ev["practice_count"]),
            int(learner_ev["practice_count"]),
            (
                f"{teacher['name']} is guiding {learner['name']} through "
                f"a {family} practice session."
            ),
        ),
    )
    session_id = int(cur.lastrowid)
    job = conn.execute(
        """
        INSERT INTO jobs
        (citizen_id, action, target, start_minute, end_minute, status, detail,
         intent_reason, guided_practice_id)
        VALUES (?, 'guided_practice', ?, ?, ?, 'active', ?, ?, ?)
        """,
        (
            teacher_id,
            learner_id,
            minute,
            minute + GUIDED_PRACTICE_DURATION,
            json.dumps(
                {
                    "learner_id": learner_id,
                    "activity_family": family,
                    "source_conversation_id": source_conversation_id,
                },
                separators=(",", ":"),
            ),
            f"Guide {learner['name']} through real {family} practice preparation.",
            session_id,
        ),
    )
    job_id = int(job.lastrowid)
    conn.execute(
        """
        UPDATE guided_practice_sessions
        SET job_id = ?
        WHERE id = ?
        """,
        (job_id, session_id),
    )
    conn.execute(
        """
        UPDATE citizens
        SET active_job_id = ?, current_activity = ?, energy = MAX(0, energy - ?)
        WHERE id = ?
        """,
        (
            job_id,
            f"Guiding {learner['name']} through {family} practice",
            GUIDED_PRACTICE_ENERGY_COST,
            teacher_id,
        ),
    )
    conn.execute(
        """
        UPDATE citizens
        SET active_job_id = ?, current_activity = ?, energy = MAX(0, energy - ?)
        WHERE id = ?
        """,
        (
            job_id,
            f"Practicing {family} with {teacher['name']}",
            GUIDED_PRACTICE_ENERGY_COST,
            learner_id,
        ),
    )
    add_history(
        conn,
        minute,
        "continuity",
        (
            f"{teacher['name']} and {learner['name']} began guided "
            f"{family} practice session #{session_id}."
        ),
    )
    return True, job_id, "Guided practice started."


def guided_practice_snapshot(conn, citizen_id: str, *, limit: int = 30) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            """
            SELECT *
            FROM guided_practice_sessions
            WHERE teacher_id = ? OR learner_id = ?
            ORDER BY COALESCE(completed_minute, started_minute) DESC, id DESC
            LIMIT ?
            """,
            (citizen_id, citizen_id, max(1, min(int(limit), 80))),
        ).fetchall()
    ]
