from __future__ import annotations

import json
import sqlite3
from typing import Any

import httpx

from .db import add_history, connect, get_meta
from .provenance import knowledge_context_for, record_face_to_face_claims
from .memory import record_conversation_memory, social_context_for
from .talk_diagnostics import record_talk_diagnostic
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"


def _diag(source_job_id: int, **kwargs: Any) -> None:
    """Diagnostics must never become a new reason for a valid talk to fail."""
    try:
        record_talk_diagnostic(source_job_id, **kwargs)
    except Exception:
        pass


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
    provenance_knowledge = knowledge_context_for(citizen_id, limit=8)
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
Provenance-backed facts and claims that actually reached you:
{provenance_knowledge}
Recent face-to-face conversation summaries for social continuity only (not physical proof):
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
    claims: list[dict[str, Any]] | None = None,
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

    try:
        record_face_to_face_claims(conversation_id, claims)
    except Exception:
        # The durable raw exchange remains authoritative for what was said.
        # Claim projection can be safely retried/backfilled later.
        pass

    return conversation_id

def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = str(raw or "").strip()
    if not text:
        return None

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    first = text.find("{")
    last = text.rfind("}")
    if first < 0 or last <= first:
        return None
    try:
        parsed = json.loads(text[first:last + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _dialogue_payload(data: dict[str, Any] | None) -> dict[str, str] | None:
    if not data:
        return None
    initiator_text = str(data.get("initiator_text") or "").strip()
    target_text = str(data.get("target_text") or "").strip()
    summary = str(data.get("summary") or "").strip()
    if not initiator_text or not target_text or not summary:
        return None
    return {
        "initiator_text": initiator_text,
        "target_text": target_text,
        "summary": summary,
    }


async def _generate_raw_exchange(
    *,
    model: str,
    prompt: str,
    source_job_id: int,
) -> dict[str, str]:
    """
    Generate only the physical conversation payload.

    Provenance enrichment is intentionally not part of this schema. A malformed
    claim list must never erase an otherwise valid exchange.
    """
    last_code = "dialogue_generation_failed"
    last_detail = ""

    async with httpx.AsyncClient(timeout=90.0) as client:
        for attempt in range(2):
            final_attempt = attempt == 1
            try:
                response = await client.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Return only one valid JSON object with exactly "
                                    "initiator_text, target_text, and summary. "
                                    "Preserve local information boundaries."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                        "think": False,
                        "format": "json",
                        "options": {
                            "temperature": 0.55 if attempt == 0 else 0.35,
                            "num_ctx": 4096,
                            "num_predict": 260 if attempt == 0 else 340,
                        },
                    },
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                last_code = "ollama_http_failure"
                last_detail = f"HTTP {exc.response.status_code}"
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Citizen dialogue request failed.") from exc
                continue
            except httpx.RequestError as exc:
                last_code = "ollama_network_failure"
                last_detail = type(exc).__name__
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Citizen dialogue request could not reach Ollama.") from exc
                continue

            try:
                envelope = response.json()
            except (ValueError, TypeError):
                envelope = None
            if not isinstance(envelope, dict):
                last_code = "ollama_response_malformed"
                last_detail = "Ollama HTTP response was not a JSON object."
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Ollama returned a malformed response envelope.")
                continue

            message = envelope.get("message") or {}
            raw = str(message.get("content") or "").strip()
            if not raw:
                last_code = "ollama_empty_response"
                last_detail = "Ollama returned no dialogue content."
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Citizen dialogue generation returned empty content.")
                continue

            data = _parse_json_object(raw)
            if data is None:
                last_code = "dialogue_malformed_json"
                last_detail = "Response was not a parseable JSON object."
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Citizen dialogue generation returned malformed JSON.")
                continue

            dialogue = _dialogue_payload(data)
            if dialogue is None:
                last_code = "dialogue_schema_incomplete"
                last_detail = "Required dialogue fields were blank or missing."
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="failure" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    raise RuntimeError("Citizen dialogue generation returned an incomplete exchange.")
                continue

            _diag(
                source_job_id,
                stage="dialogue_generation",
                outcome="success",
                code="dialogue_generated",
                detail=f"Valid raw exchange on attempt {attempt + 1}.",
            )
            return dialogue

    raise RuntimeError(f"Citizen dialogue generation failed: {last_code} {last_detail}".strip())


async def _extract_claims_best_effort(
    *,
    model: str,
    source_job_id: int,
    conversation_id: int,
    initiator_text: str,
    target_text: str,
) -> None:
    """
    Enrich a durable exchange with claim provenance.

    This phase is intentionally non-fatal. The raw stored conversation is the
    information-transfer event even when claim classification is unavailable.
    """
    prompt = f"""
Extract concrete factual assertions from this ALREADY STORED face-to-face exchange.

INITIATOR:
{initiator_text}

TARGET:
{target_text}

Return JSON only:
{{
  "claims": [
    {{
      "speaker": "initiator or target",
      "subject_type": "location, material, citizen, project, or other",
      "subject_id": "known stable id if clearly present, otherwise null",
      "topic": "short factual topic key",
      "value": "an exact sentence or clause copied verbatim from that speaker's text"
    }}
  ]
}}

Rules:
- Do not invent or paraphrase the claim value.
- Include only factual assertions literally present in the stored text.
- Questions, greetings, suggestions, guesses, and implications are not claims.
- An empty claims array is valid.
""".strip()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return only valid JSON claim metadata for the supplied stored transcript.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "think": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.15,
                        "num_ctx": 2048,
                        "num_predict": 300,
                    },
                },
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _diag(
            source_job_id,
            stage="claim_extraction",
            outcome="degraded",
            code="claim_ollama_http_failure",
            detail=f"HTTP {exc.response.status_code}; raw exchange remains stored.",
        )
        return
    except httpx.RequestError as exc:
        _diag(
            source_job_id,
            stage="claim_extraction",
            outcome="degraded",
            code="claim_ollama_network_failure",
            detail=f"{type(exc).__name__}; raw exchange remains stored.",
        )
        return

    try:
        envelope = response.json()
    except (ValueError, TypeError):
        envelope = None
    if not isinstance(envelope, dict):
        _diag(
            source_job_id,
            stage="claim_extraction",
            outcome="degraded",
            code="claim_response_malformed",
            detail="Claim response envelope was malformed; raw exchange remains stored.",
        )
        return

    raw = str((envelope.get("message") or {}).get("content") or "").strip()
    data = _parse_json_object(raw)
    if data is None:
        _diag(
            source_job_id,
            stage="claim_extraction",
            outcome="degraded",
            code="claim_malformed_json",
            detail="Claim metadata was not parseable; raw exchange remains stored.",
        )
        return

    claims = data.get("claims")
    if not isinstance(claims, list):
        _diag(
            source_job_id,
            stage="claim_extraction",
            outcome="degraded",
            code="claim_schema_incomplete",
            detail="Claims field was missing/not a list; raw exchange remains stored.",
        )
        return

    try:
        receipt_ids = record_face_to_face_claims(conversation_id, claims)
    except sqlite3.DatabaseError as exc:
        _diag(
            source_job_id,
            stage="claim_persistence",
            outcome="degraded",
            code="claim_persistence_failure",
            detail=f"{type(exc).__name__}; raw exchange remains stored.",
        )
        return
    except Exception as exc:
        _diag(
            source_job_id,
            stage="claim_persistence",
            outcome="degraded",
            code="claim_projection_failure",
            detail=f"{type(exc).__name__}; raw exchange remains stored.",
        )
        return

    _diag(
        source_job_id,
        stage="claim_extraction",
        outcome="success",
        code="claims_projected" if receipt_ids else "claims_empty",
        detail=f"{len(receipt_ids)} provenance receipt(s) created.",
    )


