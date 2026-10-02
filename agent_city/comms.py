from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

import httpx

from .db import add_history, connect, get_meta
from .continuity_language import (
    guided_practice_context,
    help_question_context,
    measured_competence_context,
    pattern_continuity_context,
    plan_discussion_context,
    recognition_context,
    self_assessment_context,
    teaching_boundary_context,
    transmittable_pattern_catalog,
)
from .grounding import (
    citizen_capability_context,
    grounding_policy_text,
    spatial_grounding_context,
)
from .provenance import knowledge_context_for, record_face_to_face_claims
from .memory import record_conversation_memory, record_knowledge_event, social_context_for
from .pattern_memory import record_social_pattern_evidence
from .personality import personality_context, dialogue_style_rules
from .talk_diagnostics import record_talk_diagnostic
from .world import format_sim_time

OLLAMA_URL = "http://127.0.0.1:11434"

# Citizen-conversation summaries are social records, not physical evidence.
# These verbs are too strong unless a separate Simulation source proves them,
# so raw talk summaries must never upgrade claims into verification.
UNSAFE_SUMMARY_TERMS = (
    "validated",
    "confirmed",
    "verified",
    "proved",
    "proven",
    "demonstrated",
    "established",
)


def _summary_is_claim_safe(summary: str) -> bool:
    text = str(summary or "").lower()
    return not any(re.search(rf"\b{re.escape(term)}\b", text) for term in UNSAFE_SUMMARY_TERMS)


def _safe_summary_fallback() -> str:
    return (
        "The citizens exchanged reports and discussed possible next steps; "
        "the conversation itself does not verify any physical claim."
    )


