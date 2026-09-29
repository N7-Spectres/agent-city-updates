from __future__ import annotations

import json
from typing import Any

from .db import connect
from .world import format_sim_time

MAX_RELATIONSHIPS_IN_CONTEXT = 4
MEMORIES_PER_RELATIONSHIP = 2
MAX_CONTEXT_CHARS = 1800
MAX_KNOWLEDGE_CONTEXT_CHARS = 1600
MAX_KNOWLEDGE_FACTS = 12
MAX_MAINTENANCE_CONTEXT_CHARS = 1200
MAX_MAINTENANCE_FACTS = 10


def ensure_memory_schema() -> None:
    """Create durable social-memory storage and backfill existing citizen conversations."""
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                sim_minute INTEGER NOT NULL,
                event_kind TEXT NOT NULL,
                counterparty_id TEXT,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                source_role TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 0.5,
                status TEXT NOT NULL DEFAULT 'remembered',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                UNIQUE(owner_id, source_type, source_id, event_kind, source_role)
            );

            CREATE INDEX IF NOT EXISTS idx_memory_events_owner_time
            ON memory_events(owner_id, sim_minute DESC, id DESC);

            CREATE INDEX IF NOT EXISTS idx_memory_events_relationship
            ON memory_events(owner_id, counterparty_id, sim_minute DESC, id DESC);

            CREATE TABLE IF NOT EXISTS relationship_state (
                owner_id TEXT NOT NULL,
                other_id TEXT NOT NULL,
                first_interaction_minute INTEGER NOT NULL,
                last_interaction_minute INTEGER NOT NULL,
                conversation_count INTEGER NOT NULL DEFAULT 0,
                cooperation_count INTEGER NOT NULL DEFAULT 0,
                disagreement_count INTEGER NOT NULL DEFAULT 0,
                help_given_count INTEGER NOT NULL DEFAULT 0,
                help_received_count INTEGER NOT NULL DEFAULT 0,
                promise_made_count INTEGER NOT NULL DEFAULT 0,
                promise_received_count INTEGER NOT NULL DEFAULT 0,
                promise_fulfilled_count INTEGER NOT NULL DEFAULT 0,
                promise_broken_count INTEGER NOT NULL DEFAULT 0,
                verified_claim_count INTEGER NOT NULL DEFAULT 0,
                contradicted_claim_count INTEGER NOT NULL DEFAULT 0,
                summary TEXT NOT NULL DEFAULT '',
                last_event_id INTEGER,
                PRIMARY KEY(owner_id, other_id)
            );
            """
        )

        rows = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id, summary
            FROM citizen_conversations
            ORDER BY id
            """
        ).fetchall()
        for row in rows:
            _remember_conversation_row(conn, row)

        _backfill_personal_discoveries(conn)
        _sync_maintenance_events(conn)
        from .spatial_memory import sync_spatial_observations_in_conn
        from .exploration_memory import sync_shared_exploration_in_conn
        from .causal_memory import ensure_causal_memory_schema_in_conn
        from .practice_memory import sync_practice_memory_in_conn
        from .guided_practice_memory import sync_guided_practice_memory_in_conn
        sync_spatial_observations_in_conn(conn)
        sync_shared_exploration_in_conn(conn)
        ensure_causal_memory_schema_in_conn(conn)
        sync_practice_memory_in_conn(conn)
        sync_guided_practice_memory_in_conn(conn)
        ensure_causal_memory_schema_in_conn(conn)
        conn.commit()


