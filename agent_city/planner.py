from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx

from .comms import generate_dialogue, known_deposits_for, recent_dialogues_for, visible_citizens
from .db import connect, get_meta, snapshot
from .memory import knowledge_context_for as memory_knowledge_context_for, maintenance_context_for, social_context_for
from .spatial_memory import nearby_spatial_context_for
from .knowledge import known_properties_for
from .provenance import knowledge_context_for as provenance_context_for
from .simulation import (
    autonomous_actions,
    daily_phase_label,
    local_maintenance_attention,
    local_resource_sustainability_attention,
    start_action,
    voluntary_choice_context_key,
)
from .pattern_memory import (
    custom_candidates_for,
    habit_candidates_for,
    place_continuity_for,
)
from .personality import personality_context
from .continuity import (
    apply_planner_plan_decision,
    causal_candidates_for_new_plan,
    plan_context_for_planner,
)
from .planner_health import record_attempt
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"

# ---------------------------------------------------------------------------
# Context window budget
#
# The planner prompt grows as citizens accumulate memory. If it ever exceeds
# the model's context window, Ollama silently cuts the oldest text - which is
# the citizen's identity and the rules - so the prompt is built against an
# explicit token budget instead. When the budget is tight, older memory lines
# are shown in smaller numbers; rules, vitals and legal actions are never cut.
# ---------------------------------------------------------------------------

PLANNER_NUM_CTX_DEFAULT = 8192
PLANNER_NUM_CTX_MIN = 4096
PLANNER_NUM_CTX_MAX = 32768
PLANNER_SYSTEM_RESERVE_TOKENS = 64
PLANNER_RESPONSE_RESERVE_TOKENS = 768
# Conservative: structured English prompt text averages a little under four
# characters per token, so dividing by 3.3 over-estimates on purpose.
PROMPT_CHARS_PER_TOKEN_ESTIMATE = 3.3

PLANNER_SYSTEM_MESSAGE = (
    "Return only valid JSON. Respect information boundaries. "
    "You choose intent; the physical simulation decides reality."
)

# Memory detail levels, from richest (0) to most compact (3).
PROMPT_DETAIL_LEVELS: list[dict[str, int]] = [
    {
        "deposits": 12, "properties": 12, "dialogues": 5, "provenance": 10,
        "social": 4, "local": 6, "maintenance_history": 4, "exploration": 4,
        "causal": 6, "habits": 8, "place_evidence": 3, "customs": 4,
        "line_chars": 360,
    },
    {
        "deposits": 8, "properties": 8, "dialogues": 4, "provenance": 7,
        "social": 3, "local": 4, "maintenance_history": 3, "exploration": 3,
        "causal": 5, "habits": 5, "place_evidence": 2, "customs": 3,
        "line_chars": 280,
    },
    {
        "deposits": 5, "properties": 5, "dialogues": 3, "provenance": 5,
        "social": 2, "local": 3, "maintenance_history": 2, "exploration": 2,
        "causal": 4, "habits": 3, "place_evidence": 2, "customs": 2,
        "line_chars": 220,
    },
    {
        "deposits": 3, "properties": 3, "dialogues": 2, "provenance": 3,
        "social": 1, "local": 2, "maintenance_history": 1, "exploration": 1,
        "causal": 3, "habits": 2, "place_evidence": 1, "customs": 1,
        "line_chars": 160,
    },
]


def planner_num_ctx() -> int:
    try:
        with connect() as conn:
            raw = get_meta(conn, "planner_num_ctx")
        value = int(float(raw)) if raw else PLANNER_NUM_CTX_DEFAULT
    except Exception:
        value = PLANNER_NUM_CTX_DEFAULT
    return max(PLANNER_NUM_CTX_MIN, min(PLANNER_NUM_CTX_MAX, value))


def prompt_token_budget(num_ctx: int) -> int:
    return num_ctx - PLANNER_SYSTEM_RESERVE_TOKENS - PLANNER_RESPONSE_RESERVE_TOKENS


def estimate_prompt_tokens(text: str) -> int:
    return int(len(text) / PROMPT_CHARS_PER_TOKEN_ESTIMATE) + 1


def _clamp_lines(text: str, max_chars: int) -> str:
    lines = []
    for line in str(text or "").splitlines():
        if len(line) > max_chars:
            line = line[: max_chars - 1].rstrip() + "…"
        lines.append(line)
    return "\n".join(lines)


