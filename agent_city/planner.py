from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from .db import connect, get_meta, snapshot
from .simulation import possible_actions, start_action
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"


def citizen_context(citizen: dict[str, Any], state: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    other = "; ".join(
        f"{c['name']}: {c['current_activity']} at {c['location']}"
        for c in state["citizens"]
        if c["id"] != citizen["id"]
    )

    inventory = [
        r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0
    ]
    inv_text = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    discovered = [
        d for d in state["deposits"] if d["discovered"]
    ]
    deposit_text = ", ".join(
        f"{d['material']} at {next((l['name'] for l in state['locations'] if l['id'] == d['location_id']), d['location_id'])}"
        for d in discovered
    ) or "no confirmed deposits yet"

    action_text = "\n".join(
        f"{i}. {a['label']} | action={a['action']} target={a.get('target')} material={a.get('material')}"
        for i, a in enumerate(actions, start=1)
    )

    return f"""
You are {citizen['name']}, one of six equal mechanical citizens at the beginning of a new settlement.

Starting aptitude: {citizen['aptitude']}. This is only an aptitude, not a permanent job.
There is no leader and no assigned long-term objective.
You should choose what you believe is a reasonable next action from the legal actions provided.
You may be curious, cautious, practical, exploratory, or cooperative, but do not invent facts.

Current time: {format_sim_time(state['sim_minute'])}
Current location: {citizen['location']}
Energy: {citizen['energy']:.0f}%
Integrity: {citizen['integrity']:.0f}%
Carrying: {inv_text}
Confirmed deposits known to the settlement: {deposit_text}
Other citizens: {other}

LEGAL ACTIONS:
{action_text}

Choose exactly one legal action. Return JSON only with this shape:
{{
  "action": "one of the legal action names",
  "target": "the exact target from that legal action",
  "material": "exact material if the action is extract, otherwise null",
  "reason": "one concise sentence"
}}

Do not create new actions. Do not claim the action has succeeded yet. The simulation will decide what actually happens.
""".strip()


async def choose_action(citizen: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    actions = possible_actions(citizen["id"])
    if not actions:
        return None

    payload = {
        "model": state["ollama_model"],
        "messages": [
            {"role": "system", "content": "Return only valid JSON. You choose intent; the physical simulation decides reality."},
            {"role": "user", "content": citizen_context(citizen, state, actions)},
        ],
        "stream": False,
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
    # Stagger initial planning so six citizens do not hit the GPU at once.
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
                if not ok:
                    # Mark a short cooldown to avoid hammering the same invalid choice.
                    with connect() as conn:
                        conn.execute(
                            "UPDATE citizens SET last_planned_minute = ? WHERE id = ?",
                            (now, citizen["id"]),
                        )
                        conn.commit()
        except Exception:
            # If Ollama is unavailable or malformed, routine simulation keeps running.
            # The citizen simply remains idle until a future planning attempt.
            with connect() as conn:
                conn.execute(
                    "UPDATE citizens SET last_planned_minute = ? WHERE id = ?",
                    (now, citizen["id"]),
                )
                conn.commit()