def _upsert_relationship_for_conversation(
    conn,
    owner_id: str,
    other_id: str,
    sim_minute: int,
    memory_event_id: int,
) -> None:
    conn.execute(
        """
        INSERT INTO relationship_state(
            owner_id, other_id,
            first_interaction_minute, last_interaction_minute,
            conversation_count, last_event_id
        )
        VALUES (?, ?, ?, ?, 1, ?)
        ON CONFLICT(owner_id, other_id) DO UPDATE SET
            first_interaction_minute = MIN(
                relationship_state.first_interaction_minute,
                excluded.first_interaction_minute
            ),
            last_interaction_minute = MAX(
                relationship_state.last_interaction_minute,
                excluded.last_interaction_minute
            ),
            conversation_count = relationship_state.conversation_count + 1,
            last_event_id = excluded.last_event_id
        """,
        (owner_id, other_id, sim_minute, sim_minute, memory_event_id),
    )


def _insert_conversation_memory(
    conn,
    *,
    owner_id: str,
    other_id: str,
    source_id: int,
    source_role: str,
    sim_minute: int,
    summary: str,
) -> None:
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status
        )
        VALUES (?, ?, 'conversation', ?, 'citizen_conversation', ?, ?, ?, 0.45, 'remembered')
        """,
        (
            owner_id,
            sim_minute,
            other_id,
            source_id,
            source_role,
            summary[:1200],
        ),
    )
    if cur.rowcount:
        _upsert_relationship_for_conversation(
            conn,
            owner_id,
            other_id,
            sim_minute,
            int(cur.lastrowid),
        )


def _remember_conversation_row(conn, row) -> None:
    source_id = int(row["id"])
    sim_minute = int(row["sim_minute"])
    initiator_id = str(row["initiator_id"])
    target_id = str(row["target_id"])
    summary = str(row["summary"] or "").strip()
    if not summary:
        summary = "A face-to-face conversation occurred; no detailed summary was retained."

    _insert_conversation_memory(
        conn,
        owner_id=initiator_id,
        other_id=target_id,
        source_id=source_id,
        source_role="initiator",
        sim_minute=sim_minute,
        summary=summary,
    )
    _insert_conversation_memory(
        conn,
        owner_id=target_id,
        other_id=initiator_id,
        source_id=source_id,
        source_role="target",
        sim_minute=sim_minute,
        summary=summary,
    )


def record_conversation_memory(conversation_id: int) -> None:
    """Remember one validated stored conversation for both participants, once."""
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id, sim_minute, initiator_id, target_id, summary
            FROM citizen_conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()
        if not row:
            return
        _remember_conversation_row(conn, row)
        conn.commit()


def _relationship_rows(citizen_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT rs.*, c.name AS other_name
            FROM relationship_state rs
            JOIN citizens c ON c.id = rs.other_id
            WHERE rs.owner_id = ?
            ORDER BY rs.last_interaction_minute DESC, c.rowid
            """,
            (citizen_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def _recent_memories(owner_id: str, other_id: str, limit: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, sim_minute, event_kind, summary, source_type, source_id, status
            FROM memory_events
            WHERE owner_id = ? AND counterparty_id = ?
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (owner_id, other_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def social_context_for(
    citizen_id: str,
    *,
    preferred_counterparties: list[str] | None = None,
    limit: int = MAX_RELATIONSHIPS_IN_CONTEXT,
) -> str:
    """
    Build bounded, explainable social context.

    The text describes recorded interaction history. It never promotes remembered
    conversation content into authoritative physical truth.
    """
    rows = _relationship_rows(citizen_id)
    if not rows:
        return "- no durable relationship history yet"

    preferred = preferred_counterparties or []
    preferred_rank = {cid: i for i, cid in enumerate(preferred)}
    rows.sort(
        key=lambda r: (
            0 if r["other_id"] in preferred_rank else 1,
            preferred_rank.get(r["other_id"], 999),
            -int(r["last_interaction_minute"]),
        )
    )

    parts: list[str] = []
    for row in rows[: max(1, limit)]:
        count = int(row["conversation_count"])
        first_label = format_sim_time(int(row["first_interaction_minute"]))
        last_label = format_sim_time(int(row["last_interaction_minute"]))
        memories = _recent_memories(
            citizen_id,
            str(row["other_id"]),
            MEMORIES_PER_RELATIONSHIP,
        )
        memory_text = " | ".join(
            " ".join(str(m["summary"]).split())[:280]
            for m in reversed(memories)
        ) or "no detailed memory retained"

        parts.append(
            f"- {row['other_name']}: {count} recorded face-to-face conversation"
            f"{'s' if count != 1 else ''}; first {first_label}; last {last_label}. "
            f"Remembered conversation content (claims, not automatic physical facts): {memory_text}"
        )

        if sum(len(p) + 1 for p in parts) >= MAX_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_CONTEXT_CHARS]


def relationship_snapshot(citizen_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Read-only relationship history for future UI/API use; contains no social score."""
    rows = _relationship_rows(citizen_id)[: max(1, limit)]
    result: list[dict[str, Any]] = []

    for row in rows:
        recent = _recent_memories(citizen_id, str(row["other_id"]), 3)
        item = dict(row)
        item["first_interaction_label"] = format_sim_time(int(row["first_interaction_minute"]))
        item["last_interaction_label"] = format_sim_time(int(row["last_interaction_minute"]))
        item["recent_memories"] = recent
        result.append(item)

    return result



def record_knowledge_event(
    owner_id: str,
    *,
    sim_minute: int,
    event_kind: str,
    source_type: str,
    source_id: int,
    summary: str,
    metadata: dict[str, Any] | None = None,
    source_role: str = "knower",
    status: str = "verified",
    importance: float = 0.6,
) -> int | None:
    """
    Store one source-linked knowledge event for one citizen.

    This does not create physical truth. Callers must only use status='verified'
    when the supplied source is authoritative for the fact. Communicated claims
    should remain status='remembered' or 'unverified' in metadata until verified.
    """
    clean_summary = " ".join(str(summary or "").split()).strip()
    if not clean_summary:
        return None

    meta = dict(metadata or {})
    meta.setdefault("verification", "verified" if status == "verified" else "unverified")
    payload = json.dumps(meta, sort_keys=True, separators=(",", ":"))

    with connect() as conn:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO memory_events(
                owner_id, sim_minute, event_kind, counterparty_id,
                source_type, source_id, source_role,
                summary, importance, status, metadata_json
            )
            VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                owner_id,
                int(sim_minute),
                event_kind[:80],
                source_type[:80],
                int(source_id),
                source_role[:80],
                clean_summary[:1200],
                max(0.0, min(float(importance), 1.0)),
                status[:40],
                payload,
            ),
        )
        conn.commit()
        return int(cur.lastrowid) if cur.rowcount else None


def _backfill_personal_discoveries(conn) -> None:
    """
    Project existing authoritative deposit discoveries into per-citizen memory.

    The source is the completed survey job when one can be matched. Older saves
    without a matching job use the authoritative deposit rowid as a legacy source
    without inventing a more specific event.
    """
    rows = conn.execute(
        """
        SELECT d.rowid AS deposit_rowid,
               d.id AS deposit_id,
               d.location_id,
               d.material,
               d.discoverer_id,
               d.discovered_minute,
               l.name AS location_name
        FROM deposits d
        JOIN locations l ON l.id = d.location_id
        WHERE d.discovered = 1
          AND d.discoverer_id IS NOT NULL
          AND d.discovered_minute IS NOT NULL
        ORDER BY d.discovered_minute, d.rowid
        """
    ).fetchall()

    for row in rows:
        job = conn.execute(
            """
            SELECT id, end_minute
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
                row["discoverer_id"],
                row["location_id"],
                int(row["discovered_minute"]),
            ),
        ).fetchone()

        source_type = "job" if job else "legacy_deposit"
        source_id = int(job["id"]) if job else int(row["deposit_rowid"])
        metadata = {
            "verification": "verified",
            "channel": "personal_experience",
            "subject_type": "deposit",
            "subject_id": str(row["deposit_id"]),
            "location_id": str(row["location_id"]),
            "material": str(row["material"]),
            "discovery_kind": "survey_confirmation",
        }
        summary = (
            f"Personally confirmed {row['material']} at {row['location_name']}."
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO memory_events(
                owner_id, sim_minute, event_kind, counterparty_id,
                source_type, source_id, source_role,
                summary, importance, status, metadata_json
            )
            VALUES (?, ?, 'location_discovery', NULL, ?, ?, 'observer', ?, 0.72, 'verified', ?)
            """,
            (
                row["discoverer_id"],
                int(row["discovered_minute"]),
                source_type,
                source_id,
                summary,
                json.dumps(metadata, sort_keys=True, separators=(",", ":")),
            ),
        )


def backfill_personal_discoveries() -> None:
    """Public idempotent hook for newly imported/migrated authoritative discoveries."""
    with connect() as conn:
        _backfill_personal_discoveries(conn)
        conn.commit()


def _knowledge_memory_rows(citizen_id: str, scan_limit: int = 120) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, sim_minute, event_kind, source_type, source_id,
                   source_role, summary, importance, status, metadata_json
            FROM memory_events
            WHERE owner_id = ?
              AND event_kind != 'conversation'
              AND source_type NOT IN (
                  'simulation_maintenance_event',
                  'simulation_spatial_observation',
                  'simulation_shared_activity'
              )
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (citizen_id, max(1, scan_limit)),
        ).fetchall()
        return [dict(r) for r in rows]


def knowledge_snapshot_for(
    citizen_id: str,
    *,
    location_id: str | None = None,
    material: str | None = None,
    process: str | None = None,
    limit: int = MAX_KNOWLEDGE_FACTS,
) -> list[dict[str, Any]]:
    """
    Return bounded per-citizen knowledge only.

    Filters are matched against structured metadata. Hidden Simulation truth is
    never queried to fill gaps, so an empty result legitimately means unknown.
    """
    # Synchronize any newly validated personal survey discoveries first.
    # This is idempotent and never imports hidden undiscovered truth.
    backfill_personal_discoveries()

    result: list[dict[str, Any]] = []
    material_key = material.casefold().strip() if material else None
    process_key = process.casefold().strip() if process else None

    for row in _knowledge_memory_rows(citizen_id):
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        if location_id and str(metadata.get("location_id") or "") != location_id:
            continue
        if material_key and str(metadata.get("material") or "").casefold() != material_key:
            continue
        if process_key and str(metadata.get("process") or "").casefold() != process_key:
            continue

        item = dict(row)
        item["metadata"] = metadata
        item["verification"] = str(
            metadata.get("verification")
            or ("verified" if row.get("status") == "verified" else "unverified")
        )
        item.pop("metadata_json", None)
        item["sim_label"] = format_sim_time(int(row["sim_minute"]))
        result.append(item)
        if len(result) >= max(1, limit):
            break

    return result


def knowledge_context_for(
    citizen_id: str,
    *,
    location_id: str | None = None,
    material: str | None = None,
    process: str | None = None,
    limit: int = 8,
) -> str:
    """Compact context that keeps verified knowledge distinct from claims."""
    facts = knowledge_snapshot_for(
        citizen_id,
        location_id=location_id,
        material=material,
        process=process,
        limit=limit,
    )
    if not facts:
        return "- no retained knowledge matching this subject"

    parts: list[str] = []
    for fact in reversed(facts):
        verification = fact["verification"]
        prefix = "Verified" if verification == "verified" else "Unverified"
        source = f"{fact['source_type']} #{fact['source_id']}"
        parts.append(
            f"- {prefix}, {fact['sim_label']} ({source}): "
            f"{' '.join(str(fact['summary']).split())[:360]}"
        )
        if sum(len(p) + 1 for p in parts) >= MAX_KNOWLEDGE_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_KNOWLEDGE_CONTEXT_CHARS]


def location_knowledge_snapshot(
    location_id: str,
    *,
    citizen_id: str | None = None,
    per_citizen_limit: int = 10,
) -> dict[str, Any]:
    """
    UI-safe location notebook model.

    With no citizen selected, knowledge stays partitioned by citizen. Facts are
    never unioned into a civilization-wide omniscient location record.
    """
    with connect() as conn:
        location = conn.execute(
            "SELECT id, name FROM locations WHERE id = ?",
            (location_id,),
        ).fetchone()
        if not location:
            return {"location": None, "citizens": []}

        if citizen_id:
            citizens = conn.execute(
                "SELECT id, name FROM citizens WHERE id = ? ORDER BY rowid",
                (citizen_id,),
            ).fetchall()
        else:
            citizens = conn.execute(
                "SELECT id, name FROM citizens ORDER BY rowid"
            ).fetchall()

    citizen_views: list[dict[str, Any]] = []
    for citizen in citizens:
        facts = knowledge_snapshot_for(
            str(citizen["id"]),
            location_id=location_id,
            limit=per_citizen_limit,
        )
        citizen_views.append(
            {
                "citizen_id": str(citizen["id"]),
                "citizen_name": str(citizen["name"]),
                "facts": facts,
                "summary": knowledge_context_for(
                    str(citizen["id"]),
                    location_id=location_id,
                    limit=min(per_citizen_limit, 6),
                ),
            }
        )

    return {
        "location": {"id": str(location["id"]), "name": str(location["name"])},
        "citizens": citizen_views,
    }



def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _maintenance_importance(event_type: str) -> float:
    if event_type == "battery_replacement":
        return 0.82
    if event_type in {"equipment_service", "structure_service"}:
        return 0.70
    if event_type == "chassis_service":
        return 0.66
    return 0.62


def _insert_maintenance_memory(
    conn,
    *,
    owner_id: str,
    source_role: str,
    event,
) -> None:
    event_type = str(event["event_type"] or "maintenance")
    summary = " ".join(str(event["summary"] or "").split()).strip()
    if not summary:
        return

    try:
        materials = json.loads(str(event["materials_json"] or "{}"))
        if not isinstance(materials, dict):
            materials = {}
    except (TypeError, ValueError, json.JSONDecodeError):
        materials = {}

    metadata = {
        "verification": "verified",
        "channel": "personal_experience",
        "experience_role": source_role,
        "job_id": int(event["job_id"]),
        "event_type": event_type,
        "target_type": str(event["target_type"]),
        "target_id": str(event["target_id"]),
        "before_value": event["before_value"],
        "after_value": event["after_value"],
        "materials": materials,
        "outcome": str(event["outcome"]),
    }

    conn.execute(
        """
        INSERT OR IGNORE INTO memory_events(
            owner_id, sim_minute, event_kind, counterparty_id,
            source_type, source_id, source_role,
            summary, importance, status, metadata_json
        )
        VALUES (?, ?, ?, NULL, 'simulation_maintenance_event', ?, ?, ?, ?, 'verified', ?)
        """,
        (
            owner_id,
            int(event["sim_minute"]),
            f"maintenance_{event_type}"[:80],
            int(event["id"]),
            source_role[:80],
            summary[:1200],
            _maintenance_importance(event_type),
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ),
    )


def _sync_maintenance_events(conn) -> None:
    """
    Import explicit validated maintenance events into citizen memory.

    This deliberately ignores condition deltas, passive wear, and History text.
    If the Simulation maintenance table is not present yet, this is a safe no-op.
    """
    if not _table_exists(conn, "maintenance_events"):
        return

    rows = conn.execute(
        """
        SELECT id, job_id, citizen_id, event_type, target_type, target_id,
               before_value, after_value, materials_json, outcome,
               sim_minute, summary
        FROM maintenance_events
        ORDER BY id
        """
    ).fetchall()

    for event in rows:
        actor_id = str(event["citizen_id"])
        actor_exists = conn.execute(
            "SELECT 1 FROM citizens WHERE id = ?",
            (actor_id,),
        ).fetchone()
        if actor_exists:
            _insert_maintenance_memory(
                conn,
                owner_id=actor_id,
                source_role="actor",
                event=event,
            )

        # If one citizen physically services another citizen, the serviced
        # citizen directly experiences the event too. Do not auto-grant
        # equipment owners, bystanders, or the whole settlement.
        if str(event["target_type"]) == "citizen":
            target_id = str(event["target_id"])
            if target_id != actor_id:
                target_exists = conn.execute(
                    "SELECT 1 FROM citizens WHERE id = ?",
                    (target_id,),
                ).fetchone()
                if target_exists:
                    _insert_maintenance_memory(
                        conn,
                        owner_id=target_id,
                        source_role="serviced_subject",
                        event=event,
                    )


def sync_maintenance_events() -> None:
    """Public idempotent synchronization hook for validated Simulation maintenance events."""
    with connect() as conn:
        _sync_maintenance_events(conn)
        conn.commit()


def _maintenance_memory_rows(citizen_id: str, scan_limit: int = 160) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, sim_minute, event_kind, source_type, source_id,
                   source_role, summary, importance, status, metadata_json
            FROM memory_events
            WHERE owner_id = ?
              AND source_type = 'simulation_maintenance_event'
            ORDER BY sim_minute DESC, id DESC
            LIMIT ?
            """,
            (citizen_id, max(1, scan_limit)),
        ).fetchall()
        return [dict(r) for r in rows]


def maintenance_snapshot_for(
    citizen_id: str,
    *,
    target_type: str | None = None,
    target_id: str | None = None,
    limit: int = MAX_MAINTENANCE_FACTS,
) -> list[dict[str, Any]]:
    """
    Return bounded maintenance experiences for one citizen.

    This is an experience/history view, not a global physical-maintenance ledger.
    """
    sync_maintenance_events()

    result: list[dict[str, Any]] = []
    for row in _maintenance_memory_rows(citizen_id):
        try:
            metadata = json.loads(str(row.get("metadata_json") or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            metadata = {}

        if target_type and str(metadata.get("target_type") or "") != target_type:
            continue
        if target_id is not None and str(metadata.get("target_id") or "") != str(target_id):
            continue

        item = dict(row)
        item["metadata"] = metadata
        item.pop("metadata_json", None)
        item["sim_label"] = format_sim_time(int(row["sim_minute"]))
        result.append(item)
        if len(result) >= max(1, limit):
            break

    return result


def maintenance_context_for(
    citizen_id: str,
    *,
    target_type: str | None = None,
    target_id: str | None = None,
    limit: int = 4,
) -> str:
    """Compact maintenance continuity for subject-relevant planning/conversation."""
    events = maintenance_snapshot_for(
        citizen_id,
        target_type=target_type,
        target_id=target_id,
        limit=limit,
    )
    if not events:
        return "- no retained meaningful maintenance history matching this subject"

    parts: list[str] = []
    for event in reversed(events):
        meta = event["metadata"]
        target = f"{meta.get('target_type', 'target')} #{meta.get('target_id', '?')}"
        before = meta.get("before_value")
        after = meta.get("after_value")
        change = ""
        if before is not None or after is not None:
            change = f" ({before if before is not None else '?'} -> {after if after is not None else '?'})"
        parts.append(
            f"- {event['sim_label']}: {event['summary']} [{target}{change}; "
            f"source maintenance event #{event['source_id']}]"
        )
        if sum(len(p) + 1 for p in parts) >= MAX_MAINTENANCE_CONTEXT_CHARS:
            break

    return "\n".join(parts)[:MAX_MAINTENANCE_CONTEXT_CHARS]
