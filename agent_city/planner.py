from __future__ import annotations

import asyncio
import json
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
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"


def citizen_context(citizen: dict[str, Any], state: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    inventory = [
        r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0
    ]
    inv_text = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    visible = visible_citizens(citizen["id"])
    visible_text = "; ".join(
        f"{c['name']} — {c['current_activity']}"
        for c in visible
    ) or "none"

    discoveries = known_deposits_for(citizen["id"])
    discovery_text = "; ".join(
        f"{d['material']} at {d['location_name']}"
        for d in discoveries
    ) or "none personally confirmed"

    properties = known_properties_for(citizen["id"])
    property_text = "; ".join(
        f"{p['subject_id']} — {p['property_key']}: {p['value_text']}"
        for p in properties
    ) or "none personally validated"

    dialogues = recent_dialogues_for(citizen["id"], limit=5)
    provenance_knowledge = provenance_context_for(citizen["id"], limit=10)
    social_history = social_context_for(
        citizen["id"],
        preferred_counterparties=[c["id"] for c in visible],
        limit=4,
    )
    local_knowledge = memory_knowledge_context_for(
        citizen["id"],
        location_id=citizen["location_id"],
        limit=6,
    )
    maintenance_history = maintenance_context_for(
        citizen["id"],
        limit=4,
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

    nearby_exploration_memory = nearby_spatial_context_for(
        citizen["id"],
        x_m=citizen.get("position_x_m"),
        y_m=citizen.get("position_y_m"),
        radius_m=250.0,
        limit=4,
    )
    dialogue_text = "\n".join(
        f"- {d['summary']}"
        for d in dialogues
    ) or "- none"

    plan_context = plan_context_for_planner(
        citizen["id"],
        now=int(state["sim_minute"]),
    )
    causal_candidates = causal_candidates_for_new_plan(
        citizen["id"],
        now=int(state["sim_minute"]),
        limit=6,
    )
    causal_candidate_text = "\n".join(
        f"- Memory #{item['memory_event_id']} "
        f"({item['source_type']} #{item['source_id']}, {item['verification']}): "
        f"{item['summary']}"
        for item in causal_candidates
    ) or (
        "- no Memory Stage 1 causal candidates are available on this runtime; "
        "do not create a new persistent plan"
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
    ]
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
            for item in place.get("evidence", [])[-3:]
        )
        place_continuity_text = (
            f"- {place['location_id']}: {place['evidence_count']} retained source-backed "
            f"experience(s). Recent evidence: {recent_place_evidence}"
        )
    else:
        place_continuity_text = "- no qualifying personal place-continuity evidence here"

    custom_rows = custom_candidates_for(citizen["id"], limit=4)
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

MAINTENANCE ATTENTION RULES:
- This section is authoritative local physical state you can assess here; it is not a command, assigned role, or priority override.
- Procedure requirements describe known starter maintenance procedures. Local stock counts are only supplied while you are physically at the Seed Site landmark.
- If required stock is missing, the corresponding service action will not become legal until the named supplies actually exist in storage.
- Do not invent a source, conversion, fabrication recipe, or substitute for a missing named supply.
- A raw deposit is not automatically a source of Fasteners, Mechanical components, Battery cells, Lubricant, or any other finished part.
- You may choose an existing legal action because of a maintenance shortage only when your current knowledge and that legal action genuinely support the connection. Talking, inspecting, waiting, or pursuing a separately validated supply path are all allowed choices; none is mandatory.
- If service is already in progress, do not act as though a second simultaneous repair is needed.

CURRENT LOCALLY OBSERVABLE RESOURCE SUSTAINABILITY:
{resource_sustainability_text}

RESOURCE SUSTAINABILITY RULES:
- These finished starter supplies are finite physical stock, but finite does not mean urgent or scarce enough to override your own judgment.
- "No validated production process currently available to you" means only that you cannot presently make more through a known Simulation-supported process.
- "Validated replenishment process available" means a real evidence-backed process has been learned; it still requires its listed physical inputs, energy, and operational structure before the action becomes legal.
- Do not infer that a particular region, deposit, plant, stone, or raw material can replenish any finished part unless the relevant validated process explicitly names that input.
- Do not invent smelting, refining, machining, chemistry, recycling, substitution, or manufacturing steps that are not in your validated capability/knowledge context.
- Travel, surveying, inspection, conversation, and experiments may be reasonable ways to investigate unknowns only when they are already legal actions. None guarantees a useful result.
- A survey may reveal a real deposit or produce no new finding. Never state what you expect to find as fact.
- This is strategic context, not an assigned objective. You may choose unrelated legal work, maintenance, rest, social activity, or exploration.

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
- These are historical evidence trails, not personality traits, roles, preferences, commands, obligations, or physical bonuses.
- A current recurring pattern may be one reason among many to repeat a legal action, but it never outweighs energy, safety, maintenance, tools, materials, knowledge, or a deliberate new choice.
- Mixed or fading evidence means later history has weakened the old pattern; do not treat it as a standing preference.
- Place continuity means events here matter in your retained history. It does not mean this is your favorite place or that the place has an objective emotional property.
- A social pattern candidate is your source-backed perspective, not proof of a universal tradition or rule.
- You remain free to choose a different legal action. Trying something new does not violate continuity.

{plan_context}

BOUNDED SOURCE-BACKED MEMORIES ELIGIBLE TO JUSTIFY A NEW OR REVISED PLAN:
{causal_candidate_text}

PLAN CONTINUITY RULES:
- A persistent plan is your own intent continuity, not a command queue.
- Every physical step still has to be selected from LEGAL ACTIONS and validated by Simulation.
- You may continue, revise, pause, resume, abandon, complete, or create a plan only when source-backed history supports that choice.
- Creating a plan requires at least one Memory ID from the eligible list above.
- Energy, maintenance, unavailable material, new evidence, or reconsideration may interrupt a plan.
- Do not invent a role, class, specialization, or hidden priority to justify a plan.

DAILY RHYTHM:
- 06:00–20:00 is the normal active cycle.
- 20:00–22:00 is wind-down: prefer wrapping up, returning, unloading, maintenance, conversation, or recharging over starting major new work.
- 22:00–06:00 is the low-activity/recharge cycle. Active jobs may finish normally, but idle citizens should not treat the night as another full work shift.
- If Simulation offers only recharge or homeward actions because energy is low, survival/recharge takes priority over personality or productivity.
- A degraded battery is fully charged when current Energy reaches its usable battery-health capacity.

INFORMATION BOUNDARY:
- You know the other five citizens exist.
- You can directly observe citizens at your own location.
- You do NOT know the current location, activity, discoveries, research results, or condition of a citizen elsewhere unless that information reached you through a real mechanism.
- A speaker claim is something somebody said and remains unverified unless a separate physical observation, survey/measurement, or experiment verifies it.
- Conversation summaries are social continuity, not authoritative physical world state.
- Use provenance-backed records for last-known remote facts and state their source/uncertainty naturally.
- Retained local knowledge may include validated personal discoveries and clearly labeled unverified reports; do not promote an unverified report into physical truth.
- No radio, network, telepathy, shared status channel, or remote communication exists yet.
- Do not invent material microstructure/properties, market/economic value, terrain/site history, weather/environment effects, tools, or capabilities as reasons for acting.
- A plausible explanation is still a hypothesis unless a validated fact in your context supports it.
- Legal action availability means the action may be attempted; it does not prove the result in advance.
- If guided_practice appears as a legal action, that means a real physical guided-practice session may be attempted now. The session itself creates no learner practice/competence.
- Do not treat guided_practice legality as proof that the guide is an expert, mentor, trainer, specialist, leader, senior, or ranked.
- Ordinary talk/explanation is information transfer only and creates no competence.
- Do not use another citizen's hidden/global competence ledger as a reason for social recognition or help-seeking.
- Retained exploration memory is historical personal evidence, not proof that the terrain/material is unchanged right now.
- Coordinate precision in retained exploration memory is limited by the recorded observation radius; do not claim finer localization.

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

Do not create new physical actions. Do not infer hidden properties from the list of possible experiments. An experiment method being available does not imply it will reveal anything. Do not invent remote knowledge. Do not claim the action succeeded yet; the simulation decides reality. A plan does not make an illegal action legal.
""".strip()


async def choose_action(citizen: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    actions = autonomous_actions(citizen["id"])
    if not actions:
        return None

    payload = {
        "model": state["ollama_model"],
        "messages": [
            {
                "role": "system",
                "content": "Return only valid JSON. Respect information boundaries. You choose intent; the physical simulation decides reality.",
            },
            {"role": "user", "content": citizen_context(citizen, state, actions)},
        ],
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0.55,
            "num_ctx": 4096,
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
        return json.loads(raw)


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

        try:
            decision = await choose_action(citizen, state)
            if decision:
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
                ok, _ = start_action(
                    citizen["id"],
                    decision,
                    autonomous_choice=True,
                    autonomous_action_count=current_autonomous_action_count,
                )
                if ok and decision.get("action") == "talk":
                    with connect() as conn:
                        talker = conn.execute(
                            "SELECT active_job_id FROM citizens WHERE id = ?",
                            (citizen["id"],),
                        ).fetchone()
                        source_job_id = int(talker["active_job_id"]) if talker and talker["active_job_id"] else 0

                    if source_job_id <= 0:
                        raise RuntimeError("Talk started without a stable physical job id.")

                    await generate_dialogue(
                        citizen["id"],
                        str(decision.get("target") or ""),
                        str(decision.get("reason") or ""),
                        state["ollama_model"],
                        source_job_id,
                    )
                elif not ok:
                    with connect() as conn:
                        conn.execute(
                            "UPDATE citizens SET last_planned_minute = ? WHERE id = ?",
                            (now, citizen["id"]),
                        )
                        conn.commit()
        except Exception:
            # Ollama or a dialogue generation failure should never stop the city clock.
            with connect() as conn:
                conn.execute(
                    "UPDATE citizens SET last_planned_minute = ? WHERE id = ?",
                    (now, citizen["id"]),
                )
                conn.commit()
