from __future__ import annotations

import json
from typing import Any

import httpx

from .db import add_history, connect, get_meta
from .memory import record_conversation_memory, social_context_for
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"


def visible_citizens(citizen_id: str) -> list[dict[str, Any]]:
    """Citizens physically co-located with this citizen right now."""
    with connect() as conn:
        me = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not me:
            return []
        rows = conn.execute(
            """
            SELECT c.id, c.name, c.aptitude, c.current_activity,
                   c.energy, c.integrity, c.location, c.location_id
            FROM citizens c
            LEFT JOIN jobs j ON j.id = c.active_job_id
            WHERE c.location_id = ?
              AND c.id != ?
              AND COALESCE(j.action, '') != 'travel'
            ORDER BY c.rowid
            """,
            (me["location_id"], citizen_id),
        ).fetchall()
        return [dict(r) for r in rows]


def known_deposits_for(citizen_id: str) -> list[dict[str, Any]]:
    """Deposits this citizen personally confirmed through surveying."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.material, d.location_id, d.discovered_minute, l.name AS location_name
            FROM deposits d
            JOIN locations l ON l.id = d.location_id
            WHERE d.discovered = 1 AND d.discoverer_id = ?
            ORDER BY d.discovered_minute, d.id
            """,
            (citizen_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def recent_dialogues_for(citizen_id: str, limit: int = 6) -> list[dict[str, Any]]:
    """Actual face-to-face conversations this citizen participated in."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT cc.*,
                   'citizen_conversation' AS source_type,
                   cc.id AS source_id,
                   cc.id AS transfer_event_id,
                   li.name AS location_name,
                   ci.name AS initiator_name, ct.name AS target_name
            FROM citizen_conversations cc
            JOIN locations li ON li.id = cc.location_id
            JOIN citizens ci ON ci.id = cc.initiator_id
            JOIN citizens ct ON ct.id = cc.target_id
            WHERE cc.initiator_id = ? OR cc.target_id = ?
            ORDER BY cc.id DESC LIMIT ?
            """,
            (citizen_id, citizen_id, limit),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


def _citizen_private_context(citizen_id: str) -> str:
    with connect() as conn:
        c = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
        if not c:
            return "Citizen record unavailable."
        cargo = conn.execute(
            "SELECT material, amount FROM citizen_inventory WHERE citizen_id = ? AND amount > 0",
            (citizen_id,),
        ).fetchall()

    discoveries = known_deposits_for(citizen_id)
    dialogues = recent_dialogues_for(citizen_id, limit=4)
    social_history = social_context_for(citizen_id, limit=3)
    cargo_text = ", ".join(f"{r['amount']:g} {r['material']}" for r in cargo) or "nothing"
    discovery_text = "; ".join(
        f"{d['material']} at {d['location_name']}" for d in discoveries
    ) or "none personally confirmed"
    dialogue_text = "\n".join(
        f"- {d['summary']}" for d in dialogues
    ) or "- none"

    return f"""
Name: {c['name']}
Aptitude: {c['aptitude']}
Location: {c['location']}
Current activity: {c['current_activity']}
Energy: {c['energy']:.0f}%
Integrity: {c['integrity']:.0f}%
Carrying: {cargo_text}
Personally confirmed discoveries: {discovery_text}
Recent things actually heard or said in face-to-face citizen conversations:
{dialogue_text}
Durable relationship history derived from actual recorded encounters:
{social_history}
""".strip()


def record_dialogue(
    sim_minute: int,
    location_id: str,
    initiator_id: str,
    target_id: str,
    initiator_text: str,
    target_text: str,
    summary: str,
    source_job_id: int | None = None,
) -> int | None:
    """
    Persist one real face-to-face exchange.

    When source_job_id is supplied, the conversation is committed only while the
    matching physical talk job is still active and both participants are still
    bound to it at the same location. The source job is unique, making retries
    idempotent instead of duplicating a transfer record.
    """
    initiator_text = str(initiator_text or "").strip()
    target_text = str(target_text or "").strip()
    summary = str(summary or "").strip()
    if not initiator_text or not target_text or not summary:
        return None

    inserted = False
    with connect() as conn:
        if source_job_id is not None:
            existing = conn.execute(
                "SELECT id FROM citizen_conversations WHERE source_job_id = ?",
                (source_job_id,),
            ).fetchone()
            if existing:
                conversation_id = int(existing["id"])
            else:
                job = conn.execute(
                    "SELECT * FROM jobs WHERE id = ?",
                    (source_job_id,),
                ).fetchone()
                initiator = conn.execute(
                    "SELECT * FROM citizens WHERE id = ?",
                    (initiator_id,),
                ).fetchone()
                target = conn.execute(
                    "SELECT * FROM citizens WHERE id = ?",
                    (target_id,),
                ).fetchone()

                if (
                    not job
                    or job["action"] != "talk"
                    or job["status"] != "active"
                    or str(job["citizen_id"]) != initiator_id
                    or str(job["target"]) != target_id
                    or not initiator
                    or not target
                    or initiator["location_id"] != target["location_id"]
                    or int(initiator["active_job_id"] or 0) != source_job_id
                    or int(target["active_job_id"] or 0) != source_job_id
                ):
                    return None

                location_id = str(initiator["location_id"])
                sim_minute = int(job["start_minute"])

                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO citizen_conversations
                    (sim_minute, location_id, initiator_id, target_id,
                     initiator_text, target_text, summary, source_job_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sim_minute,
                        location_id,
                        initiator_id,
                        target_id,
                        initiator_text[:1400],
                        target_text[:1400],
                        summary[:1200],
                        source_job_id,
                    ),
                )
                if cur.rowcount:
                    conversation_id = int(cur.lastrowid)
                    inserted = True
                else:
                    existing = conn.execute(
                        "SELECT id FROM citizen_conversations WHERE source_job_id = ?",
                        (source_job_id,),
                    ).fetchone()
                    if not existing:
                        return None
                    conversation_id = int(existing["id"])
        else:
            cur = conn.execute(
                """
                INSERT INTO citizen_conversations
                (sim_minute, location_id, initiator_id, target_id,
                 initiator_text, target_text, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sim_minute,
                    location_id,
                    initiator_id,
                    target_id,
                    initiator_text[:1400],
                    target_text[:1400],
                    summary[:1200],
                ),
            )
            conversation_id = int(cur.lastrowid)
            inserted = True

        if inserted:
            initiator = conn.execute(
                "SELECT name FROM citizens WHERE id = ?",
                (initiator_id,),
            ).fetchone()
            target = conn.execute(
                "SELECT name FROM citizens WHERE id = ?",
                (target_id,),
            ).fetchone()
            loc = conn.execute(
                "SELECT name FROM locations WHERE id = ?",
                (location_id,),
            ).fetchone()
            if initiator and target and loc:
                add_history(
                    conn,
                    sim_minute,
                    "conversation",
                    f"{initiator['name']} and {target['name']} talked at {loc['name']}.",
                )
        conn.commit()

    # Memory is a derived projection of the durable conversation record. A
    # projection failure must never erase or invalidate the actual exchange.
    try:
        record_conversation_memory(conversation_id)
    except Exception:
        pass

    return conversation_id

async def generate_dialogue(
    initiator_id: str,
    target_id: str,
    reason: str | None,
    model: str,
    source_job_id: int,
) -> dict[str, str]:
    """Generate one short, grounded, face-to-face exchange and persist it."""
    with connect() as conn:
        initiator = conn.execute("SELECT * FROM citizens WHERE id = ?", (initiator_id,)).fetchone()
        target = conn.execute("SELECT * FROM citizens WHERE id = ?", (target_id,)).fetchone()
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (source_job_id,)).fetchone()

        if not initiator or not target:
            raise ValueError("Citizen record missing")
        if (
            not job
            or job["action"] != "talk"
            or job["status"] != "active"
            or str(job["citizen_id"]) != initiator_id
            or str(job["target"]) != target_id
        ):
            raise ValueError("Talk job is not active or no longer matches these participants")
        if (
            initiator["location_id"] != target["location_id"]
            or int(initiator["active_job_id"] or 0) != source_job_id
            or int(target["active_job_id"] or 0) != source_job_id
        ):
            raise ValueError("Citizens are no longer in the same active face-to-face talk")
        now = int(job["start_minute"])
        location_id = initiator["location_id"]
        location = conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()

    initiator_context = _citizen_private_context(initiator_id)
    target_context = _citizen_private_context(target_id)
    purpose = (reason or "The initiator wants to speak briefly.").strip()

    prompt = f"""
Create ONE short face-to-face conversation between two Agent City citizens who are physically together.

Time: {format_sim_time(now)}
Location: {location['name'] if location else location_id}

INITIATOR PRIVATE KNOWLEDGE:
{initiator_context}

TARGET PRIVATE KNOWLEDGE:
{target_context}

Why the initiator chose to speak:
{purpose}

INFORMATION RULES:
- A citizen may state their OWN current status, plans, personal discoveries, or things they actually heard in prior conversations.
- They may directly observe the other citizen because they are at the same location.
- They do NOT know the current status of citizens at other locations unless somebody previously told them.
- Do not invent completed work, discoveries, resources, remote events, or communication technology.
- Conversation can transfer information: after this exchange, both participants may remember what was said.
- Keep it natural and brief: one statement from the initiator and one response from the target.

Return JSON only:
{
  "initiator_text": "1-2 natural sentences",
  "target_text": "1-2 natural sentences",
  "summary": "one concise factual summary of what these two actually communicated"
}
""".strip()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return only valid JSON. Preserve local information boundaries; do not invent remote knowledge.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.6,
                        "num_ctx": 4096,
                        "num_predict": 260,
                    },
                },
            )
            response.raise_for_status()
            data = json.loads(response.json()["message"]["content"])
    except Exception as exc:
        raise RuntimeError("Citizen dialogue generation failed; no exchange was recorded.") from exc

    result = {
        "initiator_text": str(data.get("initiator_text") or "").strip(),
        "target_text": str(data.get("target_text") or "").strip(),
        "summary": str(data.get("summary") or "").strip(),
    }
    if not result["initiator_text"] or not result["target_text"] or not result["summary"]:
        raise RuntimeError("Citizen dialogue generation returned an incomplete exchange; nothing was recorded.")

    conversation_id = record_dialogue(
        now,
        location_id,
        initiator_id,
        target_id,
        result["initiator_text"],
        result["target_text"],
        result["summary"],
        source_job_id=source_job_id,
    )
    if conversation_id is None:
        raise RuntimeError("Talk was invalidated before the generated exchange could be committed.")

    result["conversation_id"] = str(conversation_id)
    result["source_job_id"] = str(source_job_id)
    return result
