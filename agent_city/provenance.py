from __future__ import annotations

from typing import Any

from .db import connect, get_meta
from .world import format_sim_time

VALID_CHANNELS = {
    "direct_observation",
    "survey_measurement",
    "experiment_result",
    "personal_experience",
    "face_to_face_claim",
}
VALID_ASSERTION_KINDS = {"validated_observation", "speaker_claim"}
VALID_VERIFICATION = {"unverified", "verified", "contradicted"}


def ensure_information_schema() -> None:
    """
    Create Communication-owned information receipts.

    A receipt means information physically reached one citizen through a specific
    mechanism. It is not a global encyclopedia and it does not replace Memory.
    """
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS information_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id TEXT NOT NULL,
                subject_type TEXT NOT NULL,
                subject_id TEXT,
                topic TEXT NOT NULL,
                value_text TEXT NOT NULL,
                channel TEXT NOT NULL,
                source_actor_id TEXT,
                origin_event_type TEXT,
                origin_event_id INTEGER,
                transfer_event_type TEXT,
                transfer_event_id INTEGER,
                source_conversation_id INTEGER,
                observed_at_sim_minute INTEGER,
                received_at_sim_minute INTEGER NOT NULL,
                assertion_kind TEXT NOT NULL,
                verification TEXT NOT NULL,
                source_key TEXT NOT NULL UNIQUE
            );

            CREATE INDEX IF NOT EXISTS idx_information_receipts_recipient_time
            ON information_receipts(recipient_id, received_at_sim_minute DESC, id DESC);

            CREATE INDEX IF NOT EXISTS idx_information_receipts_subject
            ON information_receipts(recipient_id, subject_type, subject_id, topic, received_at_sim_minute DESC);
            """
        )

        _backfill_validated_v05_knowledge(conn)
        _sync_v06_simulation_knowledge(conn)
        conn.commit()


def _insert_receipt(
    conn,
    *,
    recipient_id: str,
    subject_type: str,
    subject_id: str | None,
    topic: str,
    value_text: str,
    channel: str,
    source_actor_id: str | None,
    origin_event_type: str | None,
    origin_event_id: int | None,
    transfer_event_type: str | None,
    transfer_event_id: int | None,
    source_conversation_id: int | None,
    observed_at_sim_minute: int | None,
    received_at_sim_minute: int,
    assertion_kind: str,
    verification: str,
    source_key: str,
) -> int | None:
    recipient_id = str(recipient_id or "").strip()
    subject_type = str(subject_type or "").strip()
    subject_id = str(subject_id).strip() if subject_id is not None else None
    topic = str(topic or "").strip()
    value_text = " ".join(str(value_text or "").split())[:1200]
    source_actor_id = str(source_actor_id).strip() if source_actor_id else None
    source_key = str(source_key or "").strip()[:500]

    if (
        not recipient_id
        or not subject_type
        or not topic
        or not value_text
        or not source_key
        or channel not in VALID_CHANNELS
        or assertion_kind not in VALID_ASSERTION_KINDS
        or verification not in VALID_VERIFICATION
    ):
        return None

    cur = conn.execute(
        """
        INSERT OR IGNORE INTO information_receipts(
            recipient_id, subject_type, subject_id, topic, value_text,
            channel, source_actor_id,
            origin_event_type, origin_event_id,
            transfer_event_type, transfer_event_id,
            source_conversation_id,
            observed_at_sim_minute, received_at_sim_minute,
            assertion_kind, verification, source_key
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            recipient_id,
            subject_type,
            subject_id,
            topic,
            value_text,
            channel,
            source_actor_id,
            origin_event_type,
            origin_event_id,
            transfer_event_type,
            transfer_event_id,
            source_conversation_id,
            observed_at_sim_minute,
            int(received_at_sim_minute),
            assertion_kind,
            verification,
            source_key,
        ),
    )
    if cur.rowcount:
        return int(cur.lastrowid)

    row = conn.execute(
        "SELECT id FROM information_receipts WHERE source_key = ?",
        (source_key,),
    ).fetchone()
    return int(row["id"]) if row else None


