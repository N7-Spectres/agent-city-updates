from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        from agent_city.memory import (
            ensure_memory_schema,
            knowledge_snapshot_for,
            maintenance_context_for,
            maintenance_snapshot_for,
            sync_maintenance_events,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # v0.6 compatibility: if Simulation's v0.7 table is not merged yet,
        # maintenance retrieval is a safe empty view rather than a crash.
        assert maintenance_snapshot_for("bex") == []

        with connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS maintenance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL UNIQUE,
                    citizen_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    before_value REAL,
                    after_value REAL,
                    materials_json TEXT,
                    outcome TEXT NOT NULL,
                    sim_minute INTEGER NOT NULL,
                    summary TEXT NOT NULL
                );
                """
            )

            # Simulate passive wear by changing physical state only. No explicit
            # maintenance event exists, so Memory must not synthesize a memory.
            conn.execute(
                "UPDATE equipment SET condition = 82 WHERE id = (SELECT MIN(id) FROM equipment)"
            )
            conn.commit()

        assert maintenance_snapshot_for("bex") == []

        with connect() as conn:
            # Bex services equipment. Only Bex directly owns this experience.
            conn.execute(
                """
                INSERT INTO maintenance_events(
                    job_id, citizen_id, event_type, target_type, target_id,
                    before_value, after_value, materials_json, outcome,
                    sim_minute, summary
                )
                VALUES (
                    7001, 'bex', 'equipment_service', 'equipment', '12',
                    58, 100, '{"Fasteners":1,"Lubricant":1}', 'success',
                    1200, 'Bex restored the extraction tool to full service condition.'
                )
                """
            )
            equipment_event_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )

            # Iri physically services Cato's chassis. Both actor and serviced
            # citizen directly experience this event.
            conn.execute(
                """
                INSERT INTO maintenance_events(
                    job_id, citizen_id, event_type, target_type, target_id,
                    before_value, after_value, materials_json, outcome,
                    sim_minute, summary
                )
                VALUES (
                    7002, 'iri', 'chassis_service', 'citizen', 'cato',
                    16, 0, '{"Lubricant":1}', 'success',
                    1260, 'Iri completed chassis joint service for Cato.'
                )
                """
            )
            citizen_event_id = int(
                conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            )
            conn.commit()

        sync_maintenance_events()

        bex = maintenance_snapshot_for("bex")
        assert len(bex) == 1
        assert bex[0]["source_type"] == "simulation_maintenance_event"
        assert int(bex[0]["source_id"]) == equipment_event_id
        assert bex[0]["metadata"]["job_id"] == 7001
        assert bex[0]["metadata"]["target_type"] == "equipment"
        assert bex[0]["metadata"]["target_id"] == "12"
        assert bex[0]["metadata"]["before_value"] == 58
        assert bex[0]["metadata"]["after_value"] == 100
        assert bex[0]["metadata"]["materials"]["Lubricant"] == 1
        assert bex[0]["metadata"]["outcome"] == "success"

        iri = maintenance_snapshot_for("iri")
        cato = maintenance_snapshot_for("cato")
        assert len(iri) == 1
        assert len(cato) == 1
        assert int(iri[0]["source_id"]) == citizen_event_id
        assert int(cato[0]["source_id"]) == citizen_event_id
        assert iri[0]["source_role"] == "actor"
        assert cato[0]["source_role"] == "serviced_subject"

        # Bystanders and the whole settlement do not automatically receive it.
        assert maintenance_snapshot_for("aris") == []
        assert maintenance_snapshot_for("vale") == []

        # Repeated sync/retrieval must remain idempotent.
        sync_maintenance_events()
        sync_maintenance_events()
        assert len(maintenance_snapshot_for("bex")) == 1
        assert len(maintenance_snapshot_for("iri")) == 1
        assert len(maintenance_snapshot_for("cato")) == 1

        # Subject filtering is bounded and specific.
        filtered = maintenance_snapshot_for(
            "bex",
            target_type="equipment",
            target_id="12",
        )
        assert len(filtered) == 1
        assert maintenance_snapshot_for(
            "bex",
            target_type="structure",
        ) == []

        context = maintenance_context_for("bex", limit=3)
        assert "maintenance event" in context
        assert "restored the extraction tool" in context

        # v0.6 knowledge facts stay separate from maintenance history.
        knowledge = knowledge_snapshot_for("bex")
        assert all(
            fact["source_type"] != "simulation_maintenance_event"
            for fact in knowledge
        )

        # API surface remains citizen-scoped and bounded.
        import main as app_module

        payload = app_module.get_maintenance_memory(
            "bex",
            target_type="equipment",
            target_id="12",
            limit=10,
        )
        assert payload["citizen"]["id"] == "bex"
        assert len(payload["events"]) == 1
        assert payload["events"][0]["source_id"] == equipment_event_id

        print("Agent City v0.7 Memory maintenance smoke test passed.")


if __name__ == "__main__":
    main()