async def generate_dialogue(
    initiator_id: str,
    target_id: str,
    reason: str | None,
    model: str,
    source_job_id: int,
) -> dict[str, Any]:
    """Generate, persist, and then best-effort enrich one face-to-face exchange."""
    with connect() as conn:
        initiator = conn.execute("SELECT * FROM citizens WHERE id = ?", (initiator_id,)).fetchone()
        target = conn.execute("SELECT * FROM citizens WHERE id = ?", (target_id,)).fetchone()
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (source_job_id,)).fetchone()

        if not initiator or not target:
            _diag(
                source_job_id,
                stage="physical_validation",
                outcome="failure",
                code="citizen_record_missing",
            )
            raise ValueError("Citizen record missing")
        if (
            not job
            or job["action"] != "talk"
            or job["status"] != "active"
            or str(job["citizen_id"]) != initiator_id
            or str(job["target"]) != target_id
        ):
            _diag(
                source_job_id,
                stage="physical_validation",
                outcome="failure",
                code="physical_talk_invalid_before_generation",
            )
            raise ValueError("Talk job is not active or no longer matches these participants")
        if (
            initiator["location_id"] != target["location_id"]
            or int(initiator["active_job_id"] or 0) != source_job_id
            or int(target["active_job_id"] or 0) != source_job_id
        ):
            _diag(
                source_job_id,
                stage="physical_validation",
                outcome="failure",
                code="physical_talk_invalid_before_generation",
            )
            raise ValueError("Citizens are no longer in the same active face-to-face talk")

        now = int(job["start_minute"])
        location_id = str(initiator["location_id"])
        location = conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()

    _diag(
        source_job_id,
        stage="physical_validation",
        outcome="success",
        code="physical_talk_valid",
    )

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
- They do NOT know current remote status unless that information actually reached them.
- Do not invent completed work, discoveries, resources, remote events, or communication technology.
- Keep it natural and brief: one statement from the initiator and one response from the target.

Return JSON only:
{{
  "initiator_text": "1-2 natural sentences",
  "target_text": "1-2 natural sentences",
  "summary": "one concise factual summary of what these two actually communicated"
}}
""".strip()

    dialogue = await _generate_raw_exchange(
        model=model,
        prompt=prompt,
        source_job_id=source_job_id,
    )

    try:
        conversation_id = record_dialogue(
            now,
            location_id,
            initiator_id,
            target_id,
            dialogue["initiator_text"],
            dialogue["target_text"],
            dialogue["summary"],
            source_job_id=source_job_id,
            claims=None,
        )
    except sqlite3.DatabaseError as exc:
        _diag(
            source_job_id,
            stage="raw_persistence",
            outcome="failure",
            code="persistence_database_failure",
            detail=type(exc).__name__,
        )
        raise RuntimeError("Citizen dialogue could not be persisted.") from exc

    if conversation_id is None:
        _diag(
            source_job_id,
            stage="raw_persistence",
            outcome="failure",
            code="physical_talk_invalid_before_persistence",
        )
        raise RuntimeError("Talk was invalidated before the generated exchange could be committed.")

    _diag(
        source_job_id,
        stage="raw_persistence",
        outcome="success",
        code="exchange_persisted",
        detail=f"conversation #{conversation_id}",
    )

    await _extract_claims_best_effort(
        model=model,
        source_job_id=source_job_id,
        conversation_id=conversation_id,
        initiator_text=dialogue["initiator_text"],
        target_text=dialogue["target_text"],
    )

    result: dict[str, Any] = dict(dialogue)
    result["conversation_id"] = str(conversation_id)
    result["source_job_id"] = str(source_job_id)
    return result