def record_validated_information(
    *,
    recipient_id: str,
    subject_type: str,
    subject_id: str | None,
    topic: str,
    value_text: str,
    channel: str,
    origin_event_type: str,
    origin_event_id: int,
    observed_at_sim_minute: int,
    received_at_sim_minute: int | None = None,
    source_key: str | None = None,
) -> int | None:
    """
    Record a Simulation-grounded observation/measurement/result for one citizen.

    This is the stable handoff surface for future v0.6 Simulation discoveries.
    Simulation remains authoritative for the event and outcome.
    """
    ensure_information_schema()

    if channel not in {
        "direct_observation",
        "survey_measurement",
        "experiment_result",
        "personal_experience",
    }:
        return None

    received = (
        int(received_at_sim_minute)
        if received_at_sim_minute is not None
        else int(observed_at_sim_minute)
    )
    key = source_key or (
        f"validated:{origin_event_type}:{int(origin_event_id)}:"
        f"{recipient_id}:{subject_type}:{subject_id or ''}:{topic}:{value_text}"
    )

    with connect() as conn:
        receipt_id = _insert_receipt(
            conn,
            recipient_id=recipient_id,
            subject_type=subject_type,
            subject_id=subject_id,
            topic=topic,
            value_text=value_text,
            channel=channel,
            source_actor_id=None,
            origin_event_type=origin_event_type,
            origin_event_id=int(origin_event_id),
            transfer_event_type=None,
            transfer_event_id=None,
            source_conversation_id=None,
            observed_at_sim_minute=int(observed_at_sim_minute),
            received_at_sim_minute=received,
            assertion_kind="validated_observation",
            verification="verified",
            source_key=key,
        )
        conn.commit()
        return receipt_id


def record_face_to_face_claims(
    conversation_id: int,
    claims: list[dict[str, Any]] | None,
) -> list[int]:
    """
    Record only concrete assertions actually emitted in one stored conversation.

    Claims are received by the *other* participant and always start unverified.
    Retelling never promotes them to verified physical truth.
    """
    if not claims:
        return []

    ensure_information_schema()

    with connect() as conn:
        conversation = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id,
                   initiator_text, target_text
            FROM citizen_conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()
        if not conversation:
            return []

        role_to_speaker = {
            "initiator": str(conversation["initiator_id"]),
            "target": str(conversation["target_id"]),
        }
        role_to_recipient = {
            "initiator": str(conversation["target_id"]),
            "target": str(conversation["initiator_id"]),
        }
        role_to_text = {
            "initiator": " ".join(str(conversation["initiator_text"] or "").split()),
            "target": " ".join(str(conversation["target_text"] or "").split()),
        }

        inserted: list[int] = []
        for index, raw in enumerate(claims[:12]):
            if not isinstance(raw, dict):
                continue
            role = str(raw.get("speaker") or "").strip().lower()
            if role not in role_to_speaker:
                continue

            subject_type = str(raw.get("subject_type") or "other").strip()[:80] or "other"
            subject_id_raw = raw.get("subject_id")
            subject_id = str(subject_id_raw).strip()[:160] if subject_id_raw else None
            topic = str(raw.get("topic") or "").strip()[:160]
            value_text = " ".join(str(raw.get("value") or "").split())[:1200]
            if not topic or not value_text:
                continue

            # The model may classify/topic-tag a claim, but it cannot invent the
            # assertion itself. The stored value must be text the speaker
            # actually said in the durable exchange.
            if value_text.casefold() not in role_to_text[role].casefold():
                continue

            receipt_id = _insert_receipt(
                conn,
                recipient_id=role_to_recipient[role],
                subject_type=subject_type,
                subject_id=subject_id,
                topic=topic,
                value_text=value_text,
                channel="face_to_face_claim",
                source_actor_id=role_to_speaker[role],
                origin_event_type=None,
                origin_event_id=None,
                transfer_event_type="citizen_conversation",
                transfer_event_id=int(conversation["id"]),
                source_conversation_id=int(conversation["id"]),
                observed_at_sim_minute=None,
                received_at_sim_minute=int(conversation["sim_minute"]),
                assertion_kind="speaker_claim",
                verification="unverified",
                source_key=(
                    f"conversation:{int(conversation['id'])}:{role}:"
                    f"{subject_type}:{subject_id or ''}:{topic}:{value_text}"
                ),
            )
            if receipt_id is not None:
                inserted.append(receipt_id)

        conn.commit()
        return inserted


