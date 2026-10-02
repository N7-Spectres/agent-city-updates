from __future__ import annotations

from collections import defaultdict
from typing import Any

from .db import connect, get_meta
from .world import format_sim_time

MAX_SELF_CONTEXT_CHARS = 1800
MAX_RECOGNITION_CONTEXT_CHARS = 1600
MAX_PLAN_CONTEXT_CHARS = 1500
MAX_COMPETENCE_CONTEXT_CHARS = 900
MAX_GUIDANCE_CONTEXT_CHARS = 1250
MAX_PATTERN_CONTEXT_CHARS = 2200

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


def _practice_recall_snapshot(
    citizen_id: str,
    *,
    activity: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """
    Model-facing practice evidence must come through Memory active recall.

    The full Simulation practice ledger is objective archive/history only.
    """
    try:
        from .practice_memory import practice_recall_snapshot_for
    except ImportError:
        return []

    try:
        rows = practice_recall_snapshot_for(
            citizen_id,
            activity=activity,
            limit=max(1, min(int(limit), 16)),
        )
    except Exception:
        return []

    return [dict(row) for row in rows]


def _practice_recall_context(
    citizen_id: str,
    *,
    activity: str | None = None,
    limit: int = 6,
) -> str:
    try:
        from .practice_memory import practice_recall_context_for
    except ImportError:
        return "- no actively recalled source-backed physical practice matching this subject"

    try:
        return str(
            practice_recall_context_for(
                citizen_id,
                activity=activity,
                limit=max(1, min(int(limit), 12)),
            )
        )
    except Exception:
        return "- no actively recalled source-backed physical practice matching this subject"


def _activity_values_from_recall(memories: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for memory in memories:
        for facet in memory.get("facets") or []:
            if str(facet.get("kind")) != "activity":
                continue
            value = str(facet.get("value") or "").strip()
            if value and value not in values:
                values.append(value)
    return values


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


def _guided_practice_recall(
    citizen_id: str,
    *,
    family: str | None = None,
    counterpart_id: str | None = None,
    role: str | None = None,
    limit: int = 8,
) -> list[dict[str, Any]]:
    try:
        from .guided_practice_memory import guided_practice_recall_snapshot_for
    except ImportError:
        return []

    try:
        rows = guided_practice_recall_snapshot_for(
            citizen_id,
            family=family,
            counterpart_id=counterpart_id,
            role=role,
            limit=max(1, min(int(limit), 16)),
        )
    except Exception:
        return []
    return [dict(row) for row in rows]


def _guided_practice_recall_context(
    citizen_id: str,
    *,
    family: str | None = None,
    counterpart_id: str | None = None,
    role: str | None = None,
    limit: int = 6,
) -> str:
    try:
        from .guided_practice_memory import guided_practice_recall_context_for
    except ImportError:
        return "- no actively recalled source-backed guided-practice experience matched"

    try:
        return str(
            guided_practice_recall_context_for(
                citizen_id,
                family=family,
                counterpart_id=counterpart_id,
                role=role,
                limit=max(1, min(int(limit), 12)),
            )
        )
    except Exception:
        return "- no actively recalled source-backed guided-practice experience matched"


def _competence_snapshot(citizen_id: str) -> list[dict[str, Any]]:
    """
    Objective physical effect for this citizen only.

    Communication never uses this helper to inspect another citizen for social
    recognition or comparative dialogue.
    """
    try:
        from .competence import competence_snapshot
    except ImportError:
        return []

    try:
        with connect() as conn:
            rows = competence_snapshot(conn, citizen_id)
    except Exception:
        return []
    return [dict(row) for row in rows]


def _guided_practice_options(citizen_id: str, counterpart_id: str | None = None) -> list[dict[str, Any]]:
    """
    Current self-owned legal ability to guide someone.

    We consume only possible_actions(citizen_id). We never query the counterpart's
    hidden/global competence ledger to tell the speaker what the other citizen
    can or cannot teach.
    """
    try:
        from .simulation import possible_actions
    except ImportError:
        return []

    try:
        rows = possible_actions(citizen_id)
    except Exception:
        return []

    options: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("action")) != "guided_practice":
            continue
        learner_id = str(row.get("learner_id") or "")
        if counterpart_id is not None and learner_id != str(counterpart_id):
            continue
        family = str(row.get("activity_family") or "").strip()
        if not learner_id or not family:
            continue
        options.append({
            "learner_id": learner_id,
            "activity_family": family,
            "label": " ".join(str(row.get("label") or "").split())[:220],
        })
    return options


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
    memories = _practice_recall_snapshot(
        citizen_id,
        activity=activity,
        limit=8,
    )
    recall_text = _practice_recall_context(
        citizen_id,
        activity=activity,
        limit=6,
    )

    lines = ["SELF-ASSESSMENT EVIDENCE:"]
    lines.append(recall_text)

    if memories:
        activities = _activity_values_from_recall(memories)
        if activity:
            same_activity_count = len(memories)
            if same_activity_count >= 3:
                lines.append(
                    f"- Your active recall currently contains at least 3 source-backed "
                    f"{activity} practice experiences, so ordinary wording such as "
                    f"'I've done {activity} several times' is supported."
                )
            else:
                lines.append(
                    f"- Your active recall currently contains fewer than 3 source-backed "
                    f"{activity} practice experiences; do not claim 'several times' from hidden archive history."
                )
        elif activities:
            lines.append(
                "- Recalled practice subjects presently available for self-assessment: "
                + ", ".join(activities[:6])
                + "."
            )
    else:
        lines.append(
            "- No active practice recall is available for present self-assessment."
        )

    lines.extend([
        "- This packet is bounded active Memory, not the full durable practice ledger.",
        "- Do not infer forgotten/low-salience archive history into present autobiographical recall.",
        "- You may interpret recalled successes/failures personally (for example, 'I feel more practiced' or 'I keep struggling with this'), but that interpretation is not objective capability truth.",
        "- Do not claim 'I am the expert/best/leader' from recalled practice.",
        "- Recall source/time/verification may be discussed; internal recall/reinforcement math must not be exposed.",
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
            lines.append(
                f"- {truth}, {item.get('sim_label')} "
                f"({item.get('source_type')} #{item.get('source_id')}): "
                f"{' '.join(str(item.get('summary') or '').split())[:300]}"
            )

    lines.extend([
        f"- This is your perspective evidence about {other_name}, not a civilization-wide reputation record.",
        "- Do not assign titles, rank, leadership, class, specialization, or universal expertise.",
        "- Do not use another citizen's hidden/global practice count. You may compare them to yourself only when information that legitimately reached you actually supports that comparison.",
        "- Repeated unverified reports remain unverified even when easy to recall.",
    ])
    return "\n".join(lines)[:MAX_RECOGNITION_CONTEXT_CHARS]


def measured_competence_context(citizen_id: str) -> str:
    """
    Describe only the citizen's own bounded physical task-time effects.

    Practice counts/source IDs remain in Simulation read models; model-facing
    language receives only the measured effect so archive history is not
    re-injected around Memory recall.
    """
    rows = _competence_snapshot(citizen_id)
    lines = ["MEASURED PHYSICAL PRACTICE EFFECTS (SELF ONLY):"]
    useful = []
    for row in rows:
        multiplier = float(row.get("duration_multiplier") or 1.0)
        reduction = max(0.0, (1.0 - multiplier) * 100.0)
        if reduction <= 0.001:
            continue
        useful.append((str(row.get("family") or ""), reduction))

    if not useful:
        lines.append("- no measurable practice-derived task-time effect is currently present")
    else:
        for family, reduction in useful[:6]:
            lines.append(
                f"- {family}: matching physical tasks currently have about "
                f"{reduction:.1f}% shorter duration from source-backed practice."
            )

    lines.extend([
        "- This is current Simulation-owned physical effect, not memory, title, rank, or social reputation.",
        "- Do not infer exact practice count or autobiographical details from this measured effect.",
        "- A measured effect may exist even when old practice is not currently recalled; do not invent the forgotten history.",
        "- Physical bottlenecks, legality, tools, materials, energy, and outcomes remain governed by Simulation.",
    ])
    return "\n".join(lines)[:MAX_COMPETENCE_CONTEXT_CHARS]


def guided_practice_context(
    citizen_id: str,
    *,
    counterpart_id: str | None = None,
    family: str | None = None,
    include_current_options: bool = True,
) -> str:
    counterpart_name = _citizen_name(counterpart_id) if counterpart_id else "the other citizen"
    recalled = _guided_practice_recall(
        citizen_id,
        family=family,
        counterpart_id=counterpart_id,
        limit=6,
    )
    recalled_text = _guided_practice_recall_context(
        citizen_id,
        family=family,
        counterpart_id=counterpart_id,
        limit=5,
    )
    options = (
        _guided_practice_options(citizen_id, counterpart_id)
        if include_current_options
        else []
    )

    lines = ["GUIDED PRACTICE / HELP CONTEXT:"]
    lines.append(recalled_text)

    if include_current_options and options:
        lines.append("- Real guided-practice actions you can legally start right now:")
        for option in options[:6]:
            learner_name = _citizen_name(option["learner_id"])
            lines.append(
                f"  - guide {learner_name} in {option['activity_family']}"
                + (f": {option['label']}" if option["label"] else "")
            )
    elif include_current_options:
        lines.append("- no guided-practice action with this counterpart is currently exposed as legal for you")

    if recalled and counterpart_id:
        lines.append(
            f"- You may refer to source-backed past guided-practice experiences with {counterpart_name} that are actually recalled above."
        )

    lines.extend([
        "- Teacher/learner are event roles, not permanent mentor/trainer/expert identities; activity-family labels are generic, not named procedures.",

        "- Asking a question or explaining something in ordinary conversation transfers information only; it creates no competence or practice.",
        "- You may ask another citizen about their experience even when you do not know the answer. Frame unknown experience as a question, not an assertion.",
        "- You may propose guided practice only when a legal guided-practice action appears above. The conversation proposal itself does not start the physical session.",
        "- A legal guided-practice option proves only current physical action availability; it does not justify saying you are socially known to be more experienced than the learner.",
        "- A completed guided-practice session itself is not learner practice/competence. Only the learner's later real matching task creates new practice evidence.",
        "- If remembered guidance was later applied to a real task, describe the event/history only when the source-backed recall actually supports it.",
        "- Do not call yourself or the counterpart expert, master, mentor, trainer, specialist, leader, senior, or ranked because of a guided-practice event.",
        "- Do not expose weighted evidence, competence scores, recall scores, or reinforcement counts.",
    ])
    return "\n".join(lines)[:MAX_GUIDANCE_CONTEXT_CHARS]


def help_question_context(
    speaker_id: str,
    counterpart_id: str | None,
) -> str:
    lines = ["ASKING FOR HELP / EXPLANATION:"]
    if counterpart_id:
        name = _citizen_name(counterpart_id)
        lines.append(
            f"- You may ask {name} about their experience even when you do not already know how practiced they are."
        )
        lines.append(
            "- If the separate recognition packet contains source-backed history, you may use that history honestly when asking."
        )
    else:
        lines.append("- no counterpart selected")
    lines.extend([
        "- A question is not a competence claim.",
        "- Do not justify a request using hidden/global competence data.",
        "- An answer/explanation transfers information only; physical skill requires real practice.",
    ])
    return "\n".join(lines)[:700]


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
    memories = _practice_recall_snapshot(citizen_id, limit=8)
    recall_text = _practice_recall_context(citizen_id, limit=6)
    activities = _activity_values_from_recall(memories)

    lines = ["TEACHING / EXPLANATION BOUNDARY:"]
    lines.append(recall_text)

    if activities:
        lines.append(
            "- From your currently recalled source-backed practice, you may explain personal experience with: "
            + ", ".join(activities[:6])
            + "."
        )
    else:
        lines.append(
            "- No actively recalled source-backed physical practice is available as present teaching experience."
        )

    lines.extend([
        "- This teaching context uses bounded active Memory, not the full durable practice ledger.",
        "- You may explain what you personally recall doing, observing, trying, or learning from real experience.",
        "- Explaining, advising, demonstrating verbally, or being asked for help does NOT create practice or competence for the listener.",
        "- Do not claim you 'trained' or 'made someone skilled' unless a future Simulation-owned guided-practice/teaching event proves it.",
        "- A teaching conversation may create social/claim memory only; skill effects remain Simulation-owned.",
        "- Do not call yourself or another citizen an expert, master, trainer, mentor, leader, or specialist as an authoritative title.",
        "- Internal recall/reinforcement values are retrieval machinery and must not be spoken as experience metrics.",
    ])
    return "\n".join(lines)[:1600]


def _pattern_snapshot(
    citizen_id: str,
    *,
    location_id: str | None = None,
) -> dict[str, Any]:
    try:
        from .pattern_memory import continuity_pattern_snapshot
    except ImportError:
        return {"citizen_id": citizen_id, "habits": [], "places": [], "customs": []}

    try:
        payload = continuity_pattern_snapshot(citizen_id, location_id=location_id)
    except Exception:
        return {"citizen_id": citizen_id, "habits": [], "places": [], "customs": []}
    return dict(payload) if isinstance(payload, dict) else {
        "citizen_id": citizen_id,
        "habits": [],
        "places": [],
        "customs": [],
    }


def transmittable_pattern_catalog(citizen_id: str) -> list[dict[str, str]]:
    """
    Patterns this citizen may legitimately describe as their own remembered
    recurring/social history.

    The catalog constrains claim extraction. The model may select one of these
    keys, but it may not invent a new pattern key through conversation.
    """
    payload = _pattern_snapshot(citizen_id)
    rows: list[dict[str, str]] = []

    for item in payload.get("habits") or []:
        action = str(item.get("action_key") or "").strip()
        context = str(item.get("context_key") or "").strip()
        state = str(item.get("state") or "").strip()
        if not action or not context or state not in {"current", "mixed", "fading"}:
            continue
        rows.append({
            "pattern_key": f"habit:{action}|{context}",
            "kind": "recurring_choice",
            "context_key": context,
            "description": (
                f"source-backed recurring choice of {action} in {context}; "
                f"evidence state {state}"
            ),
        })

    for item in payload.get("customs") or []:
        key = str(item.get("pattern_key") or "").strip()
        if not key:
            continue
        rows.append({
            "pattern_key": key,
            "kind": "social_pattern",
            "context_key": "",
            "description": (
                f"owner-perspective social pattern supported by "
                f"{int(item.get('evidence_count') or 0)} source events"
            ),
        })

    # Deduplicate while preserving the stronger first description.
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for row in rows:
        if row["pattern_key"] in seen:
            continue
        seen.add(row["pattern_key"])
        result.append(row)
    return result[:12]


def pattern_continuity_context(
    citizen_id: str,
    *,
    location_id: str | None = None,
) -> str:
    payload = _pattern_snapshot(citizen_id, location_id=location_id)
    habits = list(payload.get("habits") or [])
    places = list(payload.get("places") or [])
    customs = list(payload.get("customs") or [])

    lines = ["RECURRING HISTORY / PLACE CONTINUITY / SOCIAL PATTERN EVIDENCE:"]

    if habits:
        lines.append("- Personal recurring-choice evidence:")
        for item in habits[:6]:
            state = str(item.get("state") or "mixed")
            action = str(item.get("action_key") or "unknown")
            context = str(item.get("context_key") or "unknown context")
            support = int(item.get("support_count") or 0)
            days = int(item.get("distinct_days") or 0)
            lines.append(
                f"  - {action} in {context}: evidence state {state}; "
                f"{support} source-backed voluntary choices across {days} simulation day(s)."
            )
    else:
        lines.append("- no qualifying source-backed recurring voluntary-choice pattern")

    if places:
        lines.append("- Personal place continuity:")
        for place in places[:3]:
            location = str(place.get("location_id") or "unknown")
            count = int(place.get("evidence_count") or 0)
            evidence = list(place.get("evidence") or [])
            recent = "; ".join(
                " ".join(str(row.get("summary") or "").split())[:180]
                for row in evidence[-2:]
            )
            lines.append(
                f"  - {location}: {count} retained source-backed experience(s)"
                + (f"; recent evidence: {recent}" if recent else "")
            )
    else:
        lines.append("- no qualifying personal place-continuity evidence in this scope")

    if customs:
        lines.append("- Owner-perspective social pattern candidates:")
        for item in customs[:4]:
            key = str(item.get("pattern_key") or "unknown")
            actors = ", ".join(str(v) for v in item.get("distinct_actors") or [])
            modes = ", ".join(str(v) for v in item.get("transmission_modes") or [])
            verification = ", ".join(str(v) for v in item.get("verification_states") or [])
            lines.append(
                f"  - {key}: source-backed social pattern evidence involving "
                f"{actors or 'unknown actors'} via {modes or 'recorded transmission'}; "
                f"verification states: {verification or 'unknown'}."
            )
    else:
        lines.append("- no qualifying owner-perspective social custom candidate")

    lines.extend([
        "- These are evidence trails, not personality traits, preferences, roles, obligations, or commands.",
        "- For a current recurring pattern, natural wording such as 'I seem to keep choosing this here' is allowed. Mixed/fading evidence should be described as changing or historical rather than a standing preference.",
        "- Place continuity means this location matters in retained personal history only because of the cited experiences. Do not call it a favorite, home, safe place, sacred place, or emotionally important unless source evidence separately supports that claim.",
        "- Social pattern evidence is perspective-specific. Do not automatically call it a tradition, custom, rule, or something everyone does.",
        "- Repeated unverified reports remain unverified. Repetition improves continuity, not truth.",
        "- Talking about a pattern can transmit a claim, but conversation alone cannot create the underlying behavior pattern.",
    ])

    return "\n".join(lines)[:MAX_PATTERN_CONTEXT_CHARS]


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
        "patterns": _pattern_snapshot(citizen_id),
        "rules": {
            "global_reputation": False,
            "authoritative_titles": False,
            "conversation_grants_skill": False,
            "self_assessment_is_interpretation": True,
            "other_recognition_requires_owner_scoped_memory": True,
            "pattern_evidence_is_not_identity": True,
            "place_evidence_is_not_favorite": True,
            "custom_evidence_is_owner_perspective": True,
        },
    }
