from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from .comms import generate_dialogue, known_deposits_for, recent_dialogues_for, visible_citizens
from .db import connect, get_meta, snapshot
from .memory import knowledge_context_for, social_context_for
from .simulation import possible_actions, start_action
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

    dialogues = recent_dialogues_for(citizen["id"], limit=5)
    social_history = social_context_for(
        citizen["id"],
        preferred_counterparties=[c["id"] for c in visible],
        limit=4,
    )
    local_knowledge = knowledge_context_for(
        citizen["id"],
        location_id=citizen["location_id"],
        limit=6,
    )
    dialogue_text = "\n".join(
        f"- {d['summary']}"
        for d in dialogues
    ) or "- none"

    action_text = "\n".join(
        f"{i}. {a['label']} | action={a['action']} target={a.get('target')} material={a.get('material')}"
        for i, a in enumerate(actions, start=1)
    )

    return f"""
You are {citizen['name']}, one of six equal mechanical citizens at the beginning of a new settlement.

Starting aptitude: {citizen['aptitude']}. This is only an aptitude, not a permanent job.
There is no leader and no assigned long-term objective.
Choose what you believe is a reasonable next action from the legal actions provided.

Current time: {format_sim_time(state['sim_minute'])}
Current location: {citizen['location']}
Energy: {citizen['energy']:.0f}%
Integrity: {citizen['integrity']:.0f}%
Carrying: {inv_text}

DIRECTLY OBSERVABLE CITIZENS AT YOUR LOCATION:
{visible_text}

DEPOSITS YOU PERSONALLY CONFIRMED:
{discovery_text}

THINGS YOU ACTUALLY HEARD OR SAID IN RECENT FACE-TO-FACE CITIZEN CONVERSATIONS:
{dialogue_text}

DURABLE SOCIAL HISTORY FROM YOUR OWN RECORDED ENCOUNTERS:
{social_history}

RETAINED KNOWLEDGE ABOUT YOUR CURRENT LOCATION:
{local_knowledge}

INFORMATION BOUNDARY:
- You know the other five citizens exist.
- You can directly observe citizens at your own location.
- You do NOT know the current location, activity, discoveries, or condition of a citizen elsewhere unless that information reached you through an actual recorded conversation.
- A conversation memory is something somebody said, not automatic proof that their claim was physically true.
- No radio, network, telepathy, shared status channel, or remote communication exists yet.

LEGAL ACTIONS:
{action_text}

Choose exactly one legal action. Return JSON only:
{{
  "action": "one of the legal action names",
  "target": "the exact target from that legal action",
  "material": "exact material if the action is extract, otherwise null",
  "reason": "one concise sentence explaining why you chose it"
}}

Do not create new actions. Do not invent remote knowledge. Do not claim the action succeeded yet; the simulation decides reality.
""".strip()


async def choose_action(citizen: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    actions = possible_actions(citizen["id"])
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
                ok, _ = start_action(citizen["id"], decision)
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