def _backfill_validated_v05_knowledge(conn) -> None:
    """
    Recover only facts whose physical source is unambiguous in old saves.

    We do not infer claim-level facts from legacy conversation summaries.
    """
    survey_jobs = conn.execute(
        """
        SELECT id, citizen_id, target, end_minute
        FROM jobs
        WHERE action = 'survey' AND status = 'complete'
        ORDER BY id
        """
    ).fetchall()

    for job in survey_jobs:
        _insert_receipt(
            conn,
            recipient_id=str(job["citizen_id"]),
            subject_type="location",
            subject_id=str(job["target"]),
            topic="survey_completed",
            value_text="A physical survey of this location was completed.",
            channel="survey_measurement",
            source_actor_id=None,
            origin_event_type="job",
            origin_event_id=int(job["id"]),
            transfer_event_type=None,
            transfer_event_id=None,
            source_conversation_id=None,
            observed_at_sim_minute=int(job["end_minute"]),
            received_at_sim_minute=int(job["end_minute"]),
            assertion_kind="validated_observation",
            verification="verified",
            source_key=f"legacy-survey:{int(job['id'])}:location",
        )

    deposits = conn.execute(
        """
        SELECT id, location_id, material, discoverer_id, discovered_minute
        FROM deposits
        WHERE discovered = 1
          AND discoverer_id IS NOT NULL
          AND discovered_minute IS NOT NULL
        ORDER BY id
        """
    ).fetchall()

    for deposit in deposits:
        source_job = conn.execute(
            """
            SELECT id
            FROM jobs
            WHERE citizen_id = ?
              AND action = 'survey'
              AND target = ?
              AND status = 'complete'
              AND end_minute <= ?
            ORDER BY end_minute DESC, id DESC
            LIMIT 1
            """,
            (
                deposit["discoverer_id"],
                deposit["location_id"],
                int(deposit["discovered_minute"]),
            ),
        ).fetchone()
        event_id = int(source_job["id"]) if source_job else None
        event_type = "job" if event_id is not None else "legacy_discovery"

        _insert_receipt(
            conn,
            recipient_id=str(deposit["discoverer_id"]),
            subject_type="location",
            subject_id=str(deposit["location_id"]),
            topic="confirmed_deposit",
            value_text=str(deposit["material"]),
            channel="survey_measurement",
            source_actor_id=None,
            origin_event_type=event_type,
            origin_event_id=event_id,
            transfer_event_type=None,
            transfer_event_id=None,
            source_conversation_id=None,
            observed_at_sim_minute=int(deposit["discovered_minute"]),
            received_at_sim_minute=int(deposit["discovered_minute"]),
            assertion_kind="validated_observation",
            verification="verified",
            source_key=(
                f"legacy-deposit:{deposit['id']}:"
                f"{deposit['discoverer_id']}"
            ),
        )



