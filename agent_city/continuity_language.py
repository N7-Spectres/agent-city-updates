from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .db import connect, get_meta
from .world import format_sim_time

MAX_SELF_CONTEXT_CHARS = 1800
MAX_RECOGNITION_CONTEXT_CHARS = 1600
MAX_PLAN_CONTEXT_CHARS = 1500

_FAIL_OUTCOMES = {
    "failed",
    "no_yield",
    "rejected",
    "cancelled",
    "canceled",
}


def _practice_snapshot(citizen_id: str, *, limit: int = 120) -> list[dict[str, Any]]:
    try:
        from .continuity import practice_snapshot_for
    except ImportError:
        return []

    try:
        rows = practice_snapshot_for(citizen_id, limit=max(1, min(int(limit), 120)))
    except Exception:
        return []

    return [dict(row) for row in rows]


def _plan_snapshot(citizen_id: str, *, include_closed: bool = False, limit: int = 6) -> list[dict[str, Any]]:
    try:
        from .continuity import plan_snapshot_for
    except ImportError:
        return []

    try:
        rows = plan_snapshot_for(
            citizen_id,
            include_closed=include_closed,
            limit=max(1, min(int(limit), 12)),
        )
    except Exception:
        return []

    return [dict(row) for row in rows]


def _causal_recall(
    owner_id: str,
    *,
    facet_filters: dict[str, str] | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    try:
        from .causal_memory import causal_recall_snapshot
    except ImportError:
        return []

    try:
        return [
            dict(item)
            for item in causal_recall_snapshot(
                owner_id,
                facet_filters=facet_filters,
                limit=max(1, min(int(limit), 16)),
            )
        ]
    except Exception:
        return []


def _citizen_name(citizen_id: str) -> str:
    with connect() as conn:
        row = conn.execute(
            "SELECT name FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
    return str(row["name"]) if row else citizen_id


def _has_activity_facet(memory: dict[str, Any], activity: str) -> bool:
    key = str(activity or "").strip()
    if not key:
        return True
    return any(
        str(facet.get("kind")) == "activity"
        and str(facet.get("value")) == key
        for facet in memory.get("facets") or []
    )


def own_practice_summary(citizen_id: str) -> list[dict[str, Any]]:
    """
    Summarize objective personal practice history without creating competence.

    Counts describe completed/failed physical practice events only. They are not
    XP, levels, classes, or a hidden expertise score.
    """
    rows = _practice_snapshot(citizen_id)
    by_activity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        activity = str(row.get("activity_type") or "").strip()
        if activity:
            by_activity[activity].append(row)

    result: list[dict[str, Any]] = []
    for activity, events in by_activity.items():
        ordered = sorted(
            events,
            key=lambda item: (
                int(item.get("completed_minute") or 0),
                int(item.get("id") or 0),
            ),
        )
        failed = sum(
            1
            for item in ordered
            if str(item.get("job_status") or "") == "failed"
            or str(item.get("outcome") or "") in _FAIL_OUTCOMES
        )
        completed = sum(
            1 for item in ordered
            if str(item.get("job_status") or "") == "complete"
        )
        last = ordered[-1]
        result.append({
            "activity": activity,
            "practice_count": len(ordered),
            "completed_count": completed,
            "failed_count": failed,
            "last_practice_event_id": int(last["id"]),
            "last_job_id": int(last["job_id"]),
            "last_completed_minute": int(last["completed_minute"]),
            "last_outcome": str(last.get("outcome") or last.get("job_status") or ""),
            # Language permission only, not a skill tier.
            "may_say_several_times": len(ordered) >= 3,
        })

    result.sort(
        key=lambda item: (
            -int(item["practice_count"]),
            -int(item["last_completed_minute"]),
            item["activity"],
        )
    )
    return result


def self_assessment_context(citizen_id: str, *, activity: str | None = None) -> str:
    summaries = own_practice_summary(citizen_id)
    if activity:
        summaries = [item for item in summaries if item["activity"] == activity]

    lines = ["SELF-ASSESSMENT EVIDENCE:"]
    if not summaries:
        lines.append("- no recorded physical practice matching this subject")
    else:
        for item in summaries[:6]:
            last_label = format_sim_time(int(item["last_completed_minute"]))
            lines.append(
                f"- {item['activity']}: {item['practice_count']} recorded physical practice "
                f"event(s); {item['completed_count']} complete, {item['failed_count']} failed; "
                f"latest {last_label} with outcome {item['last_outcome']}."
            )

    lines.extend([
        "- These counts describe your own real practice history. They are not XP, level, rank, role, title, or guaranteed competence.",
        "- You may say you have done an activity several times only when that activity has at least 3 recorded practice events.",
        "- You may interpret repeated successes/failures personally (for example, 'I feel more practiced' or 'I keep struggling with this'), but that self-assessment is a belief, not objective capability truth.",
        "- Do not claim 'I am the expert/best/leader' from practice history.",
    ])

    return "\n".join(lines)[:MAX_SELF_CONTEXT_CHARS]


def recognition_context(
    speaker_id: str,
    other_id: str,
    *,
    activity: str | None = None,
    limit: int = 6,
) -> str:
    """
    Perspective-safe recognition about another citizen.

    Uses only Memory owned by the speaker. It never reads the other citizen's
    global practice_events directly, so recognition cannot bypass information
    travel.
    """
    other_name = _citizen_name(other_id)
    memories = _causal_recall(
        speaker_id,
        facet_filters={"counterparty": other_id},
        limit=max(limit * 2, 8),
    )
    if activity:
        memories = [item for item in memories if _has_activity_facet(item, activity)]
    memories = memories[: max(1, limit)]

    lines = [f"PERSPECTIVE-SAFE RECOGNITION OF {other_name.upper()}:"]
    if not memories:
        lines.append(
            f"- you have no source-backed personal recall that supports an assessment of {other_name}"
            + (f" for {activity}" if activity else "")
        )
    else:
        for item in memories:
            truth = "verified experience" if item.get("verification") == "verified" else "remembered/report"
            reinforcement = int(item.get("reinforcement_count") or 1)
            repeated = f"; related recall x{reinforcement}" if reinforcement > 1 else ""
            lines.append(
                f"- {truth}, {item.get('sim_label')} "
                f"({item.get('source_type')} #{item.get('source_id')}{repeated}): "
                f"{' '.join(str(item.get('summary') or '').split())[:300]}"
            )

    lines.extend([
        f"- This is your perspective evidence about {other_name}, not a civilization-wide reputation record.",
        "- Do not assign titles, rank, leadership, class, specialization, or universal expertise.",
        "- Do not use another citizen's hidden/global practice count. You may compare them to yourself only when information that legitimately reached you actually supports that comparison.",
        "- Repeated unverified reports remain unverified even when easy to recall.",
    ])
    return "\n".join(lines)[:MAX_RECOGNITION_CONTEXT_CHARS]


def plan_discussion_context(citizen_id: str) -> str:
    plans = _plan_snapshot(citizen_id, include_closed=False, limit=4)
    lines = ["PERSISTENT PLAN DISCUSSION:"]
    if not plans:
        lines.append("- no active or paused canonical plan")
    else:
        for plan in plans:
            lines.append(
                f"- Plan #{plan['id']} [{plan['status']}]: {plan['current_intent']} "
                f"| next: {plan['next_step']} "
                f"| unresolved: {plan.get('unresolved_question') or 'none'}"
            )
    lines.extend([
        "- A plan is continuing intent, not competence and not proof that the next step will succeed.",
        "- Conversation may discuss, question, or suggest revising a plan, but speaking about it does not create, complete, pause, revise, resume, abandon, or supersede the canonical plan.",
        "- Only the Simulation/planner plan lifecycle may change canonical plan state.",
    ])
    return "\n".join(lines)[:MAX_PLAN_CONTEXT_CHARS]


def teaching_boundary_context(citizen_id: str) -> str:
    summaries = own_practice_summary(citizen_id)
    practiced = [item for item in summaries if int(item["practice_count"]) > 0]

    lines = ["TEACHING / EXPLANATION BOUNDARY:"]
    if practiced:
        lines.append(
            "- You have personal physical experience you may explain for: "
            + ", ".join(
                f"{item['activity']} ({item['practice_count']} practice event"
                f"{'s' if item['practice_count'] != 1 else ''})"
                for item in practiced[:5]
            )
            + "."
        )
    else:
        lines.append("- no source-backed physical practice is available as personal teaching experience")

    lines.extend([
        "- You may explain what you personally did, observed, tried, or learned from real experience.",
        "- Explaining, advising, demonstrating verbally, or being asked for help does NOT create practice or competence for the listener.",
        "- Do not claim you 'trained' or 'made someone skilled' unless a future Simulation-owned guided-practice/teaching event proves it.",
        "- A teaching conversation may create social/claim memory only; skill effects remain Simulation-owned.",
        "- Do not call yourself or another citizen an expert, master, trainer, mentor, leader, or specialist as an authoritative title.",
    ])
    return "\n".join(lines)[:1600]


def visitor_continuity_context(citizen_id: str, visitor: str, *, limit: int = 5) -> str:
    memories = _causal_recall(
        citizen_id,
        facet_filters={"visitor": visitor},
        limit=max(1, limit),
    )
    lines = [f"VISITOR CONTINUITY FOR {visitor}:"]
    if not memories:
        lines.append("- no source-backed retained visitor continuity matched")
    else:
        for item in memories:
            truth = "verified experience" if item.get("verification") == "verified" else "remembered/report"
            lines.append(
                f"- {truth}, {item.get('sim_label')} "
                f"({item.get('source_type')} #{item.get('source_id')}): "
                f"{' '.join(str(item.get('summary') or '').split())[:320]}"
            )
    lines.append(
        "- Visitor importance/familiarity comes from real visits, exchanges, and shared activities; UI/account ownership creates no social authority."
    )
    return "\n".join(lines)[:1600]


def continuity_language_snapshot(citizen_id: str) -> dict[str, Any]:
    """
    Debug/read-model surface. Contains evidence summaries, not hidden scores.
    """
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
    return {
        "citizen_id": citizen_id,
        "sim_minute": now,
        "practice": own_practice_summary(citizen_id),
        "plans": _plan_snapshot(citizen_id, include_closed=False, limit=6),
        "rules": {
            "global_reputation": False,
            "authoritative_titles": False,
            "conversation_grants_skill": False,
            "self_assessment_is_interpretation": True,
            "other_recognition_requires_owner_scoped_memory": True,
        },
    }
