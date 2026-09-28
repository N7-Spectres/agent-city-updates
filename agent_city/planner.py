from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from .db import connect, get_meta, snapshot
from .simulation import possible_actions, start_action
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"


def _citizen_location_id(citizen: dict[str, Any], state: dict[str, Any]) -> str | None:
    location_id = citizen.get("location_id")
    if location_id:
        return str(location_id)

    location_name = citizen.get("location")
    if not location_name:
        return None

    for location in state.get("locations", []):
        if location.get("name") == location_name:
            return str(location.get("id"))
    return None


def _is_traveling(citizen: dict[str, Any]) -> bool:
    if citizen.get("is_traveling") or citizen.get("traveling"):
        return True
    activity = str(citizen.get("current_activity") or "").strip().lower()
    return activity.startswith("travel") or activity.startswith("en route")


def citizen_context(citizen: dict[str, Any], state: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    citizen_location_id = _citizen_location_id(citizen, state)

    directly_observable = []
    for other_citizen in state.get("citizens", []):
        if other_citizen.get("id") == citizen.get("id") or _is_traveling(other_citizen):
            continue
        other_location_id = _citizen_location_id(other_citizen, state)
        if citizen_location_id and other_location_id == citizen_location_id:
            directly_observable.append(str(other_citizen.get("name") or other_citizen.get("id")))

    local_people_text = ", ".join(directly_observable) or "no other citizens directly observable here"

    inventory = [
        r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0
    ]
    inv_text = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    local_deposits = [
        d
        for d in state.get("deposits", [])
        if d.get("discovered") and citizen_location_id and str(d.get("location_id")) == citizen_location_id
    ]
    deposit_text = ", ".join(str(d["material"]) for d in local_deposits) or "none directly observable here"

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

Information rule: you only know information that could physically have reached you.
Remote citizens' current location, activity, plans, condition, and discoveries are unknown unless a real communication or observation record is provided.
A communicated claim is something another citizen said; it is not automatically verified physical truth.

Current time: {format_sim_time(state['sim_minute'])}
Current location: {citizen['location']}
Energy: {citizen['energy']:.0f}%
Integrity: {citizen['integrity']:.0f}%
Carrying: {inv_text}
Locally confirmed deposits directly observable now: {deposit_text}
Citizens directly observable at this location: {local_people_text}

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