def _naturalize_conversation_summary(
    summary: str,
    initiator_name: str,
    target_name: str,
) -> str:
    """
    Keep stored social summaries readable for people.

    The dialogue generator uses structured participant roles internally, but
    those schema labels must not leak into the citizen-facing History UI.
    """
    text = " ".join(str(summary or "").split()).strip()
    if not text:
        return text

    # Strip role+name appositives before generic role replacement, e.g.
    # "The initiator, Cato, brought up..." -> "Cato brought up...".
    text = re.sub(
        rf"\bthe initiator\s*,\s*{re.escape(initiator_name)}\s*,\s*",
        f"{initiator_name} ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        rf"\bthe target(?: citizen)?\s*,\s*{re.escape(target_name)}\s*,\s*",
        f"{target_name} ",
        text,
        flags=re.IGNORECASE,
    )

    replacements = (
        (r"\bthe initiator\b", initiator_name),
        (r"\binitiator\b", initiator_name),
        (r"\bthe target citizen\b", target_name),
        (r"\btarget citizen\b", target_name),
        (r"\bthe conversation target\b", target_name),
        (r"\bconversation target\b", target_name),
        (r"\bthe target\b", target_name),
        (r"\baction target\b", target_name),
        (r"\bsource job(?:\s*#\d+)?\b", "the conversation"),
        (r"\bproposal state\b", "discussion"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Clean up the most common artifact if the model wrote both a role and name,
    # e.g. "The initiator, Cato,..." before role substitution.
    for name in (initiator_name, target_name):
        escaped = re.escape(name)
        text = re.sub(
            rf"\b{escaped}\s*,\s*{escaped}\b",
            name,
            text,
            flags=re.IGNORECASE,
        )

    return " ".join(text.split()).strip()


def _diag(source_job_id: int, **kwargs: Any) -> None:
    """Diagnostics must never become a new reason for a valid talk to fail."""
    try:
        record_talk_diagnostic(source_job_id, **kwargs)
    except Exception:
        pass


def _pattern_catalog_text(citizen_id: str) -> str:
    rows = transmittable_pattern_catalog(citizen_id)
    if not rows:
        return "- none"
    return "\n".join(
        f"- {row['pattern_key']}: {row['description']}"
        for row in rows
    )


def _existing_pattern_memory_id(owner_id: str, receipt_id: int) -> int | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM memory_events
            WHERE owner_id = ?
              AND source_type = 'information_receipt'
              AND source_id = ?
              AND event_kind = 'reported_social_pattern'
              AND source_role = 'recipient'
            LIMIT 1
            """,
            (owner_id, int(receipt_id)),
        ).fetchone()
    return int(row["id"]) if row else None


def _project_social_pattern_claims(
    conversation_id: int,
    claims: list[dict[str, Any]] | None,
    receipt_ids: list[int] | None,
) -> list[int]:
    """
    Best-effort Stage 3 social-pattern projection.

    A transcript-grounded claim can become social-pattern evidence only when:
    - provenance already created a real face-to-face receipt,
    - the claim value is the actual stored speaker text,
    - the extractor chose an exact pattern key from that speaker's source-backed
      transmittable catalog.

    This cannot create the speaker's pattern, make the claim verified, or create
    a custom by itself.
    """
    if not claims or not receipt_ids:
        return []

    with connect() as conn:
        conversation = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id,
                   initiator_text, target_text
            FROM citizen_conversations
            WHERE id = ?
            """,
            (int(conversation_id),),
        ).fetchone()
        if not conversation:
            return []
        placeholders = ",".join("?" for _ in receipt_ids)
        receipts = conn.execute(
            f"""
            SELECT *
            FROM information_receipts
            WHERE id IN ({placeholders})
              AND source_conversation_id = ?
              AND channel = 'face_to_face_claim'
              AND assertion_kind = 'speaker_claim'
            """,
            (*[int(v) for v in receipt_ids], int(conversation_id)),
        ).fetchall()

    role_to_speaker = {
        "initiator": str(conversation["initiator_id"]),
        "target": str(conversation["target_id"]),
    }
    role_to_text = {
        "initiator": " ".join(str(conversation["initiator_text"] or "").split()),
        "target": " ".join(str(conversation["target_text"] or "").split()),
    }
    catalogs = {
        speaker_id: {
            str(row["pattern_key"]): row
            for row in transmittable_pattern_catalog(speaker_id)
        }
        for speaker_id in role_to_speaker.values()
    }

    receipt_lookup: dict[tuple[str, str], list[Any]] = {}
    for row in receipts:
        key = (
            str(row["source_actor_id"] or ""),
            " ".join(str(row["value_text"] or "").split()).casefold(),
        )
        receipt_lookup.setdefault(key, []).append(row)

    evidence_ids: list[int] = []
    for raw in claims[:12]:
        if not isinstance(raw, dict):
            continue
        role = str(raw.get("speaker") or "").strip().lower()
        if role not in role_to_speaker:
            continue
        if str(raw.get("subject_type") or "").strip().lower() != "social_pattern":
            continue

        pattern_key = str(raw.get("pattern_key") or "").strip()
        value_text = " ".join(str(raw.get("value") or "").split()).strip()
        if not pattern_key or not value_text:
            continue
        if value_text.casefold() not in role_to_text[role].casefold():
            continue

        speaker_id = role_to_speaker[role]
        catalog_row = catalogs.get(speaker_id, {}).get(pattern_key)
        if not catalog_row:
            continue

        matches = receipt_lookup.get((speaker_id, value_text.casefold()), [])
        if not matches:
            continue
        receipt = matches[0]
        recipient_id = str(receipt["recipient_id"])

        metadata = {
            "verification": str(receipt["verification"] or "unverified"),
            "channel": "face_to_face_claim",
            "source_actor_id": speaker_id,
            "source_conversation_id": int(conversation_id),
            "information_receipt_id": int(receipt["id"]),
            "pattern_key": pattern_key,
            "pattern_kind": str(catalog_row.get("kind") or "social_pattern"),
            "context_key": str(catalog_row.get("context_key") or ""),
        }
        memory_id = record_knowledge_event(
            recipient_id,
            sim_minute=int(receipt["received_at_sim_minute"]),
            event_kind="reported_social_pattern",
            source_type="information_receipt",
            source_id=int(receipt["id"]),
            source_role="recipient",
            summary=value_text,
            metadata=metadata,
            status="remembered",
            importance=0.52,
        )
        if memory_id is None:
            memory_id = _existing_pattern_memory_id(recipient_id, int(receipt["id"]))
        if memory_id is None:
            continue

        evidence_id = record_social_pattern_evidence(
            memory_id,
            pattern_key=pattern_key,
            actor_id=speaker_id,
            transmission_mode="heard",
            context_key=str(catalog_row.get("context_key") or ""),
        )
        if evidence_id is not None:
            evidence_ids.append(int(evidence_id))

    return evidence_ids


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


def _citizen_private_context(citizen_id: str, counterpart_id: str | None = None) -> str:
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
    pattern_history = pattern_continuity_context(
        citizen_id,
        location_id=str(c["location_id"]),
    )
    capability_context = citizen_capability_context(citizen_id)
    spatial_context = spatial_grounding_context(citizen_id)
    self_context = self_assessment_context(citizen_id)
    plan_context = plan_discussion_context(citizen_id)
    teaching_context = teaching_boundary_context(citizen_id)
    measured_context = measured_competence_context(citizen_id)
    guidance_context = guided_practice_context(
        citizen_id,
        counterpart_id=counterpart_id,
        include_current_options=True,
    )
    help_context = help_question_context(citizen_id, counterpart_id)
    recognition = (
        recognition_context(citizen_id, counterpart_id)
        if counterpart_id
        else "PERSPECTIVE-SAFE RECOGNITION:\n- no counterpart selected"
    )
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
Personality and voice:
{personality_context(dict(c))}
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

{pattern_history}

{capability_context}

{spatial_context}

{self_context}

{plan_context}

{recognition}

{teaching_context}

{measured_context}

{guidance_context}

{help_context}
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
        receipt_ids = record_face_to_face_claims(conversation_id, claims)
        _project_social_pattern_claims(conversation_id, claims, receipt_ids)
    except Exception:
        # The durable raw exchange remains authoritative for what was said.
        # Claim/pattern projection can be safely retried/backfilled later.
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
                                    "Preserve local information boundaries. "
                                    "The summary is a social record of what was said, not physical evidence. "
                                    "Write summary prose for a human reader and never expose participant-role or "
                                    "backend schema terms such as initiator, target citizen, source job, action target, "
                                    "or proposal state. Never upgrade reports or agreements into validated, confirmed, "
                                    "verified, proved, demonstrated, or established physical facts."
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
            if dialogue is not None and not _summary_is_claim_safe(dialogue["summary"]):
                last_code = "summary_claim_upgrade"
                last_detail = "Dialogue summary used verification language unsupported by a conversation source."
                _diag(
                    source_job_id,
                    stage="dialogue_generation",
                    outcome="degraded" if final_attempt else "retry",
                    code=last_code,
                    detail=last_detail,
                )
                if final_attempt:
                    dialogue["summary"] = _safe_summary_fallback()
                else:
                    continue

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
    with connect() as conn:
        conversation = conn.execute(
            """
            SELECT initiator_id, target_id
            FROM citizen_conversations
            WHERE id = ?
            """,
            (int(conversation_id),),
        ).fetchone()

    initiator_patterns = (
        _pattern_catalog_text(str(conversation["initiator_id"]))
        if conversation else "- none"
    )
    target_patterns = (
        _pattern_catalog_text(str(conversation["target_id"]))
        if conversation else "- none"
    )

    prompt = f"""
Extract concrete factual assertions from this ALREADY STORED face-to-face exchange.

ALLOWED SOURCE-BACKED SOCIAL PATTERN KEYS FOR THE INITIATOR:
{initiator_patterns}

ALLOWED SOURCE-BACKED SOCIAL PATTERN KEYS FOR THE TARGET:
{target_patterns}

INITIATOR:
{initiator_text}

TARGET:
{target_text}

Return JSON only:
{{
  "claims": [
    {{
      "speaker": "initiator or target",
      "subject_type": "location, material, citizen, project, social_pattern, or other",
      "subject_id": "known stable id if clearly present, otherwise null",
      "topic": "short factual topic key",
      "value": "an exact sentence or clause copied verbatim from that speaker's text",
      "pattern_key": "exact allowed source-backed pattern key above, but ONLY for a literal recurring/social pattern claim; otherwise null"
    }}
  ]
}}

Rules:
- Do not invent or paraphrase the claim value.
- Include only factual assertions literally present in the stored text.
- Questions, greetings, suggestions, guesses, and implications are not claims.
- Use subject_type "social_pattern" and pattern_key only when the speaker literally states a recurring/social pattern that matches one of THAT SPEAKER'S allowed keys above.
- Never invent, paraphrase, normalize, or transfer a pattern key between speakers.
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

    try:
        pattern_evidence_ids = _project_social_pattern_claims(
            conversation_id,
            claims,
            receipt_ids,
        )
    except Exception as exc:
        pattern_evidence_ids = []
        _diag(
            source_job_id,
            stage="pattern_projection",
            outcome="degraded",
            code="pattern_projection_failure",
            detail=f"{type(exc).__name__}; raw exchange and claim receipts remain stored.",
        )

    _diag(
        source_job_id,
        stage="claim_extraction",
        outcome="success",
        code="claims_projected" if receipt_ids else "claims_empty",
        detail=(
            f"{len(receipt_ids)} provenance receipt(s) created; "
            f"{len(pattern_evidence_ids)} source-backed pattern transmission(s) retained."
        ),
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

    initiator_name = str(initiator["name"])
    target_name = str(target["name"])
    initiator_context = _citizen_private_context(initiator_id, target_id)
    target_context = _citizen_private_context(target_id, initiator_id)
    purpose = (reason or f"{initiator_name} wants to speak briefly.").strip()

    prompt = f"""
Create ONE short face-to-face conversation between two Agent City citizens who are physically together.

Time: {format_sim_time(now)}
Location: {location['name'] if location else location_id}

{initiator_name.upper()} PRIVATE KNOWLEDGE:
{initiator_context}

{target_name.upper()} PRIVATE KNOWLEDGE:
{target_context}

Why {initiator_name} chose to speak:
{purpose}

{grounding_policy_text(visitor_facing=False)}

{dialogue_style_rules()}

INFORMATION RULES:
- A citizen may state their OWN current status, plans, personal discoveries, or things they actually heard in prior conversations.
- They may directly observe the other citizen because they are at the same location.
- They do NOT know current remote status unless that information actually reached them.
- Do not invent completed work, discoveries, resources, remote events, or communication technology.
- Keep it natural and brief: one statement from {initiator_name} and one response from {target_name}.
- Let each citizen sound recognizably different. Do not flatten both voices into the same operational-assistant tone.
- Personality may influence preference and wording, but never creates authority, rank, command rights, or extra knowledge.
- An invented explanation, material property, terrain detail, weather effect, economic value, tool, or capability is not allowed just because it would make the conversation more colorful.
- Do not invent official-sounding names for procedures, protocols, inspections, repair methods, tools, or equipment. If an exact name is absent from authoritative capability/knowledge and source-backed recall, use generic proposal language instead.
- If an older remembered/report summary contains an unsupported named procedure, preserve it only as something previously discussed/reported; do not upgrade it into an established method or capability.
- Repeated personal practice may support phrases like "I've done this several times" only when the citizen's own physical practice evidence supports it.
- Self-assessment such as "I think I'm getting better" remains interpretation, not objective capability truth.
- Recognition of the other citizen is perspective-based. Do not assign expert, master, leader, trainer, mentor, specialist, rank, or reputation as authoritative identity.
- Do not compare another citizen's experience to your own unless information that legitimately reached the speaker supports that comparison.
- Explaining or teaching through conversation does not create practice, competence, or skill for the listener.
- Discussing a persistent plan does not create, revise, pause, resume, abandon, supersede, or complete the canonical plan.
- A measured practice-derived task-time effect is an objective physical effect for the speaker only. It is not a title, rank, proficiency level, or social reputation.
- Never expose another citizen's hidden/global competence snapshot as recognition evidence.
- A real guided-practice session is a physical Simulation event. Ordinary explanation is not guided practice and grants zero competence.
- A completed guided-practice session still creates no learner practice by itself; only the learner's later real matching task creates new practice evidence.
- Teacher and learner describe one event, not permanent mentor/trainer/expert identities.
- Recurring personal behavior may be described only from the source-backed recurring-history packet. "Current", "mixed", and "fading" describe evidence state, not a personality trait or preference.
- Place continuity is personal remembered history, not an objective "favorite place", home, safe place, or sacred place label.
- Social pattern candidates are perspective-specific evidence. Do not automatically call them customs, traditions, rules, rituals, or something everyone does.
- Talking about a recurring/social pattern may transmit a claim to the listener, but speech cannot create the underlying repeated behavior or make the claim verified.

SUMMARY TRUTH RULES:
- The summary describes communication, not physical verification.
- Write the summary for a human reader using {initiator_name} and {target_name} by name.
- Never refer to either citizen as "the initiator", "initiator", "the target", "target citizen", or "conversation target".
- Never expose backend terms such as "source job", "action target", "proposal state", or other schema/process labels in the summary.
- Prefer ordinary verbs such as "said", "reported", "discussed", "brought up", "compared", "planned", or "agreed".
- Do not use "validated", "confirmed", "verified", "proved", "proven", "demonstrated", or "established" for a physical claim in a conversation summary.
- An agreement to inspect, travel, recharge, build, or test remains an intention until Simulation records the physical action/outcome.
- A citizen reporting their own inventory/status may be summarized as a report; the listener hearing it does not independently verify it.

Return JSON only:
{{
  "initiator_text": "1-2 natural sentences",
  "target_text": "1-2 natural sentences",
  "summary": "one concise claim-safe summary of what these two communicated"
}}
""".strip()

    dialogue = await _generate_raw_exchange(
        model=model,
        prompt=prompt,
        source_job_id=source_job_id,
    )
    dialogue["summary"] = _naturalize_conversation_summary(
        dialogue["summary"],
        initiator_name,
        target_name,
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

