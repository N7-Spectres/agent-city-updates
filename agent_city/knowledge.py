from __future__ import annotations

from typing import Any

from .db import connect


def grant_citizen_knowledge(
    conn,
    citizen_id: str,
    discovery_id: int,
    learned_minute: int,
    acquisition_kind: str,
    source_type: str,
    source_id: str | int,
    verification_state: str = "verified",
) -> None:
    """
    Record that a specific citizen has access to a validated discovery.

    Communication may later use this interface after a real information-transfer
    event. Merely creating a discovery does not grant it to everybody.
    """
    conn.execute(
        """
        INSERT INTO citizen_knowledge
        (citizen_id, discovery_id, learned_minute, acquisition_kind,
         source_type, source_id, verification_state)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(citizen_id, discovery_id) DO UPDATE SET
            learned_minute = MIN(citizen_knowledge.learned_minute, excluded.learned_minute),
            verification_state = CASE
                WHEN citizen_knowledge.verification_state = 'verified' THEN 'verified'
                ELSE excluded.verification_state
            END
        """,
        (
            citizen_id,
            int(discovery_id),
            int(learned_minute),
            acquisition_kind,
            source_type,
            str(source_id),
            verification_state,
        ),
    )


def record_discovery(
    conn,
    *,
    discovery_kind: str,
    subject_type: str,
    subject_id: str,
    citizen_id: str,
    location_id: str,
    source_job_id: int | None,
    discovered_minute: int,
    summary: str,
    property_id: str | None = None,
    acquisition_kind: str = "direct_observation",
) -> int:
    cur = conn.execute(
        """
        INSERT INTO discoveries
        (discovery_kind, subject_type, subject_id, property_id, citizen_id,
         location_id, source_job_id, discovered_minute, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            discovery_kind,
            subject_type,
            subject_id,
            property_id,
            citizen_id,
            location_id,
            source_job_id,
            int(discovered_minute),
            summary[:1200],
        ),
    )
    discovery_id = int(cur.lastrowid)
    grant_citizen_knowledge(
        conn,
        citizen_id,
        discovery_id,
        discovered_minute,
        acquisition_kind,
        "discovery",
        discovery_id,
        "verified",
    )
    return discovery_id


def citizen_knows_property(conn, citizen_id: str, property_id: str) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM citizen_knowledge ck
        JOIN discoveries d ON d.id = ck.discovery_id
        WHERE ck.citizen_id = ?
          AND d.property_id = ?
        LIMIT 1
        """,
        (citizen_id, property_id),
    ).fetchone()
    return bool(row)


def citizen_knows_deposit(conn, citizen_id: str, deposit_id: str) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM citizen_knowledge ck
        JOIN discoveries d ON d.id = ck.discovery_id
        WHERE ck.citizen_id = ?
          AND d.discovery_kind = 'deposit'
          AND d.subject_id = ?
        LIMIT 1
        """,
        (citizen_id, deposit_id),
    ).fetchone()
    return bool(row)


def known_properties_for(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT ck.learned_minute, ck.acquisition_kind, ck.source_type, ck.source_id,
                   ck.verification_state,
                   d.id AS discovery_id, d.subject_type, d.subject_id, d.location_id,
                   d.discovered_minute, d.summary,
                   wp.id AS property_id, wp.property_key, wp.value_text, wp.unit
            FROM citizen_knowledge ck
            JOIN discoveries d ON d.id = ck.discovery_id
            JOIN world_properties wp ON wp.id = d.property_id
            WHERE ck.citizen_id = ?
            ORDER BY ck.learned_minute, d.id
            """,
            (citizen_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def known_deposits_for_citizen(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT ck.learned_minute, ck.acquisition_kind, ck.source_type, ck.source_id,
                   ck.verification_state,
                   d.id AS discovery_id, d.location_id, d.discovered_minute, d.summary,
                   dep.id AS deposit_id, dep.material,
                   l.name AS location_name
            FROM citizen_knowledge ck
            JOIN discoveries d ON d.id = ck.discovery_id
            JOIN deposits dep
              ON d.discovery_kind = 'deposit' AND dep.id = d.subject_id
            JOIN locations l ON l.id = d.location_id
            WHERE ck.citizen_id = ?
            ORDER BY ck.learned_minute, d.id
            """,
            (citizen_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def knowledge_payload_for(citizen_id: str) -> dict[str, Any]:
    """
    Citizen-specific safe read model. It contains only facts that have actually
    reached this citizen through a recorded knowledge row.
    """
    with connect() as conn:
        citizen = conn.execute(
            "SELECT id, name, location_id FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
        if not citizen:
            return {"citizen_id": citizen_id, "discoveries": [], "properties": [], "deposits": []}

        rows = conn.execute(
            """
            SELECT ck.*,
                   d.discovery_kind, d.subject_type, d.subject_id, d.property_id,
                   d.location_id, d.discovered_minute, d.summary,
                   wp.property_key, wp.value_text, wp.unit,
                   dep.material AS deposit_material
            FROM citizen_knowledge ck
            JOIN discoveries d ON d.id = ck.discovery_id
            LEFT JOIN world_properties wp ON wp.id = d.property_id
            LEFT JOIN deposits dep
              ON d.discovery_kind = 'deposit' AND dep.id = d.subject_id
            WHERE ck.citizen_id = ?
            ORDER BY ck.learned_minute, ck.discovery_id
            """,
            (citizen_id,),
        ).fetchall()

    discoveries = [dict(row) for row in rows]
    return {
        "citizen_id": citizen_id,
        "citizen_name": citizen["name"],
        "discoveries": discoveries,
        "properties": [d for d in discoveries if d.get("property_id")],
        "deposits": [d for d in discoveries if d.get("discovery_kind") == "deposit"],
    }