def _table_exists(conn, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return bool(row)


def _sync_v06_simulation_knowledge(conn) -> None:
    """
    Mirror only Simulation facts already granted to a specific citizen.

    This intentionally reads citizen_knowledge/discoveries, never hidden
    world_properties by themselves. It therefore cannot turn hidden truth into
    knowledge merely because the physical truth exists.
    """
    if not (
        _table_exists(conn, "citizen_knowledge")
        and _table_exists(conn, "discoveries")
    ):
        return

    has_world_properties = _table_exists(conn, "world_properties")
    has_deposits = _table_exists(conn, "deposits")

    property_join = (
        "LEFT JOIN world_properties wp ON wp.id = d.property_id"
        if has_world_properties
        else "LEFT JOIN (SELECT NULL AS id, NULL AS property_key, NULL AS value_text) wp ON 1 = 0"
    )
    deposit_join = (
        "LEFT JOIN deposits dep ON d.discovery_kind = 'deposit' AND dep.id = d.subject_id"
        if has_deposits
        else "LEFT JOIN (SELECT NULL AS id, NULL AS material) dep ON 1 = 0"
    )

    rows = conn.execute(
        f"""
        SELECT ck.citizen_id, ck.discovery_id, ck.learned_minute,
               ck.acquisition_kind, ck.source_type, ck.source_id,
               ck.verification_state,
               d.discovery_kind, d.subject_type, d.subject_id, d.property_id,
               d.location_id, d.source_job_id, d.discovered_minute, d.summary,
               wp.property_key, wp.value_text AS property_value_text,
               dep.material AS deposit_material
        FROM citizen_knowledge ck
        JOIN discoveries d ON d.id = ck.discovery_id
        {property_join}
        {deposit_join}
        WHERE ck.verification_state = 'verified'
        ORDER BY ck.learned_minute, ck.discovery_id
        """
    ).fetchall()

    channel_map = {
        "direct_survey": "survey_measurement",
        "direct_experiment": "experiment_result",
        "direct_observation": "direct_observation",
        "personal_experience": "personal_experience",
    }

    for row in rows:
        acquisition = str(row["acquisition_kind"] or "")
        channel = channel_map.get(acquisition, "personal_experience")

        if row["property_id"]:
            topic = str(row["property_key"] or row["property_id"])
            value_text = str(row["property_value_text"] or row["summary"] or "").strip()
        elif row["discovery_kind"] == "deposit":
            topic = "confirmed_deposit"
            value_text = str(row["deposit_material"] or row["summary"] or "").strip()
        else:
            topic = str(row["discovery_kind"] or "validated_discovery")
            value_text = str(row["summary"] or "").strip()

        if not value_text:
            continue

        _insert_receipt(
            conn,
            recipient_id=str(row["citizen_id"]),
            subject_type=str(row["subject_type"] or "other"),
            subject_id=str(row["subject_id"]) if row["subject_id"] is not None else None,
            topic=topic,
            value_text=value_text,
            channel=channel,
            source_actor_id=None,
            origin_event_type="simulation_discovery",
            origin_event_id=int(row["discovery_id"]),
            transfer_event_type=None,
            transfer_event_id=None,
            source_conversation_id=None,
            observed_at_sim_minute=int(row["discovered_minute"]),
            received_at_sim_minute=int(row["learned_minute"]),
            assertion_kind="validated_observation",
            verification="verified",
            source_key=f"simulation-knowledge:{row['citizen_id']}:{int(row['discovery_id'])}",
        )

    # An inconclusive/repeated experiment is still a real experience even when
    # it creates no new discovery. Preserve the attempt/result for the citizen
    # who performed it without fabricating a hidden property finding.
    if not _table_exists(conn, "experiment_results"):
        return

    results = conn.execute(
        """
        SELECT id, citizen_id, location_id, material, method, outcome,
               discovery_id, summary, completed_minute
        FROM experiment_results
        ORDER BY id
        """
    ).fetchall()

    for result in results:
        summary = str(result["summary"] or "").strip()
        if not summary:
            continue
        _insert_receipt(
            conn,
            recipient_id=str(result["citizen_id"]),
            subject_type="material",
            subject_id=str(result["material"]),
            topic=f"experiment_{result['outcome']}",
            value_text=summary,
            channel="experiment_result",
            source_actor_id=None,
            origin_event_type="simulation_experiment_result",
            origin_event_id=int(result["id"]),
            transfer_event_type=None,
            transfer_event_id=None,
            source_conversation_id=None,
            observed_at_sim_minute=int(result["completed_minute"]),
            received_at_sim_minute=int(result["completed_minute"]),
            assertion_kind="validated_observation",
            verification="verified",
            source_key=f"simulation-experiment-result:{int(result['id'])}",
        )


def information_receipts_for(
    citizen_id: str,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    ensure_information_schema()

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        rows = conn.execute(
            """
            SELECT ir.*, c.name AS source_actor_name,
                   l.name AS subject_location_name
            FROM information_receipts ir
            LEFT JOIN citizens c ON c.id = ir.source_actor_id
            LEFT JOIN locations l
              ON ir.subject_type = 'location'
             AND l.id = ir.subject_id
            WHERE ir.recipient_id = ?
            ORDER BY ir.received_at_sim_minute DESC, ir.id DESC
            LIMIT ?
            """,
            (citizen_id, max(1, min(int(limit), 200))),
        ).fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["age_minutes"] = max(0, now - int(item["received_at_sim_minute"]))
        item["received_label"] = format_sim_time(int(item["received_at_sim_minute"]))
        if item.get("observed_at_sim_minute") is not None:
            item["observed_label"] = format_sim_time(int(item["observed_at_sim_minute"]))
        else:
            item["observed_label"] = None
        result.append(item)
    return result


def knowledge_context_for(citizen_id: str, *, limit: int = 10) -> str:
    rows = information_receipts_for(citizen_id, limit=max(1, limit))
    if not rows:
        return "- no provenance-backed knowledge records yet"

    lines: list[str] = []
    for row in reversed(rows[-limit:]):
        subject = row.get("subject_location_name") or row.get("subject_id") or row["subject_type"]
        received = row["received_label"]

        if row["assertion_kind"] == "speaker_claim":
            source = row.get("source_actor_name") or row.get("source_actor_id") or "another citizen"
            lines.append(
                f"- Heard from {source} at {received} (unverified claim): "
                f"{subject} / {row['topic']} = {row['value_text']}"
            )
        else:
            lines.append(
                f"- Verified {row['channel']} at {received}: "
                f"{subject} / {row['topic']} = {row['value_text']}"
            )

    return "\n".join(lines)


def knowledge_payload(citizen_id: str, *, limit: int = 100) -> dict[str, Any]:
    with connect() as conn:
        citizen = conn.execute(
            "SELECT id, name, location_id, location FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
        now = int(get_meta(conn, "sim_minute") or "360")

    if not citizen:
        return {
            "citizen_id": citizen_id,
            "exists": False,
            "sim_minute": now,
            "records": [],
            "locations": {},
        }

    records = information_receipts_for(citizen_id, limit=limit)
    locations: dict[str, dict[str, Any]] = {}

    # Current physical location is directly observable now. It is deliberately
    # derived, not archived as a fake historical event.
    current_location_id = str(citizen["location_id"])
    locations[current_location_id] = {
        "location_id": current_location_id,
        "location_name": str(citizen["location"]),
        "current_direct_observation": True,
        "facts": [],
    }

    for record in records:
        if record["subject_type"] != "location" or not record.get("subject_id"):
            continue
        lid = str(record["subject_id"])
        entry = locations.setdefault(
            lid,
            {
                "location_id": lid,
                "location_name": record.get("subject_location_name") or lid,
                "current_direct_observation": lid == current_location_id,
                "facts": [],
            },
        )
        entry["facts"].append(record)

    return {
        "citizen_id": str(citizen["id"]),
        "citizen_name": str(citizen["name"]),
        "exists": True,
        "sim_minute": now,
        "sim_label": format_sim_time(now),
        "records": records,
        "locations": locations,
    }