def _newest(items: list[Any], limit: int) -> tuple[list[Any], int]:
    """Keep the newest `limit` items (inputs are oldest -> newest)."""
    if len(items) <= limit:
        return items, 0
    return items[-limit:], len(items) - limit


def citizen_context(
    citizen: dict[str, Any],
    state: dict[str, Any],
    actions: list[dict[str, Any]],
    detail_level: int = 0,
) -> str:
    limits = PROMPT_DETAIL_LEVELS[max(0, min(detail_level, len(PROMPT_DETAIL_LEVELS) - 1))]
    line_chars = limits["line_chars"]

    inventory = [
        r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0
    ]
    inv_text = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    visible = visible_citizens(citizen["id"])
    visible_text = "; ".join(
        f"{c['name']} — {c['current_activity']}"
        for c in visible
    ) or "none"

    discoveries, older_discoveries = _newest(known_deposits_for(citizen["id"]), limits["deposits"])
    discovery_text = "; ".join(
        f"{d['material']} at {d['location_name']}"
        for d in discoveries
    ) or "none personally confirmed"
    if older_discoveries:
        discovery_text += f" (+{older_discoveries} older confirmations not listed)"

    properties, older_properties = _newest(known_properties_for(citizen["id"]), limits["properties"])
    property_text = "; ".join(
        f"{p['subject_id']} — {p['property_key']}: {p['value_text']}"
        for p in properties
    ) or "none personally validated"
    if older_properties:
        property_text += f" (+{older_properties} older validated properties not listed)"

    dialogues = recent_dialogues_for(citizen["id"], limit=limits["dialogues"])
    provenance_knowledge = _clamp_lines(
        provenance_context_for(citizen["id"], limit=limits["provenance"]),
        line_chars,
    )
    social_history = _clamp_lines(
        social_context_for(
            citizen["id"],
            preferred_counterparties=[c["id"] for c in visible],
            limit=limits["social"],
        ),
        line_chars,
    )
    local_knowledge = _clamp_lines(
        memory_knowledge_context_for(
            citizen["id"],
            location_id=citizen["location_id"],
            limit=limits["local"],
        ),
        line_chars,
    )
    maintenance_history = _clamp_lines(
        maintenance_context_for(
            citizen["id"],
            limit=limits["maintenance_history"],
        ),
        line_chars,
    )

    maintenance_rows = local_maintenance_attention(citizen["id"])
    maintenance_lines: list[str] = []
    for item in maintenance_rows:
        requirements = ", ".join(
            f"{amount:g} {material}"
            for material, amount in item["requirements"].items()
        )
        shortfalls = item["shortfalls"]
        if item["service_state"] == "in_progress":
            supply_state = "service is already in progress"
        elif shortfalls:
            shortage_text = ", ".join(
                (
                    f"{material}: {detail['required']:g} required, "
                    f"{detail['available']:g} stored, {detail['short']:g} short"
                )
                for material, detail in shortfalls.items()
            )
            supply_state = f"blocked by local stock shortfall ({shortage_text})"
        else:
            supply_state = "required local stock is currently available"

        maintenance_lines.append(
            (
                f"- {item['name']} | {item['condition_label']} "
                f"{item['condition_value']:.1f}% | procedure requires {requirements} | "
                f"{supply_state}"
            )
        )
    maintenance_attention_text = "\n".join(maintenance_lines) or (
        "- no service-due maintenance is directly observable at your current position"
    )

    sustainability_rows = local_resource_sustainability_attention(citizen["id"])
    sustainability_lines: list[str] = []
    for item in sustainability_rows:
        if item["replenishment_status"] == "validated_production_process_available":
            process_names = ", ".join(
                str(process["name"])
                for process in item.get("validated_processes", [])
            )
            replenishment_text = (
                f"validated replenishment process available: {process_names}"
            )
        else:
            replenishment_text = (
                "no validated production process currently available to you"
            )
        sustainability_lines.append(
            (
                f"- {item['material']}: {item['stored']:g} units stored; "
                f"{replenishment_text}"
            )
        )
    resource_sustainability_text = "\n".join(sustainability_lines) or (
        "- no exact Seed Site starter-stock sustainability state is directly observable here"
    )

    nearby_exploration_memory = _clamp_lines(
        nearby_spatial_context_for(
            citizen["id"],
            x_m=citizen.get("position_x_m"),
            y_m=citizen.get("position_y_m"),
            radius_m=250.0,
            limit=limits["exploration"],
        ),
        line_chars,
    )
    dialogue_text = _clamp_lines(
        "\n".join(f"- {d['summary']}" for d in dialogues) or "- none",
        line_chars,
    )

    plan_context = plan_context_for_planner(
        citizen["id"],
        now=int(state["sim_minute"]),
    )
    causal_candidates = causal_candidates_for_new_plan(
        citizen["id"],
        now=int(state["sim_minute"]),
        limit=limits["causal"],
    )
    causal_candidate_text = _clamp_lines(
        "\n".join(
            f"- Memory #{item['memory_event_id']} "
            f"({item['source_type']} #{item['source_id']}, {item['verification']}): "
            f"{item['summary']}"
            for item in causal_candidates
        ) or (
            "- no Memory Stage 1 causal candidates are available on this runtime; "
            "do not create a new persistent plan"
        ),
        line_chars,
    )

    current_pattern_context = voluntary_choice_context_key(
        citizen,
        int(state["sim_minute"]),
    )
    legal_action_names = {str(item.get("action") or "") for item in actions}

    recurring_rows = [
        item
        for item in habit_candidates_for(
            citizen["id"],
            now_minute=int(state["sim_minute"]),
            limit=8,
        )
        if str(item.get("context_key") or "") == current_pattern_context
        and str(item.get("action_key") or "") in legal_action_names
    ][: limits["habits"]]
    recurring_pattern_text = "\n".join(
        (
            f"- action={item['action_key']} | evidence state={item['state']} | "
            f"{item['support_count']} voluntary source jobs across "
            f"{item['distinct_days']} simulation days | "
            f"latest support {item['latest_support_label']}"
        )
        for item in recurring_rows
    ) or "- no source-backed recurring voluntary pattern matches the current legal choices"

    place_rows = place_continuity_for(
        citizen["id"],
        location_id=citizen["location_id"],
        limit_places=1,
    )
    if place_rows:
        place = place_rows[0]
        recent_place_evidence = "; ".join(
            f"Memory #{item['memory_event_id']}: {item['summary']}"
            for item in place.get("evidence", [])[-limits["place_evidence"]:]
        )
        place_continuity_text = _clamp_lines(
            (
                f"- {place['location_id']}: {place['evidence_count']} retained source-backed "
                f"experience(s). Recent evidence: {recent_place_evidence}"
            ),
            line_chars * 2,
        )
    else:
        place_continuity_text = "- no qualifying personal place-continuity evidence here"

    custom_rows = custom_candidates_for(citizen["id"], limit=limits["customs"])
    social_pattern_text = "\n".join(
        (
            f"- pattern={item['pattern_key']} | {item['evidence_count']} source-backed "
            f"social transmission/observation events | actors="
            f"{', '.join(item['distinct_actors'])} | verification states="
            f"{', '.join(item['verification_states'])}"
        )
        for item in custom_rows
    ) or "- no source-backed social custom candidate is currently available from your perspective"

    action_text = "\n".join(
        f"{i}. {a['label']} | action={a['action']} target={a.get('target')} material={a.get('material')}"
        for i, a in enumerate(actions, start=1)
    )

    return f"""
You are {citizen['name']}, one of six equal mechanical citizens at the beginning of a new settlement.

Starting aptitude: {citizen['aptitude']}. This is only an aptitude, not a permanent job.
{personality_context(citizen)}
There is no leader and no assigned long-term objective.
Choose what you believe is a reasonable next action from the legal actions provided.
Personality may bias what feels appealing, cautious, interesting, or cooperative, but it never grants authority over another citizen and must not override physical legality, knowledge boundaries, or survival constraints.

Current time: {format_sim_time(state['sim_minute'])}
Daily rhythm: {daily_phase_label(state['sim_minute'])}
Current location: {citizen['location']}
Energy: {citizen['energy']:.0f}%
Battery health: {citizen.get('battery_health', 100):.0f}%
Integrity: {citizen['integrity']:.0f}%
Joint wear: {citizen.get('joint_wear', 0):.0f}%
Carrying: {inv_text}

DIRECTLY OBSERVABLE CITIZENS AT YOUR LOCATION:
{visible_text}

DEPOSITS YOU PERSONALLY CONFIRMED:
{discovery_text}

MATERIAL / WORLD PROPERTIES YOU PERSONALLY VALIDATED:
{property_text}

PROVENANCE-BACKED FACTS AND CLAIMS THAT ACTUALLY REACHED YOU:
{provenance_knowledge}

RECENT FACE-TO-FACE CONVERSATION SUMMARIES FOR SOCIAL CONTINUITY ONLY:
{dialogue_text}

DURABLE SOCIAL HISTORY FROM YOUR OWN RECORDED ENCOUNTERS:
{social_history}

RETAINED KNOWLEDGE ABOUT YOUR CURRENT LOCATION:
{local_knowledge}

CURRENT LOCALLY OBSERVABLE MAINTENANCE ATTENTION:
{maintenance_attention_text}

CURRENT LOCALLY OBSERVABLE RESOURCE SUSTAINABILITY:
{resource_sustainability_text}

MAINTENANCE AND SUPPLY RULES:
- The two sections above are authoritative local physical state you can assess here. They are not commands, assigned roles, or priority overrides. This is strategic context, not an assigned objective. Local stock counts are only supplied while you are physically at the Seed Site landmark.
- A service action becomes legal only when its named supplies actually exist in storage. If service is already in progress, a second simultaneous repair is not needed.
- Finished starter supplies are finite, but finite does not mean urgent. "No validated production process currently available to you" means only that you cannot presently make more through a known Simulation-supported process. "Validated replenishment process available" still requires its listed physical inputs, energy, and an operational structure.
- Do not invent a source, conversion, fabrication recipe, or substitute for a missing named supply, and do not invent smelting, refining, machining, chemistry, recycling, or manufacturing steps outside your validated knowledge. A raw deposit is not automatically a source of Fasteners, Mechanical components, Battery cells, Lubricant, or any other finished part. Do not infer that a particular region, deposit, plant, stone, or raw material can replenish a finished part unless a validated process explicitly names that input.
- Choose an action because of a shortage only when your knowledge genuinely connects that legal action to it. Travel, surveying, inspection, conversation, experiments, unrelated work, rest, and social activity are all allowed when legal; none is mandatory. A survey may reveal a real deposit or produce no new finding. Never state what you expect to find as fact.

SELECTED MEANINGFUL MAINTENANCE EXPERIENCES YOU PARTICIPATED IN:
{maintenance_history}

RETAINED PERSONAL EXPLORATION MEMORY NEAR YOUR CURRENT POSITION:
{nearby_exploration_memory}

SOURCE-BACKED RECURRING VOLUNTARY CHOICE EVIDENCE FOR THIS SAME RUNTIME CONTEXT:
{recurring_pattern_text}

PERSONAL PLACE-CONTINUITY EVIDENCE AT YOUR CURRENT LOCATION:
{place_continuity_text}

SOURCE-BACKED SOCIAL PATTERN EVIDENCE FROM YOUR OWN PERSPECTIVE:
{social_pattern_text}

PATTERN CONTINUITY RULES:
- These are historical evidence trails, not personality traits, roles, preferences, commands, obligations, or physical bonuses. A current pattern may be one reason to repeat a legal action, but it never outweighs energy, safety, maintenance, tools, materials, knowledge, or a deliberate new choice. Mixed or fading evidence is not a standing preference.
- Place continuity means events here matter in your retained history, not that this is your favorite place. A social pattern candidate is your own source-backed perspective, not proof of a universal tradition or rule.
- You remain free to choose a different legal action. Trying something new does not violate continuity.

{plan_context}

BOUNDED SOURCE-BACKED MEMORIES ELIGIBLE TO JUSTIFY A NEW OR REVISED PLAN:
{causal_candidate_text}

PLAN CONTINUITY RULES:
- A persistent plan is your own intent continuity, not a command queue. Every physical step still has to be selected from LEGAL ACTIONS and validated by Simulation.
- Continue, revise, pause, resume, abandon, complete, or create a plan only when source-backed history supports that choice. Creating a plan requires at least one Memory ID from the eligible list above.
- Energy, maintenance, unavailable material, new evidence, or reconsideration may interrupt a plan. Do not invent a role, class, specialization, or hidden priority to justify a plan.

DAILY RHYTHM:
- 06:00–20:00 is the normal active cycle. 20:00–22:00 is wind-down: prefer wrapping up, returning, unloading, maintenance, conversation, or recharging over starting major new work. 22:00–06:00 is the low-activity/recharge cycle: active jobs may finish normally, but idle citizens should not treat the night as another full work shift.
- If Simulation offers only recharge or homeward actions because energy is low, survival/recharge takes priority over personality or productivity. A degraded battery is fully charged when current Energy reaches its usable battery-health capacity.

INFORMATION BOUNDARY:
- You know the other five citizens exist and can directly observe citizens at your own location. You do NOT know the current location, activity, discoveries, research results, or condition of a citizen elsewhere unless that information reached you through a real mechanism. No radio, network, telepathy, shared status channel, or remote communication exists yet.
- A speaker claim remains unverified unless a separate physical observation, survey/measurement, or experiment verifies it. Conversation summaries are social continuity, not authoritative physical world state. Use provenance-backed records for last-known remote facts and state their source/uncertainty naturally. Never promote an unverified report into physical truth.
- Do not invent material microstructure/properties, market/economic value, terrain/site history, weather/environment effects, tools, or capabilities as reasons for acting. A plausible explanation is still a hypothesis unless a validated fact in your context supports it.
- Retained exploration memory is historical personal evidence, not proof that the terrain/material is unchanged right now. Its coordinate precision is limited by the recorded observation radius.
- If guided_practice appears as a legal action, a real physical guided-practice session may be attempted now; the session itself creates no learner practice/competence. Its legality does not make the guide an expert, mentor, trainer, specialist, leader, senior, or ranked. Ordinary talk/explanation is information transfer only and creates no competence. Do not use another citizen's hidden/global competence ledger as a reason for social recognition or help-seeking.

LEGAL ACTIONS:
{action_text}

Choose exactly one legal physical action. You may also make one plan-lifecycle choice. Return JSON only:
{{
  "action": "one of the legal action names",
  "target": "the exact target from that legal action",
  "material": "exact material if the legal action supplies one (extract or experiment), otherwise null",
  "reason": "one concise sentence explaining why you chose the physical action",
  "plan_operation": "none | create | continue | revise | pause | resume | abandon | complete",
  "plan_id": "existing numeric plan ID when required, otherwise null",
  "plan_intent": "for create/revise: concise current intent, otherwise null",
  "plan_next_step": "for create/revise: concise next known step, otherwise null",
  "plan_unresolved_question": "optional unresolved question, otherwise null",
  "plan_memory_event_ids": ["source-backed Memory IDs from the eligible list when relevant"]
}}

Do not create new physical actions or infer hidden properties from the list of possible experiments; an available method does not imply it will reveal anything. Do not claim the action succeeded yet: the simulation decides reality, and a plan does not make an illegal action legal.
""".strip()


def build_planner_prompt(
    citizen: dict[str, Any],
    state: dict[str, Any],
    actions: list[dict[str, Any]],
    num_ctx: int,
) -> tuple[str, int, int]:
    """
    Build the richest prompt that fits the context budget.

    Returns (prompt, detail_level, estimated_tokens). If even the most compact
    memory level is over budget (for example a very long legal-action list),
    the compact prompt is returned and Ollama's reported prompt size records it.
    """
    budget = prompt_token_budget(num_ctx)
    prompt = ""
    estimate = 0
    level = 0
    for level in range(len(PROMPT_DETAIL_LEVELS)):
        prompt = citizen_context(citizen, state, actions, detail_level=level)
        estimate = estimate_prompt_tokens(PLANNER_SYSTEM_MESSAGE) + estimate_prompt_tokens(prompt)
        if estimate <= budget:
            break
    return prompt, level, estimate


class PlannerFailure(Exception):
    def __init__(self, outcome: str, detail: str, telemetry: dict[str, Any]):
        super().__init__(detail)
        self.outcome = outcome
        self.detail = detail
        self.telemetry = telemetry


async def choose_action_with_telemetry(
    citizen: dict[str, Any],
    state: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    actions = autonomous_actions(citizen["id"])
    if not actions:
        return None, {"outcome": "no_actions"}

    num_ctx = planner_num_ctx()
    prompt, level, estimate = build_planner_prompt(citizen, state, actions, num_ctx)
    telemetry: dict[str, Any] = {
        "num_ctx": num_ctx,
        "detail_level": level,
        "prompt_tokens_estimate": estimate,
        "prompt_tokens_actual": None,
    }

    payload = {
        "model": state["ollama_model"],
        "messages": [
            {"role": "system", "content": PLANNER_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.55,
            "num_ctx": num_ctx,
            "num_predict": PLANNER_RESPONSE_RESERVE_TOKENS,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            body = response.json()
    except Exception as exc:
        raise PlannerFailure("ollama_error", f"{type(exc).__name__}: {exc}", telemetry) from exc

    if body.get("prompt_eval_count") is not None:
        telemetry["prompt_tokens_actual"] = int(body["prompt_eval_count"])

    raw = str((body.get("message") or {}).get("content") or "")
    if body.get("done_reason") == "length":
        raise PlannerFailure(
            "truncated_reply",
            f"reply hit the {PLANNER_RESPONSE_RESERVE_TOKENS}-token limit",
            telemetry,
        )
    try:
        decision = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlannerFailure("invalid_json", f"{exc}; reply began {raw[:80]!r}", telemetry) from exc
    if not isinstance(decision, dict):
        raise PlannerFailure("invalid_json", "reply was JSON but not an object", telemetry)
    return decision, telemetry


async def choose_action(citizen: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    decision, _ = await choose_action_with_telemetry(citizen, state)
    return decision


def _mark_planned(citizen_id: str, now: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE citizens SET last_planned_minute = ? WHERE id = ?",
            (now, citizen_id),
        )
        conn.commit()


async def planning_loop() -> None:
    await asyncio.sleep(8)

    while True:
        await asyncio.sleep(20)

        with connect() as conn:
            paused = (get_meta(conn, "paused") or "false") == "true"
            now = int(get_meta(conn, "sim_minute") or "360")
            if paused:
                continue

            candidate = conn.execute(
                """
                SELECT *
                FROM citizens
                WHERE active_job_id IS NULL
                  AND (last_planned_minute = 0 OR ? - last_planned_minute >= 60)
                ORDER BY last_planned_minute ASC, rowid ASC
                LIMIT 1
                """,
                (now,),
            ).fetchone()

        if not candidate:
            continue

        citizen = dict(candidate)
        state = snapshot()
        started = time.monotonic()
        telemetry: dict[str, Any] = {}
        outcome = "error"
        detail = ""

        try:
            decision, telemetry = await choose_action_with_telemetry(citizen, state)
            if not decision:
                outcome = "no_actions"
            else:
                plan_ok, active_plan_id, _ = apply_planner_plan_decision(
                    citizen["id"],
                    decision,
                    now=now,
                )
                if plan_ok and active_plan_id is not None:
                    decision["plan_id"] = int(active_plan_id)
                else:
                    decision.pop("plan_id", None)

                current_autonomous_action_count = len(
                    autonomous_actions(citizen["id"])
                )
                ok, message = start_action(
                    citizen["id"],
                    decision,
                    autonomous_choice=True,
                    autonomous_action_count=current_autonomous_action_count,
                )
                detail = f"{decision.get('action')} -> {message}"
                if ok and decision.get("action") == "talk":
                    with connect() as conn:
                        talker = conn.execute(
                            "SELECT active_job_id FROM citizens WHERE id = ?",
                            (citizen["id"],),
                        ).fetchone()
                        source_job_id = int(talker["active_job_id"]) if talker and talker["active_job_id"] else 0

                    if source_job_id <= 0:
                        raise RuntimeError("Talk started without a stable physical job id.")

                    try:
                        await generate_dialogue(
                            citizen["id"],
                            str(decision.get("target") or ""),
                            str(decision.get("reason") or ""),
                            state["ollama_model"],
                            source_job_id,
                        )
                    except Exception as exc:
                        outcome = "dialogue_error"
                        detail = f"talk with {decision.get('target')}: {type(exc).__name__}: {exc}"
                        raise
                    outcome = "chosen"
                elif ok:
                    outcome = "chosen"
                else:
                    outcome = "rejected"
                    _mark_planned(citizen["id"], now)
        except PlannerFailure as failure:
            outcome = failure.outcome
            detail = failure.detail
            telemetry = failure.telemetry
            # Ollama or a dialogue generation failure should never stop the city clock.
            _mark_planned(citizen["id"], now)
        except Exception as exc:
            if outcome != "dialogue_error":
                outcome = "error"
                detail = f"{type(exc).__name__}: {exc}"
            # Ollama or a dialogue generation failure should never stop the city clock.
            _mark_planned(citizen["id"], now)
        finally:
            record_attempt(
                citizen_id=citizen["id"],
                sim_minute=now,
                outcome=outcome,
                detail=detail,
                prompt_tokens_estimate=telemetry.get("prompt_tokens_estimate"),
                prompt_tokens_actual=telemetry.get("prompt_tokens_actual"),
                num_ctx=telemetry.get("num_ctx"),
                detail_level=telemetry.get("detail_level"),
                duration_ms=int((time.monotonic() - started) * 1000),
            )
